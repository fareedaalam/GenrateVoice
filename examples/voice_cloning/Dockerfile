# CPU-only image for the XTTS-v2 voice cloning Gradio app.
# Build from the repo root: docker build -f examples/voice_cloning/Dockerfile .
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    espeak-ng \
    libsndfile1 \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install CPU-only torch FIRST, from PyTorch's own CPU wheel index. Without
# this, plain `pip install torch` on Linux pulls the CUDA build by default,
# dragging in ~2GB+ of unused nvidia_cudnn/nvidia_cublas etc. packages that
# are dead weight on a GPU-less VPS.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir "torch==2.2.2" "torchaudio==2.2.2" \
        --index-url https://download.pytorch.org/whl/cpu

# Pinned versions below are required together on Python 3.11 CPU:
# - gradio 4.44.1 is the newest release still compatible with
#   huggingface-hub<1.0 (needed by transformers 4.42.4, see next line)
# - transformers 4.42.4 is the newest release that still exports the
#   generation-API symbols (BeamSearchScorer etc.) XTTS's streaming
#   generator imports; transformers 5.x removed them
# - pydantic<2.10 and fastapi/starlette pins avoid a gradio_client
#   schema bug and a template-rendering break against newer releases
#   of those two, which gradio 4.44.1 was not built against
# - numba==0.59.1 and spacy[ja]<3.8 avoid pulling versions with no
#   prebuilt wheel (spacy 3.8's thinc dependency needs Python>=3.10;
#   numba's newest releases may lack wheels for some platforms)
RUN pip install --no-cache-dir "numba==0.59.1" "spacy[ja]<3.8,>=3" \
    && pip install --no-cache-dir -e . \
    && pip install --no-cache-dir \
        "transformers==4.42.4" \
        "gradio==4.44.1" \
        "huggingface-hub>=0.23.2,<1.0" \
        "pydantic<2.10" \
        "fastapi==0.115.6" \
        "starlette==0.41.3"

# COQUI_TOS_AGREED=1 skips the interactive CPML license prompt on first
# model download, which would otherwise hang forever (no stdin in a container).
# TTS_HOME points the ~1.8GB model cache at a path meant to be a mounted
# volume, so it survives container restarts/redeploys.
ENV COQUI_TOS_AGREED=1 \
    TTS_HOME=/data/tts \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860

EXPOSE 7860

WORKDIR /app/examples/voice_cloning
CMD ["python", "app.py"]
