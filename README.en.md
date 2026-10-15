# CosyVoice 3 public voice library

A reusable, speaker-authorized voice profile for Mandarin and occasional English narration. The repository publisher supplied their own recordings and permits everyone to use the voice, including in commercial projects.

**Original voice assets: CC0 1.0. Original code and documentation: MIT.** See [speaker permission and license scope](VOICE_LICENSE.md). [中文说明](README.md)

## Listen and download

- [Mandarin narration](examples/cosy-zh.wav): 16.40 seconds; [script](examples/demo-zh.txt).
- [English narration](examples/cosy-en.wav): 16.52 seconds; [script](examples/demo-en.txt).
- [Complete release bundle](https://github.com/elonmaskhair-prog/cosyvoice3-voice-library/releases/latest).

The repository includes the original 7-minute phone recording, two Mandarin and two English reference clips with matching transcripts, four CosyVoice prompt caches, model/version metadata, example WAV files and local generation tools. The media files are ordinary Git files; Git LFS is not required.

Reference clips are 48kHz mono PCM16 WAV. Generated examples are 24kHz mono PCM16 WAV and can be imported into video editors. The `.pt` files contain reusable speaker prompts, not a standalone fine-tuned model. New speech requires the matching CosyVoice base model and a new text script.

## Windows quick start

Tested on Windows with Python 3.12.13, RTX 5080 Laptop 16GB, PyTorch 2.8.0 and CUDA 12.8. These runtime scripts use an NVIDIA CUDA GPU. Downloaded WAV files can be used independently of the runtime.

Install [Git](https://git-scm.com/downloads), [uv](https://docs.astral.sh/uv/getting-started/installation/) and [FFmpeg](https://ffmpeg.org/download.html), then ensure they are on `PATH`.

```powershell
git clone https://github.com/elonmaskhair-prog/cosyvoice3-voice-library.git
cd cosyvoice3-voice-library
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
```

Setup creates `.venv`, fetches pinned upstream source and dependencies, and downloads and verifies the official base model. Initial setup downloads several GB. Launch `start.cmd` and open **http://127.0.0.1:7861**. Enter a short paragraph and choose a language. WAV files and metadata are saved under `outputs/`.

Command line:

```powershell
.\.venv\Scripts\python.exe scripts\synthesize.py --text-file examples\demo-zh.txt --output outputs\video-001.wav
.\.venv\Scripts\python.exe scripts\synthesize.py --language en --text-file examples\demo-en.txt --output outputs\video-002.wav
```

Use `--reference-id zh-02` or `--reference-id en-02` to try the alternate reference. Existing outputs are not overwritten. Generate long narration in short paragraphs and assemble the selected takes in your editor.

If the pinned source and model are already installed, set `COSYVOICE_SOURCE_DIR` and `COSYVOICE_MODEL_DIR` to their directories before launching. Preserve the WAV references and transcripts alongside the prompt caches for future engine changes.

## Validation

```powershell
python scripts\verify_assets.py
```

This checks published file hashes, reference transcripts, WAV formats and durations without requiring a GPU. The four selected references and two examples also passed local Whisper transcription comparison, ignoring punctuation and case; see [audio-checks.json](voices/my-voice-v1/audio-checks.json). Automatic transcription is not a rating of speaker similarity, pronunciation or naturalness.

The full recording's automatic transcript has not been manually corrected throughout. Some later English passages contain changed words or incomplete reading and were not selected as reference clips. Do not treat the full automatic transcript as verified training annotation.

`model.lock.json` pins source and model revisions. `requirements-resolved-win.txt` records the validated Windows environment; use it in place of `requirements.txt` for exact dependency versions. Fixed seeds do not guarantee bit-identical audio across hardware or software versions.

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for upstream components and their licenses. GitHub distributes the assets; speech synthesis runs on your own machine.
