# XTTS-v2 Voice Cloner

A small reusable tool for zero-shot voice cloning built on top of Coqui's
[XTTS-v2](https://huggingface.co/coqui/XTTS-v2) model, via the `TTS.api.TTS`
class already included in this repo/package.

## ⚠️ Ethical use notice

This tool can reproduce a person's voice from a short audio sample. Use it
**only** for voices you own or have explicit, informed consent to clone
(e.g. your own voice, or a collaborator's with their agreement). Do **not**
use it to impersonate someone without consent, commit fraud, or deceive
anyone. You are responsible for how you use this tool.

## License

XTTS-v2 weights are free to download, but usage is governed by the
**Coqui Public Model License (CPML) v0.1** (https://coqui.ai/cpml):
free for personal, research, and non-commercial use; commercial use
requires a separate paid license from Coqui.

## Prerequisites

- Python 3.10 or 3.11 (this repo declares `>=3.9,<3.12`, but on 3.9 several
  transitive dependencies — `spacy`/`thinc`, `bangla` — no longer publish
  Python-3.9-compatible releases; 3.10/3.11 avoid that entirely)
- `pip3 install tts`, or `pip install -e .` from the repo root if you're
  working from this checkout
- ~1.8GB free disk space for the first-time model download
- A GPU is optional but speeds up synthesis considerably

### Verified working setup (macOS, tested in this repo)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
# transformers' latest major version dropped APIs XTTS's streaming
# generator still imports (BeamSearchScorer etc.) — pin a compatible one:
pip install "transformers==4.42.4"
```

If dependency resolution picks a `numba`/`llvmlite` version with no
prebuilt wheel for your platform (it tries to compile LLVM from source and
fails), pin an older numba first, e.g. `pip install "numba==0.59.1"`,
then re-run `pip install -e .`.

### First run: accepting the license

The first time you load XTTS-v2, the underlying `ModelManager` will prompt
you interactively to accept the CPML license:

```
 > You must agree to the terms of the Coqui Public Model License (CPML) [y/n]
```

Type `y` and it's remembered for future runs (a marker file is written to
the model cache dir). To skip the prompt (e.g. for scripting/CI), set:

```bash
export COQUI_TOS_AGREED=1
```

## Usage

### CLI

```bash
python examples/voice_cloning/clone_voice.py \
    --text "Hello, this is a cloned voice." \
    --speaker-wav path/to/reference.wav \
    --language en \
    --output examples/voice_cloning/output/cloned.wav
```

Use `--text-file path/to/text.txt` instead of `--text` for longer passages.
Multiple reference clips can be passed to `--speaker-wav` for better cloning
quality.

### As a Python module

```python
from examples.voice_cloning.voice_cloner import VoiceCloner

cloner = VoiceCloner()  # auto-selects GPU if available
cloner.clone(
    text="Hello, this is a cloned voice.",
    speaker_wav="path/to/reference.wav",
    output_path="examples/voice_cloning/output/cloned.wav",
    language="en",
)
```

### Web UI (Gradio)

```bash
pip install gradio
python examples/voice_cloning/app.py
```

Then open http://127.0.0.1:7860 to upload a reference clip, type text, pick
a language, and generate/play the cloned audio in the browser.

Note: the package's built-in `tts-server` command does **not** support
arbitrary voice cloning (no reference-audio upload — it's built for
pre-configured multi-speaker models), so this Gradio app is provided instead.

## Reference audio tips

- 6-30 seconds long
- Single speaker, minimal background noise or music
- Clear, natural speech (avoid heavy filters/effects)

## Supported languages

| Code | Language | Code | Language | Code | Language |
|------|----------|------|----------|------|----------|
| en | English | pl | Polish | ko | Korean |
| es | Spanish | tr | Turkish | ja | Japanese |
| fr | French | ru | Russian | hi | Hindi |
| de | German | nl | Dutch | | |
| it | Italian | cs | Czech | | |
| pt | Portuguese | ar | Arabic | | |
| | | zh-cn | Chinese | | |
| | | hu | Hungarian | | |
