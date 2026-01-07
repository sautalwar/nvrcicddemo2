# Get all available Fabric/Power BI capacities
# Helper script to list available capacities and their IDs

param(
    [Parameter(Mandatory=$false)]
    [string]$TenantId
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Available Fabric Capacities" -ForegroundColor Cyan
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
if ($TenantId) {
    Connect-PowerBIServiceAccount -Tenant $TenantId
} else {
    Connect-PowerBIServiceAccount
}
Write-Host ""

# Get all capacities
try {
    $capacities = Get-PowerBICapacity -Scope Organization
    
    if ($capacities.Count -eq 0) {
        Write-Host "⚠️ No capacities found in this tenant" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To create a Fabric capacity:" -ForegroundColor Cyan
        Write-Host "1. Go to Azure Portal" -ForegroundColor Gray
        Write-Host "2. Create a 'Microsoft Fabric' resource" -ForegroundColor Gray
        Write-Host "3. Or use Power BI Premium capacity" -ForegroundColor Gray
    } else {
        Write-Host "Found $($capacities.Count) capacity/capacities:" -ForegroundColor Green
        Write-Host ""
        
        foreach ($capacity in $capacities) {
            Write-Host "Capacity Name: $($capacity.DisplayName)" -ForegroundColor Cyan
            Write-Host "  ID: $($capacity.Id)" -ForegroundColor White
            Write-Host "  SKU: $($capacity.Sku)" -ForegroundColor Gray
            Write-Host "  State: $($capacity.State)" -ForegroundColor Gray
            Write-Host "  Region: $($capacity.Region)" -ForegroundColor Gray
            
            # Get workspaces in this capacity
            $workspacesInCapacity = Get-PowerBIWorkspace -Scope Organization | 
                Where-Object { $_.CapacityId -eq $capacity.Id }
            Write-Host "  Workspaces: $($workspacesInCapacity.Count)" -ForegroundColor Gray
            
            Write-Host ""
        }
        
        Write-Host "=====================================" -ForegroundColor Cyan
        Write-Host "Copy the Capacity ID to use in assign-fabric-capacity.ps1" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Error retrieving capacities: $($_.Exception.Message)" -ForegroundColor Red
}

# Disconnect
Disconnect-PowerBIServiceAccount
