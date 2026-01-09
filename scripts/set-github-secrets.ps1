# Set GitHub repository and environment secrets for Fabric CI/CD
# Requires: GitHub CLI (gh) and an authenticated session: gh auth login
# 
# SECURITY NOTE: This script does NOT contain hardcoded secrets.
# All sensitive values must be passed as parameters or entered interactively.
# See README.md for proper usage instructions.

param(
    [Parameter(Mandatory=$true)]
    [string]$Owner,

    [Parameter(Mandatory=$true)]
    [string]$Repo,

    [Parameter(Mandatory=$false)]
    [string]$AzureClientId,

    [Parameter(Mandatory=$false)]
    [SecureString]$AzureClientSecret,

    [Parameter(Mandatory=$false)]
    [string]$AzureTenantId,

    [Parameter(Mandatory=$false)]
    [string]$AzureSubscriptionId,

    [Parameter(Mandatory=$false)]
    [string]$FabricDevWorkspaceId,

    [Parameter(Mandatory=$false)]
    [string]$FabricTestWorkspaceId,

    [Parameter(Mandatory=$false)]
    [string]$FabricProdWorkspaceId,

    [Parameter(Mandatory=$false)]
    [switch]$AlsoSetEnvironmentSecrets,

    [Parameter(Mandatory=$false)]
    [switch]$SecurePrompt = $true,

    [Parameter(Mandatory=$false)]
    [string]$WorkspaceIdsFile = "workspace-ids.txt"
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "GitHub Secrets Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Validate gh
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "❌ GitHub CLI 'gh' is not installed." -ForegroundColor Red
    Write-Host "Install from: https://cli.github.com/ and run 'gh auth login'" -ForegroundColor Yellow
    exit 1
}

# Check auth status
try {
    gh auth status | Out-Null
} catch {
    Write-Host "🔐 Authenticating GitHub CLI..." -ForegroundColor Yellow
    gh auth login
}

$repoRef = "$Owner/$Repo"
Write-Host "📦 Target repository: $repoRef" -ForegroundColor Cyan

# If workspace IDs not provided, try reading from file
if (-not $FabricDevWorkspaceId -or -not $FabricTestWorkspaceId -or -not $FabricProdWorkspaceId) {
    $path = Join-Path -Path (Get-Location) -ChildPath $WorkspaceIdsFile
    if (Test-Path $path) {
        Write-Host "📄 Reading workspace IDs from $path" -ForegroundColor Gray
        $content = Get-Content $path | Where-Object { $_ -match "FABRIC_.*_WORKSPACE_ID=" }
        foreach ($line in $content) {
            $parts = $line.Split('=')
            if ($parts.Length -eq 2) {
                switch -Regex ($parts[0]) {
                    'FABRIC_DEV_WORKSPACE_ID' { $FabricDevWorkspaceId = $parts[1] }
                    'FABRIC_TEST_WORKSPACE_ID' { $FabricTestWorkspaceId = $parts[1] }
                    'FABRIC_PRODUCTION_WORKSPACE_ID' { $FabricProdWorkspaceId = $parts[1] }
                    'FABRIC_PROD_WORKSPACE_ID' { $FabricProdWorkspaceId = $parts[1] }
                }
            }
        }
    }
}

# If SecurePrompt enabled, interactively and securely collect any missing sensitive values
function Get-PlainFromSecure {
    param([System.Security.SecureString]$Secure)
    return (New-Object System.Net.NetworkCredential("", $Secure)).Password
}

# Always use secure prompt for missing credentials to prevent accidental exposure
if (-not $AzureClientId) {
    $s = Read-Host -AsSecureString "Enter AZURE_CLIENT_ID"
    $AzureClientId = Get-PlainFromSecure -Secure $s
}
if (-not $AzureClientSecret) {
    $s = Read-Host -AsSecureString "Enter AZURE_CLIENT_SECRET"
    $AzureClientSecretPlain = Get-PlainFromSecure -Secure $s
} else {
    $AzureClientSecretPlain = Get-PlainFromSecure -Secure $AzureClientSecret
}
if (-not $AzureTenantId) {
    $s = Read-Host -AsSecureString "Enter AZURE_TENANT_ID"
    $AzureTenantId = Get-PlainFromSecure -Secure $s
}
if (-not $AzureSubscriptionId) {
    $s = Read-Host -AsSecureString "Enter AZURE_SUBSCRIPTION_ID"
    $AzureSubscriptionId = Get-PlainFromSecure -Secure $s
}

# Helper to set a secret
function Set-RepoSecret {
    param(
        [string]$Name,
        [string]$Value
    )
    if (-not $Value) {
        Write-Host "⚠️ Skipping secret '$Name' (no value provided)" -ForegroundColor Yellow
        return
    }
    Write-Host "🔑 Setting secret: $Name" -ForegroundColor Green
    # IMPORTANT: Do not echo or persist values. Pass via GH CLI directly.
    gh secret set $Name -R $repoRef -b $Value | Out-Null
}

# Helper to set environment secret
function Set-EnvSecret {
    param(
        [string]$EnvName,
        [string]$Name,
        [string]$Value
    )
    if (-not $Value) { return }
    Write-Host "🔒 Setting environment secret: $EnvName/$Name" -ForegroundColor Green
    gh secret set $Name -R $repoRef -e $EnvName -b $Value | Out-Null
}

# Repository-level secrets
Set-RepoSecret -Name 'AZURE_CLIENT_ID' -Value $AzureClientIdPlain
Set-RepoSecret -Name 'AZURE_CLIENT_SECRET' -Value $AzureClientSecret
Set-RepoSecret -Name 'AZURE_TENANT_ID' -Value $AzureTenantId
Set-RepoSecret -Name 'AZURE_SUBSCRIPTION_ID' -Value $AzureSubscriptionId
Set-RepoSecret -Name 'FABRIC_DEV_WORKSPACE_ID' -Value $FabricDevWorkspaceId
Set-RepoSecret -Name 'FABRIC_TEST_WORKSPACE_ID' -Value $FabricTestWorkspaceId
# Prefer FABRIC_PROD_WORKSPACE_ID, but accept PRODUCTION alias
if ($FabricProdWorkspaceId) {
    Set-RepoSecret -Name 'FABRIC_PROD_WORKSPACE_ID' -Value $FabricProdWorkspaceId
}

# Optional: mirror as environment secrets for finer-grained control
if ($AlsoSetEnvironmentSecrets) {
    Set-EnvSecret -EnvName 'development' -Name 'FABRIC_WORKSPACE_ID' -Value $FabricDevWorkspaceId
    Set-EnvSecret -EnvName 'test' -Name 'FABRIC_WORKSPACE_ID' -Value $FabricTestWorkspaceId
    Set-EnvSecret -EnvName 'production' -Name 'FABRIC_WORKSPACE_ID' -Value $FabricProdWorkspaceId
    Set-EnvSecret -EnvName 'production' -Name 'AZURE_CLIENT_ID' -Value $AzureClientId
    Set-EnvSecret -EnvName 'production' -Name 'AZURE_CLIENT_SECRET' -Value $AzureClientSecretPlain
    Set-EnvSecret -EnvName 'production' -Name 'AZURE_TENANT_ID' -Value $AzureTenantId
    Set-EnvSecret -EnvName 'production' -Name 'AZURE_SUBSCRIPTION_ID' -Value $AzureSubscriptionId
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "✅ Secrets configured for $repoRef" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
