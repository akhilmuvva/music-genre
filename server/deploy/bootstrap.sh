#!/usr/bin/env bash
set -euo pipefail

# server/deploy/bootstrap.sh
# Bootstrap script to prepare an Ubuntu VPS for deploying the music-genre app
# - Installs Docker engine & compose plugin
# - Creates deploy directory and clones repo (if missing)
# - Creates a minimal .env template (safe permissions)
# - Pulls and starts docker-compose.prod.yml
#
# Usage on the VPS (run as a non-root user with sudo privileges):
#   curl -fsSL https://example.com/bootstrap.sh -o bootstrap.sh && bash bootstrap.sh 
# or copy this script to the VPS and run:
#   chmod +x bootstrap.sh
#   ./bootstrap.sh GIT_REPO_URL /srv/music-genre yourdomain.com

GIT_REPO_URL=${1:-https://github.com/akhilmuvva/music-genre.git}
REPO_DIR=${2:-/srv/music-genre}
DOMAIN=${3:-yourdomain.com}

echo "Bootstrap start: repo=${GIT_REPO_URL} dir=${REPO_DIR} domain=${DOMAIN}"

if [ "$EUID" -eq 0 ]; then
  echo "This script should not be run as root. Run as a normal user with sudo privileges." >&2
  exit 1
fi

sudo apt update
sudo apt upgrade -y

echo "Installing prerequisites..."
sudo apt install -y ca-certificates curl gnupg lsb-release git

echo "Installing Docker..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "Adding $USER to docker group (you may need to logout/login for this to take effect)..."
sudo usermod -aG docker "$USER" || true

echo "Preparing repo directory..."
if [ ! -d "$REPO_DIR" ]; then
  mkdir -p "$REPO_DIR"
  git clone "$GIT_REPO_URL" "$REPO_DIR"
else
  if [ -d "$REPO_DIR/.git" ]; then
    (cd "$REPO_DIR" && git fetch --all && git reset --hard origin/main)
  else
    echo "Directory $REPO_DIR exists but is not a git repo; pulling into it is skipped." >&2
  fi
fi

cd "$REPO_DIR"

# Create a minimal .env if not present
if [ ! -f .env ]; then
  echo "Creating .env template (update values before starting services)..."
  cat > .env <<EOF
DJANGO_SECRET_KEY=replace_me_with_a_strong_secret
API_TOKEN=replace_with_api_token_for_server
REACT_APP_API_TOKEN=replace_with_api_token_for_client
ALLOWED_HOSTS=${DOMAIN}
DEBUG=0
EOF
  chmod 600 .env
fi

echo "Pulling and starting Docker Compose (production file if present)..."
COMPOSE_FILE=docker-compose.prod.yml
if [ ! -f "$COMPOSE_FILE" ]; then
  COMPOSE_FILE=docker-compose.yml
fi

docker compose -f "$COMPOSE_FILE" pull || true
docker compose -f "$COMPOSE_FILE" up -d --build

echo "Bootstrap complete. Check services with: docker compose -f $COMPOSE_FILE ps"
echo "If you modified .env, restart containers: docker compose -f $COMPOSE_FILE up -d --build"
