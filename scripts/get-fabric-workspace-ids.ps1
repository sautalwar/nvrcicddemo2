# Script to retrieve Fabric Workspace IDs
# Run this after setting up Azure credentials

Write-Host "🔍 Retrieving Fabric Workspace IDs..." -ForegroundColor Cyan
Write-Host ""

# Check if authenticated
Write-Host "🔐 Authenticating to Azure..." -ForegroundColor Cyan
az login --use-device-code 2>$null | Out-Null

# Get Fabric token
Write-Host "🎫 Getting Fabric access token..." -ForegroundColor Cyan
$token = az account get-access-token --resource https://analysis.windows.net/powerbi/api --query accessToken -o tsv

if (-not $token) {
    Write-Host "❌ Failed to get Fabric token. Please ensure you're logged in to Azure." -ForegroundColor Red
    exit 1
}

# Call Fabric API to list workspaces
Write-Host "📂 Fetching your Fabric workspaces..." -ForegroundColor Cyan
Write-Host ""

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces" -Headers $headers -Method Get
    
    if ($response.value.Count -eq 0) {
        Write-Host "⚠️  No workspaces found. Please create workspaces in Fabric first." -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host "✅ Found $($response.value.Count) workspace(s):" -ForegroundColor Green
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($workspace in $response.value) {
        Write-Host "📁 Workspace Name: " -NoNewline -ForegroundColor Yellow
        Write-Host $workspace.displayName -ForegroundColor White
        Write-Host "   Workspace ID:   " -NoNewline -ForegroundColor Yellow
        Write-Host $workspace.id -ForegroundColor Green
        Write-Host "   Type:           " -NoNewline -ForegroundColor Yellow
        Write-Host $workspace.type -ForegroundColor White
        Write-Host ""
    }
    
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📝 Identify your environment workspaces and add to GitHub Secrets:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   FABRIC_DEV_WORKSPACE_ID  = <copy ID of your DEV workspace>" -ForegroundColor White
    Write-Host "   FABRIC_TEST_WORKSPACE_ID = <copy ID of your TEST workspace>" -ForegroundColor White
    Write-Host "   FABRIC_PROD_WORKSPACE_ID = <copy ID of your PROD workspace>" -ForegroundColor White
    Write-Host ""
    
    # If user has workspaces with obvious names
    $devWs = $response.value | Where-Object { $_.displayName -like "*dev*" -or $_.displayName -like "*Dev*" }
    $testWs = $response.value | Where-Object { $_.displayName -like "*test*" -or $_.displayName -like "*Test*" }
    $prodWs = $response.value | Where-Object { $_.displayName -like "*prod*" -or $_.displayName -like "*Prod*" -or $_.displayName -like "*Production*" }
    
    if ($devWs -or $testWs -or $prodWs) {
        Write-Host "💡 Suggested mappings based on workspace names:" -ForegroundColor Yellow
        Write-Host ""
        if ($devWs) {
            Write-Host "   DEV:  $($devWs.displayName) → $($devWs.id)" -ForegroundColor Green
        }
        if ($testWs) {
            Write-Host "   TEST: $($testWs.displayName) → $($testWs.id)" -ForegroundColor Green
        }
        if ($prodWs) {
            Write-Host "   PROD: $($prodWs.displayName) → $($prodWs.id)" -ForegroundColor Green
        }
        Write-Host ""
    }
    
} catch {
    Write-Host "❌ Error calling Fabric API: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Alternative: Get Workspace IDs from Fabric Portal URLs" -ForegroundColor Yellow
    Write-Host "   1. Go to app.fabric.microsoft.com" -ForegroundColor White
    Write-Host "   2. Click on a workspace" -ForegroundColor White
    Write-Host "   3. The URL will look like: https://app.fabric.microsoft.com/groups/WORKSPACE-ID/..." -ForegroundColor White
    Write-Host "   4. Copy the WORKSPACE-ID from the URL" -ForegroundColor White
}

Write-Host ""
Write-Host "🔗 Next: Add all secrets to GitHub" -ForegroundColor Cyan
Write-Host "   Go to: https://github.com/sautalwar/nvrfabricdemo1/settings/secrets/actions" -ForegroundColor White
Write-Host ""
