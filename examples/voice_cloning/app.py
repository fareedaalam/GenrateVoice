#!/usr/bin/env python3
"""Simple Gradio web UI for XTTS-v2 voice cloning.

Requires: pip install gradio
Run:      python examples/voice_cloning/app.py
Then open http://127.0.0.1:7860

Only clone voices you own or have explicit consent to clone.
"""

import sys
from pathlib import Path

try:
    import gradio as gr
except ImportError:
    sys.exit("Gradio is not installed. Install it with: pip install gradio")

from voice_cloner import SUPPORTED_LANGUAGES, VoiceCloner

OUTPUT_PATH = Path(__file__).parent / "output" / "app_output.wav"

cloner = VoiceCloner()


def run_clone(text, speaker_wav, language):
    if not text or not text.strip():
        raise gr.Error("Please enter some text to synthesize.")
    if not speaker_wav:
        raise gr.Error("Please upload a reference audio clip of the voice to clone.")
    output_path = cloner.clone(
        text=text,
        speaker_wav=speaker_wav,
        output_path=OUTPUT_PATH,
        language=language,
    )
    return str(output_path)


with gr.Blocks(title="XTTS-v2 Voice Cloner") as demo:
    gr.Markdown(
        "# XTTS-v2 Voice Cloner\n"
        "Educational use only. Only clone voices you own or have explicit "
        "consent to clone. Never use this for impersonation, fraud, or deception."
    )
    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(label="Text to speak", lines=4, placeholder="Type the text to synthesize...")
            speaker_wav_input = gr.Audio(label="Reference voice (6-30s, clean, single speaker)", type="filepath")
            language_input = gr.Dropdown(choices=SUPPORTED_LANGUAGES, value="en", label="Language")
            clone_button = gr.Button("Clone Voice", variant="primary")
        with gr.Column():
            output_audio = gr.Audio(label="Cloned voice output")

    clone_button.click(
        fn=run_clone,
        inputs=[text_input, speaker_wav_input, language_input],
        outputs=output_audio,
    )

if __name__ == "__main__":
    # show_api=False: avoids a gradio_client bug where API-schema generation
    # for the Audio component crashes on every request, which otherwise
    # breaks the app with "localhost is not accessible" at startup.
    demo.launch(show_api=False)
