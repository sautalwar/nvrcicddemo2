# Grant Service Principal access to Fabric Workspaces
# This script automates adding a service principal as Admin to multiple Fabric workspaces

param(
    [Parameter(Mandatory=$true)]
    [string]$ServicePrincipalId,
    
    [Parameter(Mandatory=$true)]
    [string]$TenantId,
    
    [Parameter(Mandatory=$true)]
    [string[]]$WorkspaceIds,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("Admin", "Contributor", "Member", "Viewer")]
    [string]$Role = "Admin"
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Fabric Workspace Access Automation" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Install required module if not present
if (-not (Get-Module -ListAvailable -Name MicrosoftPowerBIMgmt)) {
    Write-Host "Installing MicrosoftPowerBIMgmt module..." -ForegroundColor Yellow
    Install-Module -Name MicrosoftPowerBIMgmt -Scope CurrentUser -Force -AllowClobber
}

# Import module
Import-Module MicrosoftPowerBIMgmt

# Connect to Power BI Service
Write-Host "Connecting to Power BI Service..." -ForegroundColor Green
Connect-PowerBIServiceAccount -Tenant $TenantId

# Function to add service principal to workspace
function Add-ServicePrincipalToWorkspace {
    param(
        [string]$WorkspaceId,
        [string]$PrincipalId,
        [string]$AccessRight
    )
    
    try {
        Write-Host "Processing workspace: $WorkspaceId" -ForegroundColor Cyan
        
        # Get workspace details
        $workspace = Get-PowerBIWorkspace -Id $WorkspaceId
        Write-Host "  Workspace Name: $($workspace.Name)" -ForegroundColor Gray
        
        # Add service principal
        Add-PowerBIWorkspaceUser -Scope Organization `
            -Id $WorkspaceId `
            -PrincipalType App `
            -Identifier $PrincipalId `
            -AccessRight $AccessRight
        
        Write-Host "  ✅ Successfully added service principal with $AccessRight access" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "  ❌ Failed to add service principal: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Process each workspace
$successCount = 0
$failCount = 0

Write-Host ""
Write-Host "Adding service principal to workspaces..." -ForegroundColor Yellow
Write-Host ""

foreach ($workspaceId in $WorkspaceIds) {
    $result = Add-ServicePrincipalToWorkspace -WorkspaceId $workspaceId `
                                              -PrincipalId $ServicePrincipalId `
                                              -AccessRight $Role
    if ($result) {
        $successCount++
    } else {
        $failCount++
    }
    Write-Host ""
}

# Summary
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Total Workspaces: $($WorkspaceIds.Count)" -ForegroundColor White
Write-Host "Successful: $successCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor Red
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "✅ All workspaces configured successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Some workspaces failed. Please check errors above." -ForegroundColor Yellow
}

# Disconnect
Disconnect-PowerBIServiceAccount
