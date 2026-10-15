# CosyVoice 3 公开声音库

一套可下载、可重复使用的个人声音素材：普通话为主，包含英文参考。录音由仓库发布者本人提供，并明确授权所有人使用该声音生成配音，包括商业视频。参见 [声音许可与说话人授权](VOICE_LICENSE.md)。

**声音素材：CC0 1.0。原创代码和说明：MIT。** [English guide](README.en.md)

## 先试听

| 配音 | 文件 | 时长 |
| --- | --- | --- |
| 普通话新文案 | [下载 / 试听 WAV](examples/cosy-zh.wav) · [文案](examples/demo-zh.txt) | 16.40 秒 |
| 英文新文案 | [下载 / 试听 WAV](examples/cosy-en.wav) · [文案](examples/demo-en.txt) | 16.52 秒 |

也可以在 [Releases](https://github.com/elonmaskhair-prog/cosyvoice3-voice-library/releases/latest) 下载完整发布包。参考音频、音色缓存和示例音频均直接保存在 Git 中，无需 Git LFS。

## 这里有什么

| 路径 | 内容 |
| --- | --- |
| `voices/my-voice-v1/references/` | 中文两段、英文两段；48kHz 单声道 WAV，每段约 7–9 秒，附准确逐字稿 |
| `voices/my-voice-v1/cosy/` | 四份可重复加载的 CosyVoice 说话人提示缓存 `.pt` |
| `voices/my-voice-v1/profile.json` | 参考选择、默认语言、SHA-256、模型版本及来源 |
| `recordings/raw/session-01.m4a` | 本人手机原始录音，约 7 分 06 秒 |
| `recordings/scripts/`、`recordings/transcripts/` | 原创朗读稿件，包括录音时提供的可选短句 |
| `recordings/analysis/` | 原录音的本地自动转写、时间戳及字幕；全文未逐字人工校对 |
| `recordings/selection.json` | 四段参考在原录音中的切分位置 |
| `examples/` | 可直接导入剪辑软件的 24kHz、单声道、16位 WAV，以及文案和生成记录 |
| `scripts/` | 下载模型、校验素材、命令行生成和本地界面 |

**输入：声音档案 + 新文案 + 对应 CosyVoice 基础模型。输出：新的 WAV 配音和同名 JSON 参数记录。** `.pt` 是录音的提示特征缓存，需要基础模型；本项目没有微调或发布一个独立的新基础模型。

## 在 Windows 上运行

已验证环境：Windows、Python 3.12.13、NVIDIA RTX 5080 Laptop 16GB、PyTorch 2.8.0 / CUDA 12.8。运行脚本使用 NVIDIA CUDA。已有 WAV 素材可以在任意支持该格式的设备上使用。

先安装并将 [Git](https://git-scm.com/downloads)、[uv](https://docs.astral.sh/uv/getting-started/installation/) 和 [FFmpeg](https://ffmpeg.org/download.html) 加入 `PATH`。

在 PowerShell 中执行：

```powershell
git clone https://github.com/elonmaskhair-prog/cosyvoice3-voice-library.git
cd cosyvoice3-voice-library
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
```

安装脚本创建 Python 环境，获取固定版本的 CosyVoice / Matcha-TTS 源码，安装依赖，下载并校验官方基础模型。首次需要联网及数 GB 下载空间。基础模型信息见 [model.lock.json](model.lock.json)。

完成后双击 **`start.cmd`**，等待加载，再打开 <http://127.0.0.1:7861>。选择语言、输入一个短段落并生成，输出保存在 `outputs/`。界面仅监听本机。关闭窗口或按 Ctrl+C 停止。

## 从视频项目调用

把新文案保存成 UTF-8 文本，在仓库根目录执行：

```powershell
.\.venv\Scripts\python.exe scripts\synthesize.py --text-file examples\demo-zh.txt --output outputs\video-001.wav
```

英文使用对应参考：

```powershell
.\.venv\Scripts\python.exe scripts\synthesize.py --language en --text-file examples\demo-en.txt --output outputs\video-002.wav
```

默认参考为 `zh-01` 和 `en-01`。加 `--reference-id zh-02` 或 `--reference-id en-02` 可比较备用录音。已有同名输出时脚本会要求换文件名。每次生成一个短段落，试听后用于视频；长旁白可以分段生成再在剪辑软件中拼接。

已经有匹配的上游源码与模型时，可在启动前设置 `COSYVOICE_SOURCE_DIR`、`COSYVOICE_MODEL_DIR` 使用已有目录；源码提交必须匹配锁定版本。以后迁移或更换引擎时，同时保留参考 WAV、逐字稿和配置。

## 验证与复现

```powershell
python scripts\verify_assets.py
```

这项校验无需 GPU，会检查公开素材的 SHA-256、逐字稿、参考 WAV 格式与时长。

四段参考和两份示例配音通过本地 Whisper large-v3-turbo 重新转写，忽略标点和大小写后与对应文字一致。结果见 [audio-checks.json](voices/my-voice-v1/audio-checks.json)。这个检查不评价音色相似度、口音或自然度，仍应试听。原录音英文后半段有改词和未读完的段落，未选作默认参考；全文 ASR 不应直接作为精确训练标注。

入口依赖见 `requirements.txt`；本次验证的 Windows 完整依赖版本见 `requirements-resolved-win.txt`。严格复现依赖时可用后者替换前者。固定随机种子有助于比较，但不同设备或软件版本未必产生逐字节相同的音频。

## 许可与来源

任何人可下载、复制、修改、分发声音素材，用该声音生成新配音，并用于商业或非商业项目。具体范围和说话人授权见 [VOICE_LICENSE.md](VOICE_LICENSE.md)，CC0 全文见 [LICENSES/CC0-1.0.txt](LICENSES/CC0-1.0.txt)。原创程序与文档采用 [MIT](LICENSE)。

运行时使用 [CosyVoice](https://github.com/QwenAudio/CosyVoice) 和官方 [Fun-CosyVoice3-0.5B-2512](https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512)。这些第三方组件保留各自许可，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。GitHub 提供素材下载；新配音由你的本地程序生成。
