# Create Fabric Workspaces using REST API
# This script creates three workspaces (Dev, Test, Prod) for CI/CD demo

param(
    [Parameter(Mandatory=$false)]
    [string]$TenantId,
    
    [Parameter(Mandatory=$false)]
    [string]$WorkspacePrefix = "NVR",
    
    [Parameter(Mandatory=$false)]
    [string]$CapacityId,
    
    [Parameter(Mandatory=$false)]
    [string]$Description = "Workspace for Fabric CI/CD Demo"
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Fabric Workspace Creation" -ForegroundColor Cyan
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

# Define workspace names
$workspaces = @(
    @{
        Name = "$WorkspacePrefix-Dev1"
        Description = "$Description - Development Environment"
    },
    @{
        Name = "$WorkspacePrefix-Test1"
        Description = "$Description - Test Environment"
    },
    @{
        Name = "$WorkspacePrefix-Production1"
        Description = "$Description - Production Environment"
    }
)

# Function to create workspace
function New-FabricWorkspace {
    param(
        [string]$Name,
        [string]$Description
    )
    
    try {
        Write-Host "Creating workspace: $Name" -ForegroundColor Cyan
        
        # Check if workspace already exists
        $existing = Get-PowerBIWorkspace -Scope Organization -Filter "name eq '$Name'" -First 1
        
        if ($existing) {
            Write-Host "  ⚠️  Workspace '$Name' already exists" -ForegroundColor Yellow
            Write-Host "  Workspace ID: $($existing.Id)" -ForegroundColor Gray
            return @{
                Status = "exists"
                WorkspaceId = $existing.Id
                Name = $Name
            }
        }
        
        # Create workspace using REST API
        $url = "https://api.powerbi.com/v1.0/myorg/groups"
        $body = @{
            name = $Name
            description = $Description
        } | ConvertTo-Json
        
        $response = Invoke-PowerBIRestMethod -Url $url -Method Post -Body $body | ConvertFrom-Json
        
        Write-Host "  ✅ Workspace created successfully" -ForegroundColor Green
        Write-Host "  Workspace ID: $($response.id)" -ForegroundColor Gray
        
        return @{
            Status = "created"
            WorkspaceId = $response.id
            Name = $Name
        }
    }
    catch {
        Write-Host "  ❌ Failed to create workspace: $($_.Exception.Message)" -ForegroundColor Red
        return @{
            Status = "failed"
            WorkspaceId = $null
            Name = $Name
            Error = $_.Exception.Message
        }
    }
}

# Function to assign capacity to workspace
function Set-WorkspaceCapacity {
    param(
        [string]$WorkspaceId,
        [string]$CapacityObjectId,
        [string]$WorkspaceName
    )
    
    try {
        Write-Host "  Assigning capacity to $WorkspaceName..." -ForegroundColor Cyan
        
        $url = "https://api.powerbi.com/v1.0/myorg/groups/$WorkspaceId/AssignToCapacity"
        $body = @{
            capacityId = $CapacityObjectId
        } | ConvertTo-Json
        
        Invoke-PowerBIRestMethod -Url $url -Method Post -Body $body
        
        Write-Host "  ✅ Capacity assigned" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "  ⚠️ Failed to assign capacity: $($_.Exception.Message)" -ForegroundColor Yellow
        return $false
    }
}

# Create workspaces
$results = @()
$createdCount = 0
$existsCount = 0
$failedCount = 0

Write-Host "Creating workspaces..." -ForegroundColor Yellow
Write-Host ""

foreach ($ws in $workspaces) {
    $result = New-FabricWorkspace -Name $ws.Name -Description $ws.Description
    $results += $result
    
    switch ($result.Status) {
        "created" { 
            $createdCount++
            
            # Assign capacity if provided
            if ($CapacityId -and $result.WorkspaceId) {
                Start-Sleep -Seconds 2  # Brief delay to ensure workspace is ready
                Set-WorkspaceCapacity -WorkspaceId $result.WorkspaceId `
                                     -CapacityObjectId $CapacityId `
                                     -WorkspaceName $result.Name
            }
        }
        "exists" { 
            $existsCount++
            
            # Assign capacity if provided and workspace exists
            if ($CapacityId -and $result.WorkspaceId) {
                Set-WorkspaceCapacity -WorkspaceId $result.WorkspaceId `
                                     -CapacityObjectId $CapacityId `
                                     -WorkspaceName $result.Name
            }
        }
        "failed" { $failedCount++ }
    }
    
    Write-Host ""
}

# Summary
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Total Workspaces: $($workspaces.Count)" -ForegroundColor White
Write-Host "Created: $createdCount" -ForegroundColor Green
Write-Host "Already Existed: $existsCount" -ForegroundColor Yellow
Write-Host "Failed: $failedCount" -ForegroundColor Red
Write-Host ""

# Display workspace IDs
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Workspace IDs (for GitHub Secrets)" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

foreach ($result in $results) {
    if ($result.WorkspaceId) {
        $envName = $result.Name -replace ".*-", ""  # Extract Dev/Test/Production
        $secretName = "FABRIC_$($envName.ToUpper())_WORKSPACE_ID"
        Write-Host "$secretName=$($result.WorkspaceId)" -ForegroundColor Green
    }
}
Write-Host ""

# Output workspace IDs to a file for easy reference
$outputFile = Join-Path $PSScriptRoot "..\workspace-ids.txt"
$results | Where-Object { $_.WorkspaceId } | ForEach-Object {
    $envName = $_.Name -replace ".*-", ""
    "FABRIC_$($envName.ToUpper())_WORKSPACE_ID=$($_.WorkspaceId)"
} | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "✅ Workspace IDs saved to: $outputFile" -ForegroundColor Green
Write-Host ""

if ($failedCount -eq 0) {
    Write-Host "✅ All workspaces configured successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Copy the workspace IDs above" -ForegroundColor Gray
    Write-Host "2. Add them as GitHub secrets in your repository" -ForegroundColor Gray
    Write-Host "3. Run grant-workspace-access.ps1 to add service principal access" -ForegroundColor Gray
} else {
    Write-Host "⚠️ Some workspaces failed. Please check errors above." -ForegroundColor Yellow
}

# Disconnect
Disconnect-PowerBIServiceAccount
