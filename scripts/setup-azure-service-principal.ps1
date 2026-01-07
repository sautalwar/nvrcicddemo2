# Setup Azure Service Principal for Fabric CI/CD
# This script creates a service principal with proper permissions for Microsoft Fabric deployments
# Usage: pwsh scripts/setup-azure-service-principal.ps1 -AppName "FabricCICD-Demo"

param(
    [Parameter(Mandatory=$false)]
    [string]$AppName = "FabricCICD-Demo",
    
    [Parameter(Mandatory=$false)]
    [switch]$CheckOnly
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Azure Service Principal Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if Azure CLI is installed and authenticated
try {
    $account = az account show 2>$null | ConvertFrom-Json
    if (-not $account) {
        Write-Host "❌ Not logged into Azure CLI. Please run: az login" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Logged in as: $($account.user.name)" -ForegroundColor Green
    Write-Host "   Subscription: $($account.name) ($($account.id))" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "❌ Azure CLI not found or not authenticated. Please run: az login" -ForegroundColor Red
    exit 1
}

# Check existing app registrations
Write-Host "Checking existing app registrations..." -ForegroundColor Yellow
$existingApps = az ad app list --show-mine --query "[].{DisplayName:displayName, AppId:appId}" -o json | ConvertFrom-Json

if ($existingApps.Count -gt 0) {
    Write-Host "`nFound $($existingApps.Count) existing app registration(s):" -ForegroundColor Cyan
    $existingApps | ForEach-Object {
        Write-Host "  - $($_.DisplayName) (AppId: $($_.AppId))" -ForegroundColor White
    }
} else {
    Write-Host "  No app registrations found" -ForegroundColor Gray
}

if ($CheckOnly) {
    Write-Host "`n✅ Check complete" -ForegroundColor Green
    exit 0
}

# Check if app with same name exists
$existingApp = $existingApps | Where-Object { $_.DisplayName -eq $AppName }
if ($existingApp) {
    Write-Host "`n⚠️  App registration '$AppName' already exists (AppId: $($existingApp.AppId))" -ForegroundColor Yellow
    $choice = Read-Host "Do you want to (C)reate new, (R)euse existing, or (Q)uit? [C/R/Q]"
    
    if ($choice -eq 'Q' -or $choice -eq 'q') {
        Write-Host "Exiting..." -ForegroundColor Gray
        exit 0
    } elseif ($choice -eq 'R' -or $choice -eq 'r') {
        $appId = $existingApp.AppId
        Write-Host "✅ Reusing existing app: $appId" -ForegroundColor Green
        
        # Get or create client secret
        Write-Host "`nCreating new client secret (previous secrets remain valid)..." -ForegroundColor Yellow
        $secretOutput = az ad app credential reset --id $appId --append --display-name "CICD-$(Get-Date -Format 'yyyyMMdd-HHmmss')" -o json | ConvertFrom-Json
        $clientSecret = $secretOutput.password
        
        Write-Host "✅ New secret created" -ForegroundColor Green
    } else {
        $AppName = "$AppName-$(Get-Date -Format 'yyyyMMddHHmmss')"
        Write-Host "Creating new app with name: $AppName" -ForegroundColor Cyan
    }
}

if (-not $appId) {
    # Create new app registration
    Write-Host "`nCreating new app registration: $AppName..." -ForegroundColor Yellow
    $app = az ad app create --display-name $AppName -o json | ConvertFrom-Json
    $appId = $app.appId
    Write-Host "✅ App created: $appId" -ForegroundColor Green

    # Create service principal
    Write-Host "Creating service principal..." -ForegroundColor Yellow
    az ad sp create --id $appId | Out-Null
    Start-Sleep -Seconds 3
    Write-Host "✅ Service principal created" -ForegroundColor Green

    # Create client secret
    Write-Host "Creating client secret..." -ForegroundColor Yellow
    $secretOutput = az ad app credential reset --id $appId --display-name "CICD-Secret" -o json | ConvertFrom-Json
    $clientSecret = $secretOutput.password
    Write-Host "✅ Client secret created" -ForegroundColor Green
}

# Assign Contributor role at subscription level
Write-Host "`nAssigning Contributor role to service principal..." -ForegroundColor Yellow
try {
    az role assignment create --assignee $appId --role "Contributor" --scope "/subscriptions/$($account.id)" 2>$null | Out-Null
    Write-Host "✅ Contributor role assigned" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Role may already be assigned or insufficient permissions" -ForegroundColor Yellow
}

# Output summary
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Service Principal Details" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "App Name:        $AppName" -ForegroundColor White
Write-Host "Client ID:       $appId" -ForegroundColor White
Write-Host "Tenant ID:       $($account.tenantId)" -ForegroundColor White
Write-Host "Subscription ID: $($account.id)" -ForegroundColor White
if ($clientSecret) {
    Write-Host "`n⚠️  CLIENT SECRET (save this now - it won't be shown again):" -ForegroundColor Yellow
    Write-Host $clientSecret -ForegroundColor Red
}
Write-Host ""

# Ask if user wants to set GitHub secrets
$setSecrets = Read-Host "`nDo you want to set these as GitHub secrets now? [Y/N]"
if ($setSecrets -eq 'Y' -or $setSecrets -eq 'y') {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Write-Host "❌ GitHub CLI 'gh' not found" -ForegroundColor Red
        exit 1
    }
    
    $owner = Read-Host "GitHub Owner (e.g., sautalwar)"
    $repo = Read-Host "GitHub Repo (e.g., nvrcicddemo1)"
    $repoRef = "$owner/$repo"
    
    Write-Host "`nSetting GitHub secrets for $repoRef..." -ForegroundColor Yellow
    gh secret set AZURE_CLIENT_ID -R $repoRef -b $appId
    if ($clientSecret) {
        gh secret set AZURE_CLIENT_SECRET -R $repoRef -b $clientSecret
    }
    gh secret set AZURE_TENANT_ID -R $repoRef -b $account.tenantId
    gh secret set AZURE_SUBSCRIPTION_ID -R $repoRef -b $account.id
    
    Write-Host "✅ GitHub secrets updated" -ForegroundColor Green
}

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Grant this service principal Admin access to your Fabric workspaces" -ForegroundColor White
Write-Host "   pwsh scripts/grant-workspace-access.ps1 -ServicePrincipalId $appId" -ForegroundColor Gray
Write-Host "2. Verify workspace IDs are set correctly in GitHub secrets" -ForegroundColor White
Write-Host "3. Run your CI/CD pipeline" -ForegroundColor White
