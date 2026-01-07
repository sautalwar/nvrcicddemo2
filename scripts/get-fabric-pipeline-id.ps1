#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Get Fabric Deployment Pipeline ID by name
.DESCRIPTION
    Lists all Fabric deployment pipelines and helps you find the pipeline ID to use in GitHub Actions
.PARAMETER PipelineName
    Name of the deployment pipeline (e.g., "pipeline1")
.PARAMETER SetSecret
    If specified, sets the FABRIC_DEPLOYMENT_PIPELINE_ID GitHub secret
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$PipelineName,
    
    [Parameter(Mandatory=$false)]
    [switch]$SetSecret
)

Write-Host "🔍 Getting Fabric Deployment Pipelines..." -ForegroundColor Cyan

# Check if PowerBI module is available
if (-not (Get-Module -ListAvailable -Name MicrosoftPowerBIMgmt.Profile)) {
    Write-Host "⚠️  MicrosoftPowerBIMgmt module not found. Installing..." -ForegroundColor Yellow
    Install-Module -Name MicrosoftPowerBIMgmt -Scope CurrentUser -Force -AllowClobber
}

# Connect to Power BI (uses same authentication as Fabric)
try {
    Write-Host "🔐 Connecting to Power BI Service..." -ForegroundColor Cyan
    Connect-PowerBIServiceAccount | Out-Null
    Write-Host "✅ Connected successfully" -ForegroundColor Green
}
catch {
    Write-Host "❌ Failed to connect: $_" -ForegroundColor Red
    exit 1
}

# Get access token for Fabric API
$token = (Get-PowerBIAccessToken -AsString).Replace("Bearer ", "")

# Call Fabric API to list deployment pipelines
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$fabricApiUrl = "https://api.fabric.microsoft.com/v1/deploymentPipelines"

try {
    Write-Host "📊 Fetching deployment pipelines..." -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri $fabricApiUrl -Headers $headers -Method Get
    
    $pipelines = $response.value
    
    if ($pipelines.Count -eq 0) {
        Write-Host "⚠️  No deployment pipelines found" -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host "`n✅ Found $($pipelines.Count) deployment pipeline(s):" -ForegroundColor Green
    Write-Host "=" * 80
    
    $foundPipeline = $null
    
    foreach ($pipeline in $pipelines) {
        $id = $pipeline.id
        $name = $pipeline.displayName
        $description = $pipeline.description
        
        Write-Host "`n📋 Pipeline: $name" -ForegroundColor Cyan
        Write-Host "   ID: $id" -ForegroundColor White
        if ($description) {
            Write-Host "   Description: $description" -ForegroundColor Gray
        }
        
        # Get stages for this pipeline
        $stagesUrl = "$fabricApiUrl/$id/stages"
        try {
            $stagesResponse = Invoke-RestMethod -Uri $stagesUrl -Headers $headers -Method Get
            $stages = $stagesResponse.value
            
            Write-Host "   Stages:" -ForegroundColor Yellow
            foreach ($stage in $stages | Sort-Object order) {
                $stageName = $stage.displayName
                $stageOrder = $stage.order
                $workspaceId = $stage.workspaceId
                Write-Host "     $stageOrder. $stageName (Workspace: $workspaceId)" -ForegroundColor Gray
            }
        }
        catch {
            Write-Host "   ⚠️  Could not retrieve stages" -ForegroundColor Yellow
        }
        
        # Check if this matches the requested pipeline name
        if ($PipelineName -and $name -eq $PipelineName) {
            $foundPipeline = $pipeline
        }
    }
    
    Write-Host "`n" + ("=" * 80)
    
    # If specific pipeline was requested
    if ($PipelineName) {
        if ($foundPipeline) {
            $pipelineId = $foundPipeline.id
            Write-Host "`n✅ Found pipeline '$PipelineName'" -ForegroundColor Green
            Write-Host "   Pipeline ID: $pipelineId" -ForegroundColor White
            
            if ($SetSecret) {
                Write-Host "`n🔐 Setting GitHub secret FABRIC_DEPLOYMENT_PIPELINE_ID..." -ForegroundColor Cyan
                
                # Detect repository from git
                $repoUrl = git config --get remote.origin.url
                if ($repoUrl -match "github\.com[:/](.+?)\.git") {
                    $repo = $matches[1]
                }
                elseif ($repoUrl -match "github\.com[:/](.+)$") {
                    $repo = $matches[1]
                }
                else {
                    Write-Host "⚠️  Could not detect GitHub repository" -ForegroundColor Yellow
                    Write-Host "   Please set the secret manually:" -ForegroundColor Yellow
                    Write-Host "   gh secret set FABRIC_DEPLOYMENT_PIPELINE_ID -b '$pipelineId' -R <owner>/<repo>" -ForegroundColor Gray
                    exit 0
                }
                
                try {
                    $pipelineId | gh secret set FABRIC_DEPLOYMENT_PIPELINE_ID -R $repo
                    Write-Host "✅ Secret set successfully for repository: $repo" -ForegroundColor Green
                }
                catch {
                    Write-Host "❌ Failed to set secret: $_" -ForegroundColor Red
                    Write-Host "   Set it manually with:" -ForegroundColor Yellow
                    Write-Host "   gh secret set FABRIC_DEPLOYMENT_PIPELINE_ID -b '$pipelineId' -R $repo" -ForegroundColor Gray
                }
            }
            else {
                Write-Host "`n💡 To set this as a GitHub secret, run:" -ForegroundColor Cyan
                Write-Host "   .\scripts\get-fabric-pipeline-id.ps1 -PipelineName '$PipelineName' -SetSecret" -ForegroundColor Gray
            }
        }
        else {
            Write-Host "`n❌ Pipeline '$PipelineName' not found" -ForegroundColor Red
            exit 1
        }
    }
    else {
        Write-Host "`n💡 To get a specific pipeline ID, run:" -ForegroundColor Cyan
        Write-Host "   .\scripts\get-fabric-pipeline-id.ps1 -PipelineName 'pipeline1'" -ForegroundColor Gray
    }
}
catch {
    Write-Host "`n❌ Failed to get deployment pipelines: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Red
    }
    exit 1
}
