# Fabric Deployment Pipeline Integration Guide

This guide explains how to connect your Fabric UI deployment pipeline (Dev → Test → Production) with your GitHub Actions CI/CD workflow.

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Actions Workflow                      │
│                                                                   │
│  1. PR Validation → 2. Deploy to Dev → 3. Trigger Fabric         │
│     (Quality Gates)    (Auto)            Deployment Pipeline      │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│            Fabric Deployment Pipeline (UI-based)                 │
│                                                                   │
│     ┌──────────┐      ┌──────────┐      ┌──────────────┐       │
│     │   Dev    │ ───> │   Test   │ ───> │  Production  │       │
│     └──────────┘      └──────────┘      └──────────────┘       │
│                                                                   │
│  Artifacts: Notebooks, Pipelines, Models, Semantic Models        │
└─────────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

### 1. Create Fabric Deployment Pipeline (UI)

1. **Go to Fabric Portal** → Click **Deployment pipelines** in left nav
2. **Create new pipeline** → Name it `pipeline1`
3. **Assign workspaces**:
   - Development → `NVR-Dev` workspace
   - Test → `NVR-Test` workspace  
   - Production → `NVR-Production` workspace
4. **Save** the pipeline

### 2. Configure GitHub Secrets

Add these secrets in your GitHub repository (Settings → Secrets):

```bash
AZURE_CLIENT_ID         # Service Principal Client ID
AZURE_CLIENT_SECRET     # Service Principal Secret
AZURE_TENANT_ID         # Your Azure Tenant ID
AZURE_SUBSCRIPTION_ID   # Your Azure Subscription ID

FABRIC_DEV_WORKSPACE_ID         # Dev workspace GUID
FABRIC_TEST_WORKSPACE_ID        # Test workspace GUID  
FABRIC_PROD_WORKSPACE_ID        # Prod workspace GUID
```

## 🔄 How It Works

### Workflow 1: Automatic Dev Deployment

```yaml
# Triggered on: Push to main branch
1. Code merged to main
2. GitHub Actions validates code
3. Deploys notebooks + pipelines to Dev workspace
4. (Optional) Triggers Fabric deployment pipeline to promote to Test
```

**Files Involved:**
- `.github/workflows/model-training-pipeline.yml` - Main workflow
- `scripts/deploy_to_fabric.py` - Python deployment script
- `scripts/trigger-fabric-deployment-pipeline.ps1` - PowerShell trigger script

### Workflow 2: Manual Test/Prod Deployment

```yaml
# Triggered on: Manual workflow dispatch
1. Developer clicks "Run workflow" in GitHub Actions
2. Select environment (Test or Prod)
3. Provide deployment reason + change ticket
4. Approval required (configured in GitHub Environments)
5. Deploys to selected environment
```

## 🚀 Step-by-Step Setup

### Step 1: Update Deployment Pipeline Name

In your workflow file (`.github/workflows/model-training-pipeline.yml`), update the pipeline name:

```yaml
pwsh scripts/trigger-fabric-deployment-pipeline.ps1 \
  -WorkspaceId "${{ secrets.FABRIC_DEV_WORKSPACE_ID }}" \
  -PipelineName "pipeline1"  # ← Change this to match your actual pipeline name
  -TargetStage "Test" \
  -Note "Automated deployment from GitHub Actions"
```

### Step 2: Test the Integration

#### Option A: Test Locally

```powershell
# 1. Create workspaces
.\scripts\create-fabric-workspaces.ps1 -WorkspacePrefix "NVR"

# 2. Grant service principal access  
.\scripts\grant-workspace-access.ps1 `
  -ServicePrincipalId "your-client-id" `
  -TenantId "your-tenant-id" `
  -WorkspaceIds @("dev-ws-id", "test-ws-id", "prod-ws-id") `
  -Role "Admin"

# 3. Assign capacity
.\scripts\assign-fabric-capacity.ps1 `
  -TenantId "your-tenant-id" `
  -CapacityId "your-capacity-id" `
  -WorkspaceIds @("dev-ws-id", "test-ws-id", "prod-ws-id")

# 4. Test deployment pipeline trigger
.\scripts\trigger-fabric-deployment-pipeline.ps1 `
  -WorkspaceId "dev-workspace-id" `
  -PipelineName "pipeline1" `
  -TargetStage "Test" `
  -WaitForCompletion
```

#### Option B: Test via GitHub Actions

1. **Push a change** to trigger the workflow:
   ```bash
   # Make a small change to notebook
   echo "# Test change" >> notebooks/model_training.ipynb
   
   git add .
   git commit -m "test: Trigger deployment pipeline"
   git push origin main
   ```

2. **Watch GitHub Actions**: Go to Actions tab and monitor the workflow

3. **Check Fabric Portal**: Verify deployment in your Fabric deployment pipeline UI

### Step 3: Configure Deployment Rules (Optional)

You can customize deployment behavior in the workflow:

```yaml
# Auto-promote to Test after Dev deployment
- name: 🎯 Auto-promote to Test
  if: success()  # Only if Dev deployment succeeds
  run: |
    pwsh scripts/trigger-fabric-deployment-pipeline.ps1 \
      -PipelineName "pipeline1" \
      -TargetStage "Test" \
      -WaitForCompletion  # Wait for completion before continuing
```

## 🎛️ Deployment Options

### Option 1: GitHub Actions → Dev Only (Manual Fabric UI promotion)

**Use Case**: You want full control in Fabric UI

```yaml
# In workflow: Deploy to Dev only
# Developers manually promote via Fabric UI
```

**Pros:**
- Visual promotion in Fabric UI
- Easy rollback via UI
- Good for learning/demo

**Cons:**
- Manual step required
- No audit trail in GitHub

### Option 2: GitHub Actions → Fabric API (Fully Automated)

**Use Case**: Full automation, GitOps approach

```yaml
# In workflow: Trigger Fabric deployment pipeline via API
# Automatically promotes Dev → Test → Prod based on rules
```

**Pros:**
- Fully automated
- Complete audit trail
- No manual intervention

**Cons:**
- Requires API configuration
- Less visibility in UI

### Option 3: Hybrid (Recommended for Demo)

**Use Case**: Best of both worlds

```yaml
# Dev → Auto-deploy via GitHub Actions
# Test → Auto-promote via Fabric API (with approval)
# Prod → Manual trigger with change ticket
```

**Configuration:**
```yaml
# Deploy to Dev (automatic)
on:
  push:
    branches: [main]

# Promote to Test (automatic after Dev)
- name: Promote to Test
  run: trigger-fabric-deployment-pipeline.ps1 -TargetStage "Test"

# Deploy to Prod (manual with approval)
on:
  workflow_dispatch:
    inputs:
      environment: prod
```

## 📊 Demo Flow

### Live Demo Script

1. **Show Fabric Deployment Pipeline**
   - Open Fabric portal
   - Show pipeline with 3 stages
   - Explain Dev → Test → Prod flow

2. **Make a Code Change**
   ```bash
   # Edit notebook to add logging
   # Commit and push
   git add notebooks/model_training.ipynb
   git commit -m "feat: Add enhanced logging"
   git push origin main
   ```

3. **Watch GitHub Actions**
   - Show workflow running
   - Point out validation steps
   - Show deployment to Dev

4. **Show Fabric Pipeline**
   - Refresh Fabric UI
   - Show artifacts in Dev stage
   - Click "Deploy" to promote to Test

5. **Show Approval Flow** (if configured)
   - GitHub shows "Waiting for approval"
   - Approve deployment
   - Watch it deploy to Test

## 🔧 Troubleshooting

### Issue: "Pipeline not found"

**Solution:**
```powershell
# List all deployment pipelines
$token = az account get-access-token --resource https://analysis.windows.net/powerbi/api --query accessToken -o tsv
$headers = @{ "Authorization" = "Bearer $token" }
Invoke-RestMethod -Uri "https://api.powerbi.com/v1.0/myorg/pipelines" -Headers $headers
```

### Issue: "Deployment failed - workspace not assigned"

**Solution:**
```powershell
# Ensure workspaces are assigned to pipeline stages in Fabric UI
# Settings → Deployment pipelines → Edit pipeline → Assign workspaces
```

### Issue: "Access denied"

**Solution:**
```powershell
# Grant service principal access to all workspaces
.\scripts\grant-workspace-access.ps1 -Role "Admin"
```

## 📚 Additional Resources

- **Fabric Deployment Pipelines Docs**: https://learn.microsoft.com/fabric/cicd/deployment-pipelines/intro-to-deployment-pipelines
- **Fabric REST API**: https://learn.microsoft.com/rest/api/fabric/
- **GitHub Actions Docs**: https://docs.github.com/actions

## 🎯 Next Steps

1. ✅ Create Fabric deployment pipeline in UI
2. ✅ Update pipeline name in workflow
3. ✅ Configure GitHub secrets
4. ✅ Test deployment locally
5. ✅ Test via GitHub Actions
6. ✅ Configure approval gates
7. ✅ Document deployment process
8. ✅ Train team on new workflow

---

**Need Help?** Check the scripts in `scripts/` folder or refer to setup documentation in `SETUP.md`.
