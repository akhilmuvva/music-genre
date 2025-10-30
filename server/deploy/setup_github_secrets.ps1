<#
.SYNOPSIS
  Set required GitHub repository secrets for CI/CD using the gh CLI.

USAGE
  From PowerShell (you must have gh CLI installed and be authenticated):
    ./setup_github_secrets.ps1 -RepoOwner akhilmuvva -RepoName music-genre -SshPrivateKeyPath C:\path\to\id_rsa

DESCRIPTION
  This script sets a standard list of secrets used by the GitHub Actions deploy workflow.
  It uses `gh secret set` and will prompt if required values are missing.
#>

param(
  [Parameter(Mandatory=$true)] [string] $RepoOwner,
  [Parameter(Mandatory=$true)] [string] $RepoName,
  [Parameter(Mandatory=$false)] [string] $SshPrivateKeyPath
)

function Set-SecretInteractive($name, $value){
  if ([string]::IsNullOrWhiteSpace($value)){
    Write-Host "Enter value for $name (empty to skip): " -NoNewline
    $val = Read-Host
  } else { $val = $value }
  if (-not [string]::IsNullOrWhiteSpace($val)){
    gh secret set $name --body "$val" --repo "$RepoOwner/$RepoName"
  } else {
    Write-Host "Skipped $name"
  }
}

# Ensure gh is available
if (-not (Get-Command gh -ErrorAction SilentlyContinue)){
  Write-Error "gh CLI not found. Install from https://cli.github.com/."; exit 1
}

$repo = "$RepoOwner/$RepoName"

Write-Host "Will set secrets for repository: $repo"

# Required secrets list
Set-SecretInteractive -name 'SSH_HOST' -value $null
Set-SecretInteractive -name 'SSH_PORT' -value '22'
Set-SecretInteractive -name 'SSH_USER' -value $null

if ($SshPrivateKeyPath -and (Test-Path $SshPrivateKeyPath)){
  gh secret set SSH_PRIVATE_KEY --body-file $SshPrivateKeyPath --repo $repo
} else {
  Set-SecretInteractive -name 'SSH_PRIVATE_KEY' -value $null
}

Set-SecretInteractive -name 'REPO_DIR' -value '/srv/music-genre'
Set-SecretInteractive -name 'SERVER_API_TOKEN' -value $null
Set-SecretInteractive -name 'REACT_APP_API_TOKEN' -value $null
Set-SecretInteractive -name 'GHCR_OWNER' -value $RepoOwner
Set-SecretInteractive -name 'GHCR_PAT' -value $null

Write-Host "Secrets setup complete. Review Secrets in GitHub repo settings to confirm."
