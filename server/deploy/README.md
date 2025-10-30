# Deployment helpers

This folder contains helper scripts and instructions for deploying the Music Genre app to a VPS and wiring CI/CD.

Files
- `bootstrap.sh` — Bootstrap an Ubuntu VPS (installs Docker, clones the repo, creates a `.env` template, starts `docker-compose.prod.yml`). Run as a non-root user with sudo privileges on the VPS.
- `setup_github_secrets.ps1` — PowerShell helper to set repository secrets via the `gh` CLI from Windows.

Recommended deployment flow (best practice)
1. Use local testing with Docker Desktop + WSL2 (build & smoke-test your containers locally).
2. Push code to GitHub. Let GitHub Actions build images and push them to GHCR.
3. Use GitHub Actions deploy workflow (SSH) to pull updates on the VPS and run `docker compose`.

Quick start
1. On the VPS (Ubuntu 22.04/24.04), run:
   sudo adduser deployuser
   # configure sudoers or use your existing sudo-enabled account
   # copy bootstrap.sh to VPS and run:
   chmod +x bootstrap.sh
   ./bootstrap.sh https://github.com/akhilmuvva/music-genre.git /srv/music-genre yourdomain.com

2. From Windows, set repo secrets used by the Actions workflows:
   ./setup_github_secrets.ps1 -RepoOwner akhilmuvva -RepoName music-genre -SshPrivateKeyPath C:\path\to\id_rsa

Notes and security
- Revoke any leaked PATs immediately and generate a new token with minimum required scopes.
- Do not commit `.env` to the repository. The `.env` created by `bootstrap.sh` is a template; edit it on the server with secure values and strict permissions (`chmod 600 .env`).
- Prefer GitHub OIDC for GHCR login where possible. If using `GHCR_PAT`, keep it restricted to package write scopes.

If you want, I can also add:
- A GitHub Actions workflow dispatch helper to test deploys safely.
- A Windows PowerShell script that SSHs to the server and runs an atomic update (pull + docker compose up -d --build).
