<#
.SYNOPSIS
  PowerShell helper to copy `bootstrap.sh` to a remote VPS, run it, and copy model files.

USAGE
  .\run_bootstrap_and_copy.ps1 -VpsIp 203.0.113.12 -DeployUser deployuser -SshKeyPath C:\Users\akhil\.ssh\id_rsa -Domain genresnap.com

NOTES
  - This script does NOT run with elevated privileges locally. It uses scp/ssh to run the bootstrap script on the remote host.
  - You will be prompted for the remote user's sudo password when the bootstrap script runs (unless the user has passwordless sudo).
  - The script only assembles and runs the commands; it does not change local files.
#>

param(
  [Parameter(Mandatory=$true)] [string] $VpsIp,
  [Parameter(Mandatory=$true)] [string] $DeployUser,
  [Parameter(Mandatory=$true)] [string] $SshKeyPath,
  [Parameter(Mandatory=$true)] [string] $Domain,
  [Parameter(Mandatory=$false)] [int] $SshPort = 22
)

function Test-Preconditions {
  if (-not (Test-Path .\server\deploy\bootstrap.sh)) {
    Write-Error "bootstrap.sh not found at .\server\deploy\bootstrap.sh. Run from repo root."
    exit 2
  }
  if (-not (Test-Path $SshKeyPath)) {
    Write-Error "SSH key not found at path: $SshKeyPath"
    exit 3
  }
}

Test-Preconditions


# Build remote target strings safely using ${} to avoid interpolation/parsing issues
$remoteTarget = "${DeployUser}@${VpsIp}"
$remoteBootstrapDest = "${remoteTarget}:/tmp/bootstrap.sh"

$scpCmd = "scp -i `"$SshKeyPath`" -P $SshPort .\server\deploy\bootstrap.sh $remoteBootstrapDest"
Write-Host "Running: $scpCmd"
& scp -i $SshKeyPath -P $SshPort .\server\deploy\bootstrap.sh $remoteBootstrapDest

$runCmd = "ssh -i `"$SshKeyPath`" -p $SshPort $remoteTarget `"bash /tmp/bootstrap.sh https://github.com/akhilmuvva/music-genre.git /srv/music-genre $Domain`""
Write-Host "Executing remote bootstrap (may prompt for sudo password):"
Write-Host $runCmd
& ssh -i $SshKeyPath -p $SshPort $remoteTarget "bash /tmp/bootstrap.sh https://github.com/akhilmuvva/music-genre.git /srv/music-genre $Domain"

Write-Host "Bootstrap finished (check remote logs if errors occurred). Now copying model files..."

$modelFiles = @(
  '.\server\models\knn_model.pkl',
  '.\server\models\minmax_scaler.pkl',
  '.\server\models\label_encoder.pkl'
)

foreach ($f in $modelFiles) {
  if (-not (Test-Path $f)) {
    Write-Warning "Model file not found locally: $f — skipping copy."
    continue
  }
  $remoteModelsDest = "${remoteTarget}:/srv/music-genre/server/models/"
  $scpModelCmd = "scp -i `"$SshKeyPath`" -P $SshPort `"$f`" $remoteModelsDest"
  Write-Host "Copying: $f -> $remoteModelsDest"
  & scp -i $SshKeyPath -P $SshPort $f $remoteModelsDest
}

Write-Host "Model copy complete. Next steps on the VPS (SSH in and):"
Write-Host "  1) sudo chmod 600 /srv/music-genre/.env"
Write-Host "  2) sudo chown -R ${DeployUser}:${DeployUser} /srv/music-genre/server/models"
Write-Host "  3) cd /srv/music-genre && docker compose -f docker-compose.prod.yml up -d --build"
Write-Host "  4) tail logs: docker compose -f docker-compose.prod.yml logs -f"

Write-Host "If you want me to run the remote deploy (git pull + docker compose up) after this, run the PowerShell helper remote_deploy.ps1 with the same connection details."
