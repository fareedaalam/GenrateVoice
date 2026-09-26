# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

This is a fork/checkout of **Coqui TTS** (`coqui-ai/TTS`), an upstream deep-learning text-to-speech library, with one custom addition on top: `examples/voice_cloning/`, a small standalone XTTS-v2 voice-cloning CLI + Gradio web app built on the library's `TTS.api.TTS` class. Most of the repo (`TTS/`, `tests/`, `recipes/`, `notebooks/`, `docs/`) is upstream Coqui code; treat it as vendored/library code unless the task specifically asks to change TTS internals.

## Running the voice cloning app locally

The user asked: **do not run this yourself** — only give them the commands to run.

```bash
# one-time setup (macOS-verified; use Python 3.10 or 3.11, not 3.9/3.12)
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install "transformers==4.42.4"   # newer transformers dropped APIs XTTS's streaming generator needs

# web UI
pip install "gradio==4.44.1" "huggingface-hub>=0.23.2,<1.0"
python examples/voice_cloning/app.py
# then open http://127.0.0.1:7860
```

```bash
# CLI usage instead of the web UI
python examples/voice_cloning/clone_voice.py \
    --text "Hello, this is a cloned voice." \
    --speaker-wav path/to/reference.wav \
    --language en \
    --output examples/voice_cloning/output/cloned.wav
```

Notes:
- First model load prompts interactively to accept the Coqui Public Model License (CPML); set `export COQUI_TOS_AGREED=1` to skip this (needed for any non-interactive/CI run).
- If `numba`/`llvmlite` fails to find a prebuilt wheel and tries to compile from source, pin `pip install "numba==0.59.1"` before re-running `pip install -e .`.
- Gradio must stay on a 4.x release (`gradio==4.44.1` is verified) — plain `pip install gradio` pulls a version requiring `huggingface-hub>=1.16`, which conflicts with the pinned `transformers==4.42.4` (needs `huggingface-hub<1.0`).
- Full context and the pinned-version rationale live in [examples/voice_cloning/README.md](examples/voice_cloning/README.md) and [examples/voice_cloning/Dockerfile](examples/voice_cloning/Dockerfile).
- Docker: `docker compose -f examples/voice_cloning/docker-compose.yml up --build` from the repo root builds a CPU-only image with all the pins above baked in.

## Voice cloning app architecture

- [examples/voice_cloning/voice_cloner.py](examples/voice_cloning/voice_cloner.py) — `VoiceCloner` class: lazily loads the XTTS-v2 model (`tts_models/multilingual/multi-dataset/xtts_v2`) via `TTS.api.TTS`, auto-selects CUDA if available, exposes `.clone(text, speaker_wav, output_path, language)`. This is the single reusable entry point; both the CLI and the web UI wrap it.
- [examples/voice_cloning/clone_voice.py](examples/voice_cloning/clone_voice.py) — argparse CLI wrapper around `VoiceCloner`.
- [examples/voice_cloning/app.py](examples/voice_cloning/app.py) — Gradio Blocks UI wrapper around `VoiceCloner`. Note `demo.launch(show_api=False)` — required to avoid a `gradio_client` crash on API-schema generation for the `Audio` component.
- The package's built-in `tts-server` CLI (`TTS/server/`) does *not* support arbitrary reference-audio voice cloning, which is why this separate example app exists.

## Commonly used commands (upstream TTS library)

```bash
make install       # pip install -e .[all], for library development
make deps           # pip install -r requirements.txt
make test           # nose2 -F -v -B --with-coverage --coverage TTS tests (main test suite)
make test_tts       # just tests.tts_tests
make test_xtts      # just tests.xtts_tests
make test_vocoder   # just tests.vocoder_tests
make test_zoo       # just tests.zoo_tests (pretrained-model smoke tests)
make style          # black + isort on tests/TTS/notebooks/recipes
make lint           # pylint + black --check + isort --check-only
```

Run a single test module directly, e.g.:
```bash
nose2 -v tests.tts_tests.test_xtts
```

## Upstream TTS library structure (for reference)

- `TTS/tts/` — text-to-speech models (`models/`, e.g. `xtts.py`, `vits.py`, `tacotron2.py`), their configs (`configs/`), and layers/utils.
- `TTS/vocoder/` — vocoder models (waveform generation from spectrograms).
- `TTS/vc/` — voice conversion models.
- `TTS/encoder/` — speaker encoder models used for speaker embeddings/cloning.
- `TTS/api.py` — the high-level `TTS` class (`TTS.tts_to_file(...)`, etc.) that the voice-cloning example is built on.
- `TTS/bin/` — training/inference entry-point scripts (`train_tts.py`, `synthesize.py`, `compute_embeddings.py`, ...), also exposed as the `tts` console script (`TTS.bin.synthesize:main`).
- `TTS/server/` — the built-in `tts-server` Flask demo server (pre-configured multi-speaker models only, no arbitrary voice cloning).
- `tests/` mirrors this by suite: `tts_tests`, `tts_tests2`, `xtts_tests`, `vocoder_tests`, `vc_tests`, `zoo_tests` (downloads real pretrained models), `data_tests`, `text_tests`, `aux_tests`, `inference_tests`, plus `bash_tests/` run via `run_bash_tests.sh`.
- Python version constraint: `>=3.9,<3.12` per `setup.py`/`pyproject.toml`, though the voice-cloning example specifically recommends 3.10/3.11 (see above).
