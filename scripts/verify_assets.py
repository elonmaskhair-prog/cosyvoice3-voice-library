"""Verify published assets without downloading models or requiring a GPU."""
import hashlib
import json
from pathlib import Path
import wave

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    manifest = json.loads((ROOT / "assets.sha256.json").read_text(encoding="utf-8"))
    for name, expected in manifest.items():
        path = ROOT / name
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError(f"Asset is missing or modified: {name}")
    directory = ROOT / "voices/my-voice-v1"
    profile = json.loads((directory / "profile.json").read_text(encoding="utf-8"))
    if digest(ROOT / profile["source"]["path"]) != profile["source"]["sha256"]:
        raise RuntimeError("Original recording checksum mismatch.")
    for reference in profile["references"]:
        if digest(directory / reference["audio"]) != reference["sha256"]:
            raise RuntimeError(f"Reference checksum mismatch: {reference['id']}")
        actual = (directory / reference["transcript"]).read_text(encoding="utf-8-sig").strip()
        if actual != reference["text"]:
            raise RuntimeError(f"Transcript mismatch: {reference['id']}")
        with wave.open(str(directory / reference["audio"]), "rb") as audio:
            assert audio.getnchannels() == 1 and audio.getsampwidth() == 2
            assert abs(audio.getnframes() / audio.getframerate() - reference["duration_seconds"]) < 0.001
    for item in profile["engine_artifacts"]["cosy"].values():
        if digest(directory / item["file"]) != item["sha256"]:
            raise RuntimeError("Speaker cache checksum mismatch.")
    print(f"Verified {len(manifest)} files, 4 references, 4 CosyVoice prompts and the original recording.")


if __name__ == "__main__":
    main()
