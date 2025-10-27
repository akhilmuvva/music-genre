# Music Genre Classifier (React + simple backend)

Simple React app that implements a drag-and-drop audio upload UI with an audio preview and a genre prediction. Includes a tiny Express backend (`/server`) that accepts uploaded audio and proxies it to an external model endpoint (or returns a fallback prediction).

Prereqs
- Node.js (16+ recommended)

Install

Open PowerShell in the project folder and run (installs client and server deps):

```powershell
npm install
cd server
npm install
cd ..
```

Run (start backend and frontend in separate terminals):

```powershell
# Terminal 1 - start server
cd server
npm start

# Terminal 2 - start client
cd "c:\\Users\\akhil\\music genre"
npm start
```

The client runs at http://localhost:3000 and the server runs at http://localhost:5000 by default.

Integrating your Colab model

- If you've trained and exported a model in Google Colab, you can either:
  1. Deploy it as an HTTP inference endpoint (recommended): wrap your model in a small Flask/FastAPI app and host it (Cloud Run, Heroku, etc.). Then set the `MODEL_API_URL` environment variable in the server to the endpoint. The server will forward uploaded audio files as multipart form fields to that URL and return the model's JSON response to the client.
  2. Run the model locally: export the model from Colab and run it inside the `server` folder (requires adapting the model code to accept multipart uploads and return JSON).

Example: set MODEL_API_URL (PowerShell)

```powershell
# in server folder
$env:MODEL_API_URL = "https://your-model-endpoint.example.com/predict"
node index.js
```

Server contract
- Endpoint: POST /api/predict
- Request: multipart/form-data with field `file` containing the audio file
- Response: JSON { genre: string, source?: string }

If you want, I can help with:
- Packaging your Colab model into a small Flask/FastAPI server suitable for Cloud Run.
- Example client code for authentication if your hosted model requires an API key.
- Converting the model to a TensorFlow.js format for client-side inference (if the model is small enough).
# Music Genre Classifier (React)

Simple React app that implements a drag-and-drop audio upload UI with an audio preview and a placeholder genre prediction.

Prereqs
- Node.js (16+ recommended)

Install

Open PowerShell in the project folder and run:

```powershell
npm install
```

Run

```powershell
npm start
```

This will open the app at http://localhost:3000

Notes
- The "genre" prediction is a deterministic placeholder for demo purposes.
- Supported file types: MP3, WAV. Max file size: 20 MB (client-side check).

Python / Django backend (added)

I copied a Django-based classifier into `server/music_genre_classifier/`. It's a simple Django project with a `predictor.py` that expects three files in `server/models/`:

- `knn_model.pkl`
- `minmax_scaler.pkl`
- `label_encoder.pkl`

How to run the Django app (PowerShell):

```powershell
# from project root
cd server
.\run_django.ps1
```

Place your model files into `server/models/` before starting the Django server. The `predictor.py` has been updated to load model files from that directory.

Docker / Containers

If you prefer not to install Python locally, there is a Docker setup to run the React client, the existing Node backend and the Django inference service together.

Quick start (requires Docker and docker-compose):

```powershell
# from repo root
docker-compose build
docker-compose up
```

This composes three services:
- `client` — React dev server on port 3000
- `node-backend` — existing Node backend (server/index.js) on port 5000
- `django` — Django inference app on port 8000

Model files should be placed in `server/models/` on the host. The Django container will use files from that directory. If no models are present, the image will create dummy placeholder pickles so you can smoke-test the pipeline.

Production compose

I also added a production compose that builds a static React app and serves it via nginx while running the Django app under gunicorn.

Files added for production:

- `Dockerfile.client.prod` — builds the React app and packages it into an nginx image
- `server/Dockerfile.prod` — production Django image using gunicorn
- `docker/nginx/nginx.conf` — nginx config to serve static files and proxy `/api/` to Django
- `docker-compose.prod.yml` — orchestrates nginx and Django (mounts `server/models` for model files)

To run the production stack (requires Docker):

```powershell
# build and start
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up
```

Notes:
- Place your real model files in `server/models/` on the host before starting the production compose. If no models are found, the Django image will generate dummy pickles for smoke tests.
- If you'd like nginx to reverse-proxy to the Node backend instead (or in addition), I can add that routing and enable the service in `docker-compose.prod.yml`.

Automatic TLS with Caddy and CI/CD

I added a Caddy reverse-proxy to `docker-compose.prod.yml` to provision TLS certificates automatically. The Caddyfile lives at `docker/caddy/Caddyfile` and proxies `/api/*` to the Django service and everything else to the static site served by nginx.

GitHub Actions deploy

I added a sample GitHub Actions workflow at `.github/workflows/deploy.yml` to SSH into your VPS on push to `main`, pull the latest code and restart the production compose. You'll need to add these repository secrets:

- `SSH_HOST` — your server IP or hostname
- `SSH_USER` — user with sudo and Docker access (e.g., ubuntu)
- `SSH_PRIVATE_KEY` — private SSH key for that user (no passphrase) added as secret
- `SSH_PORT` — (optional) default 22
- `REPO_DIR` — directory on the server where your repo is deployed (e.g., `/opt/music-genre`)

Make sure the server has Docker & docker-compose installed and that the private key corresponds to a user with access to the repo directory. The workflow uses `appleboy/ssh-action` to execute remote commands.

Security, tokens and GHCR notes

- API token: The Django `/api/predict` endpoint supports an optional simple API token. Set `API_TOKEN` in the server environment to a secret value to require `X-API-KEY` header on requests. For the React client, set `REACT_APP_API_TOKEN` in the build environment so the client includes `X-API-KEY` when calling the API.

- GHCR images: the CI workflow `build-and-push.yml` builds and publishes images to GitHub Container Registry under `ghcr.io/<owner>/music_genre_django` and `ghcr.io/<owner>/music_genre_client`. The production compose supports pulling these images if you set the `GHCR_OWNER` environment variable on the server (or leave it unset to use local builds).
  If your GHCR images are private, add a repository secret named `GHCR_PAT` containing a Personal Access Token with scopes `write:packages` and `read:packages`. The deploy workflow will use this token to `docker login` on the server before pulling images.

- Systemd unit: there is an example systemd unit at `deploy/musicgenre.service` you can copy to `/etc/systemd/system/` and enable to auto-start the compose on boot.

