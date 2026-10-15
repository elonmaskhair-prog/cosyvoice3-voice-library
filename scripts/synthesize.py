"""Generate narration from the published CosyVoice 3 voice profile."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "model.lock.json").read_text(encoding="utf-8"))
DEFAULT_PROFILE = ROOT / "voices" / "my-voice-v1"

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
for key in ("NO_PROXY", "no_proxy"):
    os.environ[key] = ",".join(filter(None, [os.environ.get(key, ""), "localhost,127.0.0.1,::1"]))


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_text(path):
    text = Path(path).read_text(encoding="utf-8-sig").strip()
    if not text:
        raise ValueError(f"Empty text file: {path}")
    return text


def resolve_profile(profile=DEFAULT_PROFILE, language="zh", reference_id=None):
    profile = Path(profile).resolve()
    if profile.is_dir():
        profile = profile / "profile.json"
    manifest = json.loads(profile.read_text(encoding="utf-8-sig"))
    language_name = {"zh": "Chinese", "en": "English"}[language]
    reference_id = reference_id or manifest["default_references"][language_name]
    reference = next((item for item in manifest["references"] if item["id"] == reference_id), None)
    if reference is None:
        raise ValueError(f"Unknown reference ID: {reference_id}")
    artifact = manifest["engine_artifacts"]["cosy"][reference_id]
    for key in ("model_id", "revision"):
        if artifact["model"][key] != LOCK[key]:
            raise ValueError(f"Profile and configured base model disagree on {key}.")
    audio = profile.parent / reference["audio"]
    voice_file = profile.parent / artifact["file"]
    if sha256(audio) != reference["sha256"] or sha256(voice_file) != artifact["sha256"]:
        raise ValueError("Voice asset checksum mismatch; restore the original file or create a new profile version.")
    transcript = read_text(profile.parent / reference["transcript"])
    if transcript != reference["text"]:
        raise ValueError("Reference transcript does not match the profile.")
    return manifest, reference, artifact, audio, voice_file


def load_model():
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("This configuration requires a compatible NVIDIA GPU and CUDA-enabled PyTorch.")
    torch.set_num_threads(min(8, os.cpu_count() or 4))
    source = Path(os.environ.get("COSYVOICE_SOURCE_DIR", ROOT / LOCK["source_directory"])).resolve()
    model_dir = Path(os.environ.get("COSYVOICE_MODEL_DIR", ROOT / LOCK["directory"])).resolve()
    if not (source / "cosyvoice" / "cli" / "cosyvoice.py").is_file():
        raise FileNotFoundError("CosyVoice source is missing. Run scripts/fetch_source.py or setup.ps1.")
    if not (model_dir / "cosyvoice3.yaml").is_file():
        raise FileNotFoundError("The base model is missing. Run scripts/download_model.py or setup.ps1.")
    actual_commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if actual_commit != LOCK["commit"]:
        raise ValueError(f"Use the pinned CosyVoice source commit: {LOCK['commit']}")
    sys.path.insert(0, str(source))
    sys.path.insert(0, str(source / "third_party" / "Matcha-TTS"))
    from cosyvoice.cli.cosyvoice import AutoModel

    return AutoModel(model_dir=str(model_dir), fp16=True, load_trt=False, load_vllm=False)


def generate(model, text, output, profile=DEFAULT_PROFILE, language="zh", reference_id=None, seed=42):
    import numpy as np
    import soundfile as sf
    import torch
    from transformers import set_seed

    if not text or not text.strip():
        raise ValueError("Enter a non-empty narration script.")
    output = Path(output).resolve()
    metadata = output.with_suffix(".json")
    if output.suffix.lower() != ".wav":
        raise ValueError("Use a .wav output filename.")
    if output.exists() or metadata.exists():
        raise FileExistsError(f"Choose a new output filename: {output}")
    manifest, reference, artifact, audio, voice_file = resolve_profile(profile, language, reference_id)
    cache = torch.load(voice_file, map_location=model.frontend.device, weights_only=True)
    speaker_id = artifact["speaker_id"]
    if speaker_id not in cache:
        raise ValueError("The prompt cache does not contain the requested speaker.")
    model.frontend.spk2info.update(cache)
    set_seed(seed)
    start = time.perf_counter()
    prompt = "You are a helpful assistant.<|endofprompt|>" + reference["text"]
    chunks = list(model.inference_zero_shot(text.strip(), prompt, str(audio), zero_shot_spk_id=speaker_id, stream=False))
    if not chunks:
        raise RuntimeError("The model returned no audio.")
    waveform = torch.cat([chunk["tts_speech"] for chunk in chunks], dim=1).squeeze(0).cpu().float().numpy()
    if not waveform.size or not np.isfinite(waveform).all():
        raise RuntimeError("The model returned empty or non-finite audio.")
    peak = float(np.abs(waveform).max())
    if peak < 1e-5:
        raise RuntimeError("The model returned near-silent audio.")
    if peak > 0.999:
        waveform *= 0.999 / peak
    output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output, waveform, model.sample_rate, subtype="PCM_16")
    report = {
        "engine": "CosyVoice 3", "model": LOCK, "profile_id": manifest["profile_id"],
        "reference_id": reference["id"], "reference_sha256": reference["sha256"],
        "voice_file_sha256": artifact["sha256"], "text": text.strip(), "language": language,
        "seed": seed, "sample_rate": model.sample_rate,
        "duration_seconds": round(len(waveform) / model.sample_rate, 3),
        "generation_seconds": round(time.perf_counter() - start, 3), "output_filename": output.name,
    }
    metadata.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--language", choices=["zh", "en"], default="zh")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--reference-id", help="Optional alternative: zh-02 or en-02")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    text = read_text(args.text_file)
    resolve_profile(args.profile, args.language, args.reference_id)
    if args.output.exists() or args.output.with_suffix(".json").exists():
        parser.error("Output already exists; choose a new filename.")
    model = load_model()
    report = generate(model, text, args.output, args.profile, args.language, args.reference_id, args.seed)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
