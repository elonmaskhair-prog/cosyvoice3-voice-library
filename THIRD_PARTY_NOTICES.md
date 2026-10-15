# Third-party components

The voice recordings were supplied by this repository's publisher. The reusable prompts and examples were generated locally using these upstream components:

| Component | Pinned version | Source / license |
| --- | --- | --- |
| CosyVoice | `074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc` | [QwenAudio/CosyVoice](https://github.com/QwenAudio/CosyVoice), Apache-2.0 |
| Matcha-TTS submodule | `dd9105b34bf2be2230f4aa1e4769fb586a3c824e` | [shivammehta25/Matcha-TTS](https://github.com/shivammehta25/Matcha-TTS), Apache-2.0 |
| Fun-CosyVoice3-0.5B-2512 | `29e01c4e8d000f4bcd70751be16fa94bf3d85a18` | [FunAudioLLM model](https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512), Apache-2.0 as identified in the model card |
| Whisper large-v3-turbo | SHA-256 recorded in `recordings/asr-model.lock.json` | [openai/whisper](https://github.com/openai/whisper), MIT; used for automatic transcript checks |
| WeText runtime | `0.1.8` | [pengzhendong/wetext](https://github.com/pengzhendong/wetext), Apache-2.0 |

The bootstrap scripts fetch the pinned upstream source and model files, retaining their upstream notices. The original wrapper code here does not relicense those components. Python dependencies and FFmpeg retain their own licenses. The voice prompt cache is not a replacement for the base model.
