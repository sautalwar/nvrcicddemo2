# Verify Fabric workspace IDs by name and (optionally) set GitHub secrets
# Usage examples:
#   pwsh scripts/verify-fabric-workspace-ids.ps1 -DevName "NVR-Dev1" -TestName "NVR-Test1" -ProdName "NVR-Production1"
#   pwsh scripts/verify-fabric-workspace-ids.ps1 -DevName "NVR-Dev1" -TestName "NVR-Test1" -ProdName "NVR-Production1" -Owner "sautalwar" -Repo "nvrcicddemo1" -SetSecrets

param(
    [Parameter(Mandatory=$true)]
    [string]$DevName,

    [Parameter(Mandatory=$true)]
    [string]$TestName,

    [Parameter(Mandatory=$true)]
    [string]$ProdName,

    [Parameter(Mandatory=$false)]
    [string]$Owner,

    [Parameter(Mandatory=$false)]
    [string]$Repo,

    [Parameter(Mandatory=$false)]
    [switch]$SetSecrets
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Verify Fabric Workspace IDs" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Ensure Power BI module
if (-not (Get-Module -ListAvailable -Name MicrosoftPowerBIMgmt)) {
    Write-Host "Installing MicrosoftPowerBIMgmt..." -ForegroundColor Yellow
    Install-Module -Name MicrosoftPowerBIMgmt -Scope CurrentUser -Force -AllowClobber
}
Import-Module MicrosoftPowerBIMgmt

# Connect
try {
    Write-Host "Connecting to Power BI Service..." -ForegroundColor Green
    Connect-PowerBIServiceAccount | Out-Null
}
catch {
    Write-Host "❌ Failed to authenticate: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

function Get-WorkspaceIdByName {
    param([string]$Name)
    $ws = Get-PowerBIWorkspace -Scope Organization | Where-Object { $_.Name -eq $Name }
    if (-not $ws) {
        Write-Host "⚠️ Workspace not found: $Name" -ForegroundColor Yellow
        $suggest = Get-PowerBIWorkspace -Scope Organization | Where-Object { $_.Name -like ("*"+$Name+"*") } | Select-Object -First 5 Name, Id
        if ($suggest) {
            Write-Host "  Suggestions:" -ForegroundColor Gray
            $suggest | ForEach-Object { Write-Host "   - $($_.Name) ($($_.Id))" -ForegroundColor Gray }
        }
        return $null
    }
    return $ws.Id
}

$devId  = Get-WorkspaceIdByName -Name $DevName
$testId = Get-WorkspaceIdByName -Name $TestName
$prodId = Get-WorkspaceIdByName -Name $ProdName

Write-Host ""; Write-Host "Resolved IDs:" -ForegroundColor Cyan
if ($devId)  { Write-Host "  DEV  ($DevName):  $devId" -ForegroundColor White } else { Write-Host "  DEV  ($DevName):  NOT FOUND" -ForegroundColor Red }
if ($testId) { Write-Host "  TEST ($TestName): $testId" -ForegroundColor White } else { Write-Host "  TEST ($TestName): NOT FOUND" -ForegroundColor Red }
if ($prodId) { Write-Host "  PROD ($ProdName): $prodId" -ForegroundColor White } else { Write-Host "  PROD ($ProdName): NOT FOUND" -ForegroundColor Red }

# Optionally set GitHub repo secrets (names only; values not echoed)
if ($SetSecrets) {
    if (-not $Owner -or -not $Repo) {
        Write-Host "❌ SetSecrets requires -Owner and -Repo" -ForegroundColor Red
        exit 1
    }
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Write-Host "❌ GitHub CLI 'gh' not found. Install from https://cli.github.com/" -ForegroundColor Red
        exit 1
    }
    $repoRef = "$Owner/$Repo"
    if ($devId)  { gh secret set FABRIC_DEV_WORKSPACE_ID  -R $repoRef -b $devId  | Out-Null }
    if ($testId) { gh secret set FABRIC_TEST_WORKSPACE_ID -R $repoRef -b $testId | Out-Null }
    if ($prodId) { gh secret set FABRIC_PROD_WORKSPACE_ID -R $repoRef -b $prodId | Out-Null }
    Write-Host "✅ GitHub secrets updated (names only shown, values hidden) for $repoRef" -ForegroundColor Green
}

Disconnect-PowerBIServiceAccount | Out-Null
Write-Host "✅ Done" -ForegroundColor Green
