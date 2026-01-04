# 🚀 Setup Instructions for Demo

This guide helps you prepare for the live demo with NVR.

## Pre-Demo Setup (Allow 2-3 hours)

### 1. Azure & Fabric Prerequisites

#### Create Service Principal

```bash
# Login to Azure
az login

# Create service principal
az ad sp create-for-rbac --name "fabric-cicd-demo" --role contributor \
  --scopes /subscriptions/{subscription-id}

# Note the output:
# {
#   "appId": "xxx",      # This is AZURE_CLIENT_ID
#   "tenant": "xxx",     # This is AZURE_TENANT_ID
#   "password": "xxx"    # Store securely
# }
```

#### Create Fabric Workspaces

1. **Create three workspaces in Fabric:**
   - `NVR-Dev`
   - `NVR-Test`
   - `NVR-Production`

2. **Get workspace IDs:**
   - Open each workspace in Fabric
   - URL will be: `https://app.fabric.microsoft.com/groups/{WORKSPACE_ID}/...`
   - Copy the GUID from the URL

3. **Grant service principal access:**
   - Go to Workspace Settings → Manage Access
   - Add service principal with Admin or Contributor role
   - Repeat for all three workspaces

### 2. GitHub Repository Setup

#### Fork/Create Repository

```bash
# Option 1: Copy demo folder to new repo
cd fabric-cicd-demo
git init
git add .
git commit -m "Initial commit: Fabric CI/CD demo"
git remote add origin https://github.com/sautalwar/nvrfabricdemo1.git
git push -u origin main

# Option 2: Work in existing repo
cd /path/to/existing/repo
cp -r fabric-cicd-demo/* .
git add .
git commit -m "Add Fabric CI/CD demo"
git push
```

#### Configure GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings → Secrets and variables → Actions**
3. Click **New repository secret** for each:

```
Name: AZURE_CLIENT_ID
Value: <appId from service principal>

Name: AZURE_TENANT_ID  
Value: <tenant from service principal>

Name: AZURE_SUBSCRIPTION_ID
Value: <your Azure subscription ID>

Name: FABRIC_DEV_WORKSPACE_ID
Value: <Dev workspace GUID>

Name: FABRIC_TEST_WORKSPACE_ID
Value: <Test workspace GUID>

Name: FABRIC_PROD_WORKSPACE_ID
Value: <Prod workspace GUID>
```

#### Configure Environment Protection

1. Go to **Settings → Environments**

2. **Create 'development' environment:**
   - Click **New environment**
   - Name: `development`
   - No protection rules needed (auto-deploy)

3. **Create 'test' environment:**
   - Name: `test`
   - ✅ Enable **Required reviewers** (add yourself)
   - Wait timer: 0 minutes

4. **Create 'production' environment:**
   - Name: `production`
   - ✅ Enable **Required reviewers** (add manager)
   - ✅ Enable **Wait timer** (5 minutes)
   - ✅ Enable **Prevent self-review**

### 3. Validate Setup

#### Test Authentication

```bash
# Install Azure CLI if needed
# Windows: winget install Microsoft.AzureCLI
# Mac: brew install azure-cli

# Test service principal login
az login --service-principal \
  --username <AZURE_CLIENT_ID> \
  --password <password> \
  --tenant <AZURE_TENANT_ID>

# Verify access
az account show

# Test Fabric API access (requires access token)
az account get-access-token --resource https://analysis.windows.net/powerbi/api
```

#### Test Local Scripts

```bash
# Navigate to demo folder
cd fabric-cicd-demo

# Install dependencies
pip install -r requirements.txt

# Validate notebooks
python scripts/validate_notebooks.py
# Expected output: "✅ All notebooks passed validation!"

# Validate pipelines
python scripts/validate_pipelines.py
# Expected output: "✅ All pipelines passed validation!"
```

#### Test Deployment Script (Dry Run)

```bash
# This will validate but won't actually deploy (remove when ready)
python scripts/deploy_to_fabric.py \
  --workspace-id "<DEV_WORKSPACE_ID>" \
  --environment dev \
  --artifact-type notebooks \
  --artifacts-path notebooks/
```

### 4. Pre-Demo Test Run

#### Create Test Branch

```bash
# Create feature branch
git checkout -b test/demo-validation

# Make small change to notebook
echo "# Test comment" >> notebooks/model_training.ipynb

# Commit and push
git add notebooks/model_training.ipynb
git commit -m "test: Validate CI/CD pipeline"
git push -u origin test/demo-validation
```

#### Test PR Validation

1. Go to GitHub and create PR
2. Watch **PR Validation** workflow run
3. Verify all checks pass (should take ~2-3 min)
4. **Do NOT merge yet** - keep for demo

#### Test Dev Deployment (Optional)

If you want to fully test before demo:

```bash
# Merge the test PR
# This will trigger deploy-dev workflow

# Watch the deployment in Actions tab
# Verify notebook appears in Dev Fabric workspace
```

### 5. Prepare for Demo

#### Browser Tabs Setup

Open these tabs **before** the demo:

1. **GitHub repo main page** - `https://github.com/sautalwar/nvrfabricdemo1`
2. **VS Code or GitHub editor** - Ready to edit notebook
3. **GitHub Actions page** - `https://github.com/sautalwar/nvrfabricdemo1/actions`
4. **Fabric Dev workspace** - Your Dev workspace URL
5. **Fabric Test workspace** - Your Test workspace URL (optional)
6. **Demo script** - `DEMO_SCRIPT.md` open in second monitor

#### Prepare Code Snippet

Have this ready to paste during demo:

```python
# Enhanced logging for production monitoring
print("=" * 50)
print("🚀 Model Training v2.0 - Enhanced Logging")
print("=" * 50)
print(f"Training started: {datetime.now()}")
print(f"Environment: {os.environ.get('ENVIRONMENT', 'dev')}")
print(f"Model version: 2.0")
print("=" * 50)
```

Save in a text file for quick copy-paste.

#### Prepare Git Commands

Save these commands for copy-paste:

```bash
# Create feature branch
git checkout -b feature/enhanced-logging

# Stage changes
git add notebooks/model_training.ipynb

# Commit
git commit -m "feat: Add enhanced logging to model training"

# Push
git push origin feature/enhanced-logging
```

### 6. Backup Plan

#### Record Demo Video

If possible, do a full run-through and record it:

```bash
# Windows: Use Windows Game Bar (Win + G)
# Mac: Use QuickTime Screen Recording
# Linux: Use OBS Studio
```

Keep this video ready in case of:
- Network issues
- GitHub Actions being slow
- Fabric API issues

#### Pre-Validate PR

Create a PR ahead of time that's already validated:
1. Create `backup/demo-pr` branch with changes
2. Open PR but **don't merge**
3. Let validation pass
4. Keep open as backup if live demo validation is slow

### 7. Final Checklist (Day Before Demo)

**Azure/Fabric:**
- [ ] Service principal working
- [ ] All three workspaces accessible
- [ ] Workspace IDs confirmed

**GitHub:**
- [ ] Repository pushed and accessible
- [ ] All secrets configured correctly
- [ ] Environment protection rules set up
- [ ] Workflows validated (test run completed)

**Local Setup:**
- [ ] Python dependencies installed
- [ ] Scripts validated locally
- [ ] Code snippets ready to paste
- [ ] Git commands ready to paste

**Demo Preparation:**
- [ ] Browser tabs bookmarked and ready
- [ ] Demo script printed/on second monitor
- [ ] Backup video recorded
- [ ] Backup PR created (optional)
- [ ] Customer info reviewed

**Materials:**
- [ ] ROI calculator ready
- [ ] Architecture diagram ready
- [ ] POC proposal ready to send
- [ ] Follow-up email drafted

### 8. Day of Demo Checklist (30 min before)

- [ ] Close unnecessary applications
- [ ] Disable notifications (Windows/Mac)
- [ ] Test internet connection
- [ ] Open all browser tabs
- [ ] Test screen sharing
- [ ] Have demo script visible
- [ ] Have code snippets ready
- [ ] Test microphone and camera
- [ ] Have water nearby
- [ ] Take a deep breath! 😊

## Troubleshooting

### "Workflow failed with 401 Unauthorized"

**Cause:** Service principal doesn't have Fabric access

**Fix:**
```bash
# Verify service principal
az ad sp show --id <AZURE_CLIENT_ID>

# Re-add to Fabric workspace
# Go to Workspace Settings → Manage Access → Add the service principal
```

### "Notebook deployment failed"

**Cause:** Notebook format issue or API limits

**Fix:**
```bash
# Validate notebook locally first
python scripts/validate_notebooks.py

# Check Fabric API status
# https://status.powerbi.com/
```

### "GitHub Actions taking too long"

**Workaround during demo:**
- Switch to showing pre-validated PR
- Or switch to recorded demo video
- Say: "For time, let me show you a completed run..."

### "Cannot access Fabric workspace"

**Cause:** Workspace ID incorrect or permissions issue

**Fix:**
```bash
# Verify workspace ID from URL
# Should be GUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Check service principal has access in Fabric UI
```

## Quick Commands Reference

```bash
# Test service principal
az login --service-principal --username $AZURE_CLIENT_ID --password $SP_PASSWORD --tenant $AZURE_TENANT_ID

# Get Fabric token
az account get-access-token --resource https://analysis.windows.net/powerbi/api

# Validate notebooks
python scripts/validate_notebooks.py

# Validate pipelines  
python scripts/validate_pipelines.py

# Deploy to Fabric (requires credentials)
python scripts/deploy_to_fabric.py --workspace-id <ID> --environment dev --artifact-type notebooks --artifacts-path notebooks/
```

## Support During Demo

If you run into issues during the live demo:

1. **Stay calm** - explain this is a live demo and issues happen
2. **Switch to backup** - use pre-recorded video or pre-validated PR
3. **Pivot to discussion** - use issue as teaching moment about troubleshooting
4. **Follow up** - promise to send working demo video after call

Remember: Even showing how you troubleshoot demonstrates expertise!

---

**Good luck! You've got this! 🚀**
