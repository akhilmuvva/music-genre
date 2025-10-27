# PowerShell helper to create venv, install dependencies and run Django dev server
# Usage: .\run_django.ps1

$env:VENV_DIR = "venv"
if (-not (Test-Path $env:VENV_DIR)) {
    python -m venv $env:VENV_DIR
}

# Activate virtualenv
$activate = Join-Path $env:VENV_DIR "Scripts\Activate.ps1"
if (Test-Path $activate) {
    . $activate
}

# Install requirements
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
}

# Run migrations and start server on port 8000
python manage.py migrate
python manage.py runserver 8000
