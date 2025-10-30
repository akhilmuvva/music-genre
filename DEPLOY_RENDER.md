# Deploying to Render (Heroku-style PaaS)

This project can be deployed to a Heroku-style PaaS such as Render, Railway, or Fly. Below are quick, tested steps for Render (recommended):

1) Prepare code
   - We include a `Procfile` at the repo root which starts Gunicorn using the Django WSGI app located at `server/music_genre_classifier`.
   - The Django Dockerfile is under `server/Dockerfile` (Render can build from that context).

2) Create a Render account and connect your GitHub repository.
   - Go to https://dashboard.render.com and sign in.
   - Create a new Web Service and connect your GitHub repo.
   - For **Environment**, choose **Docker** and set the Docker context to `server` (or point Render to use the `server/Dockerfile`).
   - Set the branch to `main` and enable Auto-Deploy if desired.

3) Environment variables
   - Add the following environment variables in the Render dashboard (Settings → Environment):
     - `DJANGO_SECRET_KEY` (generate a secure random string)
     - `API_TOKEN` (server's API token used by the client)
     - `REACT_APP_API_TOKEN` (client token if used)
     - `ALLOWED_HOSTS` (set to your Render service domain and any custom domains)
     - Any other secrets used by the server (database URL, etc.)

4) Model files
   - If your model pickles are small, include them in `server/models/` and commit to the repo. The Dockerfile will copy them into the container.
   - If the model files are large, store them in object storage (S3/GCS) and make the app download them at startup, or mount a persistent volume if your PaaS supports it.

5) Domain & TLS
   - Render provides automatic TLS for connected custom domains.
   - Add a custom domain in the Render dashboard and update your DNS records to point to Render.

6) Logs & debugging
   - Use the Render dashboard to view real-time logs and the service console.

7) Optional: split frontend
   - Host the React app separately on Vercel or Netlify (fast, free). Point the frontend to the Render API endpoint.

If you'd like, I can:
- Add a GitHub Actions workflow that builds the Docker image and pushes to GHCR (useful if you prefer deploying via container registry), or
- Create a sample cloud-init/user-data for other providers.
