# Deploy Fabric Deployment Pipeline
# This script deploys or triggers a Fabric deployment pipeline to promote artifacts across environments

param(
    [Parameter(Mandatory=$true)]
    [string]$WorkspaceId,
    
    [Parameter(Mandatory=$true)]
    [string]$PipelineName,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("Dev", "Test", "Production")]
    [string]$TargetStage = "Production",
    
    [Parameter(Mandatory=$false)]
    [string]$Note = "Automated deployment from GitHub Actions",
    
    [Parameter(Mandatory=$false)]
    [switch]$WaitForCompletion,
    
    [Parameter(Mandatory=$false)]
    [int]$TimeoutMinutes = 30
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Fabric Deployment Pipeline Trigger" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if running in GitHub Actions
$isGitHubActions = $env:GITHUB_ACTIONS -eq "true"

# Get access token
if ($isGitHubActions) {
    Write-Host "🔐 Running in GitHub Actions - using environment token" -ForegroundColor Cyan
    $token = $env:FABRIC_TOKEN
    
    if (-not $token) {
        Write-Host "❌ FABRIC_TOKEN environment variable not found" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "🔐 Getting Fabric access token..." -ForegroundColor Cyan
    
    # Install module if needed
    if (-not (Get-Module -ListAvailable -Name MicrosoftPowerBIMgmt)) {
        Install-Module -Name MicrosoftPowerBIMgmt -Scope CurrentUser -Force -AllowClobber
    }
    
    Import-Module MicrosoftPowerBIMgmt
    Connect-PowerBIServiceAccount
    
    $tokenObj = Invoke-PowerBIRestMethod -Url "https://api.powerbi.com/v1.0/myorg/" -Method Get
    # For local execution, we'll use the connection established
}

# Function to get deployment pipeline
function Get-DeploymentPipeline {
    param([string]$Name)
    
    try {
        $url = "https://api.powerbi.com/v1.0/myorg/pipelines"
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers
        $pipeline = $response.value | Where-Object { $_.displayName -eq $Name }
        
        return $pipeline
    }
    catch {
        Write-Host "❌ Error getting pipeline: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Function to trigger deployment
function Start-PipelineDeployment {
    param(
        [string]$PipelineId,
        [int]$SourceStageOrder,
        [int]$TargetStageOrder,
        [string]$DeploymentNote
    )
    
    try {
        $url = "https://api.powerbi.com/v1.0/myorg/pipelines/$PipelineId/deploy"
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        $body = @{
            sourceStageOrder = $SourceStageOrder
            isBackwardDeployment = $false
            note = $DeploymentNote
            options = @{
                allowCreateArtifact = $true
                allowOverwriteArtifact = $true
            }
        } | ConvertTo-Json
        
        Write-Host "📤 Triggering deployment..." -ForegroundColor Yellow
        Write-Host "  Source Stage: Order $SourceStageOrder" -ForegroundColor Gray
        Write-Host "  Target Stage: Order $TargetStageOrder" -ForegroundColor Gray
        
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body
        
        return $response
    }
    catch {
        Write-Host "❌ Error triggering deployment: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Function to check deployment status
function Get-DeploymentStatus {
    param(
        [string]$PipelineId,
        [string]$OperationId
    )
    
    try {
        $url = "https://api.powerbi.com/v1.0/myorg/pipelines/$PipelineId/operations/$OperationId"
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers
        return $response
    }
    catch {
        Write-Host "⚠️ Could not get deployment status" -ForegroundColor Yellow
        return $null
    }
}

# Main execution
Write-Host "🔍 Finding deployment pipeline: $PipelineName" -ForegroundColor Cyan

if (-not $isGitHubActions) {
    $pipeline = Get-DeploymentPipeline -Name $PipelineName
} else {
    # Use REST API directly with token
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-RestMethod -Uri "https://api.powerbi.com/v1.0/myorg/pipelines" -Method Get -Headers $headers
    $pipeline = $response.value | Where-Object { $_.displayName -eq $PipelineName }
}

if (-not $pipeline) {
    Write-Host "❌ Pipeline '$PipelineName' not found in workspace" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Pipeline found: $($pipeline.displayName)" -ForegroundColor Green
Write-Host "  Pipeline ID: $($pipeline.id)" -ForegroundColor Gray
Write-Host ""

# Determine stage orders (Fabric uses 0-based indexing: Dev=0, Test=1, Prod=2)
$stageMapping = @{
    "Dev" = 0
    "Test" = 1
    "Production" = 2
}

$targetStageOrder = $stageMapping[$TargetStage]
$sourceStageOrder = $targetStageOrder - 1

if ($sourceStageOrder -lt 0) {
    Write-Host "❌ Cannot deploy to Dev stage (it's the first stage)" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Deploying to $TargetStage stage..." -ForegroundColor Yellow
Write-Host ""

$deployment = Start-PipelineDeployment `
    -PipelineId $pipeline.id `
    -SourceStageOrder $sourceStageOrder `
    -TargetStageOrder $targetStageOrder `
    -DeploymentNote $Note

if (-not $deployment) {
    Write-Host "❌ Deployment failed to start" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Deployment started successfully!" -ForegroundColor Green
Write-Host "  Operation ID: $($deployment.id)" -ForegroundColor Gray
Write-Host ""

# Wait for completion if requested
if ($WaitForCompletion) {
    Write-Host "⏳ Waiting for deployment to complete..." -ForegroundColor Yellow
    
    $startTime = Get-Date
    $completed = $false
    
    while (-not $completed) {
        Start-Sleep -Seconds 10
        
        $status = Get-DeploymentStatus -PipelineId $pipeline.id -OperationId $deployment.id
        
        if ($status) {
            Write-Host "  Status: $($status.status)" -ForegroundColor Cyan
            
            if ($status.status -eq "Succeeded") {
                $completed = $true
                Write-Host ""
                Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
                break
            }
            elseif ($status.status -eq "Failed") {
                Write-Host ""
                Write-Host "❌ Deployment failed!" -ForegroundColor Red
                if ($status.error) {
                    Write-Host "  Error: $($status.error.message)" -ForegroundColor Red
                }
                exit 1
            }
        }
        
        # Check timeout
        $elapsed = (Get-Date) - $startTime
        if ($elapsed.TotalMinutes -gt $TimeoutMinutes) {
            Write-Host ""
            Write-Host "⚠️ Deployment timeout ($TimeoutMinutes minutes)" -ForegroundColor Yellow
            Write-Host "  Deployment may still be in progress. Check Fabric portal for status." -ForegroundColor Gray
            exit 1
        }
    }
}

# Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Deployment Summary" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Pipeline: $PipelineName" -ForegroundColor White
Write-Host "Target Stage: $TargetStage" -ForegroundColor White
Write-Host "Operation ID: $($deployment.id)" -ForegroundColor White
Write-Host "Note: $Note" -ForegroundColor White
Write-Host ""

if (-not $isGitHubActions) {
    Disconnect-PowerBIServiceAccount
}

Write-Host "✅ Done!" -ForegroundColor Green
