# Script to retrieve Azure credentials for GitHub Actions
# Run this script to get all required values

Write-Host "🔍 Retrieving Azure Credentials..." -ForegroundColor Cyan
Write-Host ""

# Get Subscription ID
Write-Host "📋 AZURE_SUBSCRIPTION_ID:" -ForegroundColor Yellow
$subscriptionId = az account show --query id -o tsv
Write-Host $subscriptionId -ForegroundColor Green
Write-Host ""

# Get Tenant ID
Write-Host "📋 AZURE_TENANT_ID:" -ForegroundColor Yellow
$tenantId = az account show --query tenantId -o tsv
Write-Host $tenantId -ForegroundColor Green
Write-Host ""

# Check if service principal exists
Write-Host "🔍 Checking for existing service principal..." -ForegroundColor Cyan
$spName = "github-actions-fabric-cicd"
$existingSp = az ad sp list --display-name $spName --query "[0].appId" -o tsv 2>$null

if ($existingSp) {
    Write-Host "✅ Found existing service principal" -ForegroundColor Green
    Write-Host "📋 AZURE_CLIENT_ID:" -ForegroundColor Yellow
    Write-Host $existingSp -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  You'll need to create a new client secret in Azure Portal:" -ForegroundColor Yellow
    Write-Host "   1. Go to Azure Portal → Microsoft Entra ID → App registrations" -ForegroundColor White
    Write-Host "   2. Search for: $spName" -ForegroundColor White
    Write-Host "   3. Click 'Certificates & secrets' → '+ New client secret'" -ForegroundColor White
    Write-Host "   4. Copy the secret value (AZURE_CLIENT_SECRET)" -ForegroundColor White
} else {
    Write-Host "📝 Creating new service principal..." -ForegroundColor Cyan
    
    # Create service principal
    $sp = az ad sp create-for-rbac `
        --name $spName `
        --role Reader `
        --scopes "/subscriptions/$subscriptionId" `
        --query "{clientId:appId, clientSecret:password, tenantId:tenant}" `
        -o json | ConvertFrom-Json
    
    Write-Host "✅ Service principal created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 AZURE_CLIENT_ID:" -ForegroundColor Yellow
    Write-Host $sp.clientId -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 AZURE_CLIENT_SECRET:" -ForegroundColor Yellow
    Write-Host $sp.clientSecret -ForegroundColor Red
    Write-Host "⚠️  SAVE THIS SECRET NOW - You won't see it again!" -ForegroundColor Red
    Write-Host ""
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📝 Summary - Add these to GitHub Secrets:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "AZURE_SUBSCRIPTION_ID = $subscriptionId" -ForegroundColor White
Write-Host "AZURE_TENANT_ID       = $tenantId" -ForegroundColor White
if ($existingSp) {
    Write-Host "AZURE_CLIENT_ID       = $existingSp" -ForegroundColor White
    Write-Host "AZURE_CLIENT_SECRET   = <create new secret in portal>" -ForegroundColor Yellow
} else {
    Write-Host "AZURE_CLIENT_ID       = $($sp.clientId)" -ForegroundColor White
    Write-Host "AZURE_CLIENT_SECRET   = $($sp.clientSecret)" -ForegroundColor White
}
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔗 Next: Get Fabric Workspace IDs" -ForegroundColor Cyan
Write-Host "   Run: .\scripts\get-fabric-workspace-ids.ps1" -ForegroundColor White
Write-Host ""
