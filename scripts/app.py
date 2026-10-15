"""Run the public voice profile locally in a small bilingual interface."""
import argparse
from datetime import datetime
import uuid

from synthesize import ROOT, generate, load_model, read_text
import gradio as gr


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=7861)
    args = parser.parse_args()
    model = load_model()

    def run(text, language):
        output = ROOT / "outputs" / (datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6] + ".wav")
        try:
            result = generate(model, text, output, language=language)
        except (ValueError, RuntimeError, OSError) as exc:
            raise gr.Error(str(exc)) from exc
        return str(output), f"{output}\n{result['duration_seconds']} seconds"

    with gr.Blocks(title="公开声音库 · CosyVoice 3") as app:
        gr.Markdown("# 公开声音库 · CosyVoice 3\n输入新文案，使用已授权公开的音色生成配音。\n\nGenerate narration with the published, speaker-authorized voice.")
        language = gr.Radio(choices=[("普通话 / Chinese", "zh"), ("英文 / English", "en")], value="zh", label="语言 / Language")
        text = gr.Textbox(label="配音文案 / Narration script", lines=6, value=read_text(ROOT / "examples" / "demo-zh.txt"))
        button = gr.Button("生成配音 / Generate", variant="primary")
        output = gr.Audio(label="试听与下载 / Listen and download", type="filepath")
        status = gr.Textbox(label="保存位置 / Saved file", interactive=False)
        button.click(run, [text, language], [output, status], api_name="generate")
    app.queue(default_concurrency_limit=1).launch(server_name="127.0.0.1", server_port=args.port, share=False)


if __name__ == "__main__":
    main()
