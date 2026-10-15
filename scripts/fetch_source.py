"""Fetch the exact upstream CosyVoice and Matcha-TTS source revisions."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", *map(str, args)], text=True).strip()


def main():
    lock = json.loads((ROOT / "model.lock.json").read_text(encoding="utf-8"))
    source = ROOT / lock["source_directory"]
    source.parent.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout", lock["repository"], str(source)], check=True)
    elif not (source / ".git").exists():
        raise RuntimeError(f"Existing path is not the managed git checkout: {source}")
    if git("-C", source, "remote", "get-url", "origin").removesuffix(".git") != lock["repository"].removesuffix(".git"):
        raise RuntimeError("Existing source checkout has an unexpected origin.")
    # A new --no-checkout clone shows deleted tracked files; only reject changes on an existing checkout.
    if (source / "cosyvoice").exists() and git("-C", source, "status", "--porcelain"):
        raise RuntimeError("Upstream checkout has local changes; preserve them before rerunning setup.")
    subprocess.run(["git", "-C", str(source), "checkout", "--detach", lock["commit"]], check=True)
    subprocess.run(["git", "-C", str(source), "submodule", "update", "--init", "--recursive"], check=True)
    assert git("-C", source, "rev-parse", "HEAD") == lock["commit"]
    assert git("-C", source / "third_party/Matcha-TTS", "rev-parse", "HEAD") == lock["matcha_commit"]
    print(f"Ready: {source}")


if __name__ == "__main__":
    main()
