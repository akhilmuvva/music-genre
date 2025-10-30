<#
.SYNOPSIS
  Remote deploy helper: SSHs to the VPS, pulls latest code and runs docker compose up.

USAGE
  .\remote_deploy.ps1 -Host 1.2.3.4 -User deployuser -RepoDir /srv/music-genre -PrivateKey C:\Users\you\.ssh\id_rsa

NOTES
  - Requires OpenSSH client available in PowerShell (Windows 10+).
  - The script does not store secrets; pass sensitive values via parameters.
#>

param(
  [Parameter(Mandatory=$true)] [string] $Host,
  [Parameter(Mandatory=$true)] [string] $User,
  [Parameter(Mandatory=$false)] [int] $Port = 22,
  [Parameter(Mandatory=$false)] [string] $PrivateKey = '',
  [Parameter(Mandatory=$false)] [string] $RepoDir = '/srv/music-genre',
  [Parameter(Mandatory=$false)] [string] $ComposeFile = 'docker-compose.prod.yml'
)

function Build-SshCommand($cmd){
  if ($PrivateKey -ne ''){
    return "ssh -i `"$PrivateKey`" -p $Port $User@$Host -- $cmd"
  } else {
    return "ssh -p $Port $User@$Host -- $cmd"
  }
}

$remoteCmd = @"
set -e
cd $RepoDir || exit 2
git fetch --all
git reset --hard origin/main
if [ -f $ComposeFile ]; then
  docker compose -f $ComposeFile pull || true
  docker compose -f $ComposeFile up -d --build
else
  echo "$ComposeFile not found in $RepoDir"
  exit 3
fi
"@

$sshCmd = Build-SshCommand($remoteCmd)

Write-Host "Running remote deploy to $User@$Host (port $Port) using repo dir $RepoDir"
Write-Host "Command: $sshCmd"

# Execute the ssh command
Invoke-Expression $sshCmd
