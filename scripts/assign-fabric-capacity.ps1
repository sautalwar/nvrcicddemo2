# Assign Fabric Capacity to Workspaces
# This script automates assigning a Fabric/Power BI capacity to multiple workspaces

param(
    [Parameter(Mandatory=$true)]
    [string]$TenantId,
    
    [Parameter(Mandatory=$true)]
    [string]$CapacityId,
    
    [Parameter(Mandatory=$true)]
    [string[]]$WorkspaceIds
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Fabric Capacity Assignment Automation" -ForegroundColor Cyan
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

# Verify capacity exists
Write-Host "Verifying capacity: $CapacityId" -ForegroundColor Cyan
try {
    $capacity = Get-PowerBICapacity -Scope Organization | Where-Object { $_.Id -eq $CapacityId }
    if ($null -eq $capacity) {
        Write-Host "❌ Capacity not found: $CapacityId" -ForegroundColor Red
        Write-Host "Available capacities:" -ForegroundColor Yellow
        Get-PowerBICapacity -Scope Organization | ForEach-Object {
            Write-Host "  - $($_.DisplayName) (ID: $($_.Id))" -ForegroundColor Gray
        }
        Disconnect-PowerBIServiceAccount
        exit 1
    }
    Write-Host "  ✅ Capacity found: $($capacity.DisplayName)" -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Host "❌ Error verifying capacity: $($_.Exception.Message)" -ForegroundColor Red
    Disconnect-PowerBIServiceAccount
    exit 1
}

# Function to assign capacity to workspace
function Set-WorkspaceCapacity {
    param(
        [string]$WorkspaceId,
        [string]$CapacityObjectId
    )
    
    try {
        Write-Host "Processing workspace: $WorkspaceId" -ForegroundColor Cyan
        
        # Get workspace details
        $workspace = Get-PowerBIWorkspace -Id $WorkspaceId
        Write-Host "  Workspace Name: $($workspace.Name)" -ForegroundColor Gray
        
        # Check current capacity
        if ($workspace.CapacityId) {
            Write-Host "  Current Capacity: $($workspace.CapacityId)" -ForegroundColor Gray
            
            # Check if already assigned to the target capacity
            if ($workspace.CapacityId -eq $CapacityObjectId) {
                Write-Host "  ℹ️  Already assigned to this capacity - skipping" -ForegroundColor Yellow
                return "skipped"
            }
        } else {
            Write-Host "  Current Capacity: None (Shared)" -ForegroundColor Gray
        }
        
        # Assign capacity using REST API
        $url = "https://api.powerbi.com/v1.0/myorg/groups/$WorkspaceId/AssignToCapacity"
        $body = @{
            capacityId = $CapacityObjectId
        } | ConvertTo-Json
        
        Invoke-PowerBIRestMethod -Url $url -Method Post -Body $body
        
        Write-Host "  ✅ Successfully assigned capacity" -ForegroundColor Green
        return "success"
    }
    catch {
        Write-Host "  ❌ Failed to assign capacity: $($_.Exception.Message)" -ForegroundColor Red
        return "failed"
    }
}

# Process each workspace
$successCount = 0
$failCount = 0
$skippedCount = 0

Write-Host "Assigning capacity to workspaces..." -ForegroundColor Yellow
Write-Host ""

foreach ($workspaceId in $WorkspaceIds) {
    $result = Set-WorkspaceCapacity -WorkspaceId $workspaceId -CapacityObjectId $CapacityId
    switch ($result) {
        "success" { $successCount++ }
        "failed" { $failCount++ }
        "skipped" { $skippedCount++ }
    }
    Write-Host ""
}

# Summary
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Capacity: $($capacity.DisplayName)" -ForegroundColor White
Write-Host "Total Workspaces: $($WorkspaceIds.Count)" -ForegroundColor White
Write-Host "Newly Assigned: $successCount" -ForegroundColor Green
Write-Host "Already Assigned: $skippedCount" -ForegroundColor Yellow
Write-Host "Failed: $failCount" -ForegroundColor Red
Write-Host ""

if ($failCount -eq 0 -and ($successCount -gt 0 -or $skippedCount -gt 0)) {
    if ($skippedCount -eq $WorkspaceIds.Count) {
        Write-Host "ℹ️  All workspaces already assigned to this capacity!" -ForegroundColor Yellow
    } else {
        Write-Host "✅ All workspaces configured successfully!" -ForegroundColor Green
    }
} elseif ($failCount -eq 0 -and $successCount -eq 0 -and $skippedCount -eq 0) {
    Write-Host "⚠️ No workspaces processed." -ForegroundColor Yellow
} else {
    Write-Host "⚠️ Some workspaces failed. Please check errors above." -ForegroundColor Yellow
}

# Disconnect
Disconnect-PowerBIServiceAccount
