"""Download the pinned official inference weights and verify their SHA-256 hashes."""
import hashlib
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "120")
os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "60")


def main():
    from huggingface_hub import snapshot_download
    from requests.exceptions import RequestException

    lock = json.loads((ROOT / "model.lock.json").read_text(encoding="utf-8"))
    destination = ROOT / lock["directory"]
    for attempt in range(5):
        try:
            snapshot_download(repo_id=lock["model_id"], revision=lock["revision"], local_dir=str(destination),
                              ignore_patterns=lock["ignore_patterns"], max_workers=3)
            break
        except (OSError, RequestException):
            if attempt == 4:
                raise
            time.sleep(min(5 * (attempt + 1), 20))
    expected = json.loads((ROOT / "model-files.json").read_text(encoding="utf-8"))
    for name, info in expected.items():
        path = destination / name
        if not path.is_file() or path.stat().st_size != info["size"]:
            raise RuntimeError(f"Model file missing or incomplete: {name}")
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != info["sha256"]:
            raise RuntimeError(f"Model checksum mismatch: {name}")
        print(f"Verified: {name}")
    print(f"Model ready: {destination}")


if __name__ == "__main__":
    main()
