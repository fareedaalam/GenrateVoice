# Deploying the XTTS-v2 Voice Cloner to Dokploy

Step-by-step guide for deploying the [Gradio voice cloning app](app.py) to a
self-hosted VPS running [Dokploy](https://dokploy.com/).

This app already ships a CPU-only `Dockerfile` and `docker-compose.yml`
(this directory), so no code changes are needed — just point Dokploy at
them.

## Prerequisites

- A Dokploy instance running on your VPS, with the dashboard reachable in
  your browser.
- This repo pushed to a Git remote Dokploy can pull from (GitHub, GitLab,
  etc.), with your target branch pushed:

  ```bash
  git push origin dev
  ```

- No GPU required — the container installs the CPU build of
  `torch`/`torchaudio`. A GPU VPS works too but gives no benefit here since
  the Dockerfile doesn't install CUDA-enabled torch.
- At least ~4GB free disk (image layers + the ~1.8GB XTTS-v2 model download)
  and ideally 2+ CPU cores (CPU inference is slower than GPU).

## What's already in place

| File | Purpose |
|---|---|
| [Dockerfile](Dockerfile) | CPU-only image: Python 3.11-slim, CPU torch wheels, pinned `transformers`/`gradio`/`huggingface-hub` versions (see comments in the file for why each pin is required together), runs `python app.py` |
| [docker-compose.yml](docker-compose.yml) | Builds from the repo root, publishes port `7860:7860`, sets `COQUI_TOS_AGREED=1` (skips the interactive CPML license prompt, which would otherwise hang forever in a container), binds `GRADIO_SERVER_NAME=0.0.0.0`, and mounts a named volume `tts-models` at `/data/tts` so the downloaded model survives redeploys |

You don't need to edit either file to deploy — only to change ports, add
auth, etc. if you want to customize the deployment.

## Step 1 — Create the service in Dokploy

1. In the Dokploy dashboard, create a new **Project** (or pick an existing
   one) and add a new **Service**.
2. Choose **Docker Compose** as the build/source type (not Dockerfile,
   Nixpacks, or Static — Compose is what defines the port mapping and the
   named volume together).

## Step 2 — Configure the source

- **Repository**: your Git remote for this repo, e.g.
  `https://github.com/fareedaalam/GenrateVoice.git`
- **Branch**: the branch you pushed, e.g. `dev`
- **Build Path**: `/` (repo root)

  This must be the repo root, not `examples/voice_cloning` — the compose
  file's build context is `../..`, i.e. it expects to build from the repo
  root so it can `COPY . /app` the whole package.

## Step 3 — Configure the compose file

- **Compose file path**: `examples/voice_cloning/docker-compose.yml`
- **Env vars**: none needed. All required env vars
  (`COQUI_TOS_AGREED`, `TTS_HOME`, `GRADIO_SERVER_NAME`,
  `GRADIO_SERVER_PORT`) are hardcoded directly in the compose file already —
  you don't need to add anything in Dokploy's env var UI for this app to
  work.
- **Volumes**: Dokploy should auto-detect the `tts-models` named volume
  declared in the compose file. Leave it as a named volume (not converted
  to a bind mount) so it's included in Dokploy's automatic volume backups.

## Step 4 — Configure the domain/port

1. Go to the service's **Domains** tab.
2. Add your domain (or use a free `*.traefik.me` domain for quick testing
   without owning a domain).
3. Set **Container Port** to `7860` — this tells Dokploy's Traefik router
   which internal port to forward to. It does *not* expose the port to the
   internet by itself; the domain + Traefik routing does that.
4. Enable **HTTPS** / Let's Encrypt for a real domain (skip for
   `*.traefik.me`, which is HTTP-only).

## Step 5 — Deploy

1. Click **Deploy** and watch the build logs.
2. The first build installs torch, transformers, gradio, and the rest of
   the pinned dependencies — this can take several minutes.
3. The **first request** to the app triggers the ~1.8GB XTTS-v2 model
   download into the `tts-models` volume — this can also take a while
   depending on the VPS's network speed. Subsequent requests and redeploys
   reuse the cached model from the volume.

## Step 6 — Verify

Check the app responds:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" https://<your-domain>
```

A `200` means the Gradio UI is up. Open the domain in a browser, upload a
short (6-30s) reference clip, type some text, and confirm you get cloned
audio back.

To confirm the model volume is actually persisting (and you're not
re-downloading 1.8GB on every deploy), trigger a second deploy in Dokploy
and check that the app becomes responsive again quickly, without a long
delay before the first successful clone.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Error: No start command could be found` | Wrong build type was selected (e.g. Nixpacks instead of Docker Compose) | Re-check Step 1 — this app must use **Docker Compose**, since it needs the Dockerfile's `CMD` plus the volume/port config from the compose file |
| Build fails pulling huge CUDA layers | A GPU-flavored torch install snuck in | Shouldn't happen here — the Dockerfile pins the CPU wheel index explicitly. If you edited the Dockerfile, re-check that line first |
| App builds and starts but the domain shows a connection error/timeout | Container Port in the Domains tab doesn't match the port the app listens on | Confirm it's set to `7860`, matching `GRADIO_SERVER_PORT` in the compose file |
| Container starts then immediately exits | CPML license prompt is blocking on stdin | Confirm `COQUI_TOS_AGREED=1` is present in the compose file's `environment:` block (it should be, untouched) |
| Every redeploy re-downloads the ~1.8GB model | Volume isn't actually persisting (converted to bind mount, or removed between deploys) | In the service's Volumes section, confirm `tts-models` is a named volume, not deleted/recreated on each deploy |

## Notes

- This app is for cloning voices you own or have explicit consent to
  clone. See the [ethical use notice](README.md#%EF%B8%8F-ethical-use-notice)
  in this directory's README before deploying it somewhere others can use
  it.
- XTTS-v2 usage is governed by the Coqui Public Model License (CPML) —
  free for personal/research/non-commercial use; commercial use needs a
  separate license from Coqui. See the
  [License section](README.md#license) in the README.
