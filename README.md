# Fabric CI/CD Demo

Complete CI/CD automation for Microsoft Fabric using GitHub Actions.

## 🎯 Demo Purpose

Demonstrate enterprise-grade CI/CD for Data Science teams using Microsoft Fabric + GitHub, featuring:
- ✅ Automated validation and testing
- ✅ Multi-environment deployments (Dev → Test → Prod)
- ✅ Approval gates and change management
- ✅ Rollback capabilities
- ✅ Full audit trail
- ✅ Model and data quality evaluation framework

## 📁 Repository Structure

```
fabric-cicd-demo/
├── .github/workflows/          # GitHub Actions CI/CD pipelines
│   ├── pr-validation.yml       # Validates PRs (linting, tests)
│   ├── deploy-dev.yml          # Auto-deploy to Dev on merge
│   ├── deploy-test.yml         # Deploy to Test (manual/approval)
│   └── deploy-prod.yml         # Deploy to Prod (gated, with backup)
│
├── notebooks/                  # Fabric Notebooks
│   ├── data_ingestion.ipynb    # Bronze → Silver ETL
│   └── model_training.ipynb    # ML model training
│
├── pipelines/                  # Fabric Pipeline definitions
│   └── customer_analytics_pipeline.json
│
├── scripts/                    # Deployment & validation scripts
│   ├── validate_notebooks.py   # Notebook structure validation
│   ├── validate_pipelines.py   # Pipeline JSON validation
│   ├── deploy_to_fabric.py     # Main deployment script
│   ├── validate_deployment.py  # Post-deployment validation
│   ├── evaluate_model.py       # Model performance evaluation
│   ├── evaluate_data_quality.py # Data quality assessment
│   ├── run_evaluation.py       # Complete evaluation suite
│   ├── run_integration_tests.py
│   ├── run_smoke_tests.py
│   ├── backup_workspace.py
│   └── rollback_deployment.py
│
└── config/                     # Environment configurations
    ├── dev.yml
    ├── test.yml
    └── prod.yml
```

## 🚀 Quick Start

### Prerequisites

1. **Azure Setup:**
   - Azure subscription with Fabric capacity
   - Service Principal with Fabric API access
   - Three Fabric workspaces: Dev, Test, Prod

2. **GitHub Setup:**
   - Fork this repository
   - Configure repository secrets (see below)

### Required GitHub Secrets

```bash
AZURE_CLIENT_ID             # Service Principal Client ID
AZURE_TENANT_ID             # Azure Tenant ID
AZURE_SUBSCRIPTION_ID       # Azure Subscription ID
FABRIC_DEV_WORKSPACE_ID     # Dev workspace GUID
FABRIC_TEST_WORKSPACE_ID    # Test workspace GUID
FABRIC_PROD_WORKSPACE_ID    # Prod workspace GUID
```

### Local Development Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd fabric-cicd-demo

# Install dependencies
pip install -r requirements.txt

# Validate notebooks locally
python scripts/validate_notebooks.py

# Validate pipelines locally
python scripts/validate_pipelines.py

# Run evaluation framework
python scripts/run_evaluation.py
```

## 📋 CI/CD Workflow

### 1️⃣ **Local Development**

```bash
# Create feature branch
git checkout -b feature/enhanced-logging

# Make changes to notebooks
# Edit notebooks/model_training.ipynb

# Validate locally
python scripts/validate_notebooks.py

# Commit and push
git add notebooks/model_training.ipynb
git commit -m "feat: Add enhanced logging"
git push origin feature/enhanced-logging
```

### 2️⃣ **Pull Request Validation**

When you open a PR to `main`:

✅ **Automatic checks run:**
- Black code formatting
- Flake8 linting
- Notebook structure validation
- Pipeline JSON schema validation
- Unit tests

**Time:** ~2-3 minutes

### 3️⃣ **Deploy to Dev**

When PR is merged to `main`:

✅ **Automatic deployment:**
- Authenticate to Azure/Fabric
- Deploy changed notebooks
- Deploy changed pipelines
- Validate deployment

**Time:** ~3-5 minutes

### 4️⃣ **Deploy to Test**

**Manual trigger** or **tag-based**:

```bash
# Option 1: Manual via GitHub UI
# Go to Actions → Deploy to Test → Run workflow

# Option 2: Tag-based
git tag v1.2.0-rc1
git push origin v1.2.0-rc1
```

✅ **Workflow:**
- Deploy all artifacts
- Run integration tests
- Validate deployment

**Time:** ~5-8 minutes

### 5️⃣ **Deploy to Production**

**Requires approval + change ticket:**

```bash
# Create production release tag
git tag v1.2.0
git push origin v1.2.0
```

✅ **Workflow:**
1. Pre-deployment validation
2. **APPROVAL GATE** (manager approval required)
3. Backup current production state
4. Deploy to production
5. Run smoke tests
6. Validate deployment
7. Send notifications

**Time:** ~10-15 minutes (including approval)

❌ **On failure:** Automatic rollback to backup

## ⏱️ Demo Timing Breakdown

| Phase | Activity | Time |
|-------|----------|------|
| **Setup** | Introduce context, show repo | 3 min |
| **Phase 1** | Make local change, commit | 2 min |
| **Phase 2** | Open PR, show validation | 3 min |
| **Phase 3** | Merge PR, watch Dev deployment | 4 min |
| **Phase 4** | Show Fabric Dev workspace | 2 min |
| **Phase 5** | Explain Test/Prod promotion | 3 min |
| **Phase 6** | Show governance controls | 3 min |
| **Q&A** | Questions & next steps | 10 min |
| **TOTAL** | **30 minutes** | |

## 🎬 Demo Script

### **Minute 0-3: Context**
*"Your data scientists today manually upload notebooks to Fabric. Let's automate that."*

**Show:** Repository structure, explain Dev/Test/Prod mapping

### **Minute 3-5: Local Change**
*"Let's add enhanced logging to our model training notebook."*

**Do:** 
```bash
# Open notebooks/model_training.ipynb
# Add new cell with logging
git checkout -b feature/enhanced-logging
git add notebooks/model_training.ipynb
git commit -m "feat: Add enhanced logging"
git push origin feature/enhanced-logging
```

### **Minute 5-8: Pull Request**
*"Open a PR. Watch GitHub automatically validate the code."*

**Show:**
- PR validation workflow running
- Linting checks passing
- Notebook validation passing

### **Minute 8-12: Merge & Deploy**
*"Approve and merge. Watch it automatically deploy to Dev."*

**Show:**
- Click merge
- `deploy-dev.yml` workflow starts
- Authentication step
- Deployment progress
- Validation

### **Minute 12-14: Fabric Verification**
*"Let's verify in Fabric that our changes are live."*

**Show:**
- Switch to Fabric UI
- Open Dev workspace
- Show updated notebook
- Point out the new logging cell

### **Minute 14-17: Promotion Strategy**
*"For Test and Prod, we add controls."*

**Show:**
- Test deployment workflow (manual trigger)
- Prod deployment workflow (approval gate)
- Change management ticket requirement

### **Minute 17-20: Governance**
*"Every change is tracked. Every deployment is auditable."*

**Show:**
- GitHub commit history
- PR approval trail
- Deployment logs
- Workspace state history

### **Minute 20-30: Q&A**
*"How does this fit your team's needs?"*

**Discuss:**
- Security & permissions
- Scaling to more notebooks
- Integration with existing tools
- POC timeline

## 🔧 Customization for Your Org

### Add Custom Validation Rules

Edit [scripts/validate_notebooks.py](scripts/validate_notebooks.py):

```python
def check_custom_rules(self, path: Path, nb: Any) -> bool:
    """Add your custom validation logic here"""
    # Example: Require specific libraries
    # Example: Enforce naming conventions
    # Example: Check for data quality tests
    pass
```

### Add Notifications

Edit workflows to add Slack/Teams notifications:

```yaml
- name: Send Notification
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Deployment to ${{ env.ENVIRONMENT }} completed!"
      }
```

### Integrate with Your Ticketing System

Edit [.github/workflows/deploy-prod.yml](.github/workflows/deploy-prod.yml):

```yaml
- name: Validate Change Ticket
  run: |
    # Add API call to ServiceNow/Jira/etc.
    python scripts/validate_ticket.py --ticket ${{ inputs.approval_ticket }}
```

## 🎯 Success Criteria for POC

After POC, you should have:
- ✅ 2-3 notebooks automated through CI/CD
- ✅ Dev workspace auto-deploying on merge
- ✅ Test workspace with manual approval
- ✅ Prod workspace with full governance
- ✅ Team trained on Git workflow
- ✅ Audit trail of all deployments

## 📊 ROI Metrics

Track these metrics during POC:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Time to deploy notebook | 30 min | 5 min | **83% faster** |
| Manual steps per deployment | 15 | 2 | **87% reduction** |
| Deployment errors | High | Low | **Fewer rollbacks** |
| Audit compliance | Manual | Automatic | **100% traceable** |

## 📊 Evaluation Framework

The workspace includes a comprehensive evaluation framework for model and data quality assessment.

### Quick Start

```bash
# Run complete evaluation suite
python scripts/run_evaluation.py
```

### Key Features

- **Model Evaluation**: Accuracy, Precision, Recall, F1-Score, ROC-AUC, Cross-validation
- **Data Quality**: Completeness, Uniqueness, Consistency, Accuracy, Timeliness, Validity
- **Performance Thresholds**: Automated quality gates for model acceptance
- **Comprehensive Reports**: JSON reports saved to `reports/` directory

### Usage Examples

**Evaluate Model Performance:**
```python
from scripts.evaluate_model import ModelEvaluator

evaluator = ModelEvaluator(model, X_test, y_test, X_train, y_train)
evaluator.predict()
evaluator.calculate_classification_metrics()
evaluator.evaluate_model_robustness()
evaluator.check_performance_thresholds()
evaluator.print_report()
evaluator.save_report('reports/model_evaluation.json')
```

**Evaluate Data Quality:**
```python
from scripts.evaluate_data_quality import DataQualityEvaluator

evaluator = DataQualityEvaluator(df, 'Customer Data')
evaluator.check_completeness(null_threshold=0.05)
evaluator.check_uniqueness(['customer_id'])
evaluator.print_report()
```

### Default Thresholds

**Model Performance:**
- Accuracy: ≥70%
- Precision: ≥65%
- Recall: ≥60%
- F1-Score: ≥65%

**Data Quality:**
- Completeness: <5% missing values
- Uniqueness: 0 duplicates for key columns
- Consistency: 100% compliance with business rules

For detailed documentation, see [EVALUATION_FRAMEWORK.md](EVALUATION_FRAMEWORK.md)

## 🛠️ Troubleshooting

### Workflow fails with "Unauthorized"
- Check Service Principal permissions
- Verify secrets are correctly set
- Ensure Fabric workspace access

### Notebook deployment fails
- Verify notebook JSON format
- Check Fabric API limits
- Review workspace capacity

### Validation fails
- Run locally: `python scripts/validate_notebooks.py`
- Check notebook format version
- Review error messages in workflow logs

## 📚 Next Steps

1. **Week 1:** Set up POC environment
2. **Week 2-3:** Migrate 2 notebooks, test deployment
3. **Week 4:** Team training on Git + PR workflow
4. **Week 5-6:** Expand to full notebook library
5. **Week 7+:** Optimize, add custom validations

## 🤝 Support

For questions or issues:
- Review workflow logs in GitHub Actions tab
- Check [Fabric API documentation](https://learn.microsoft.com/fabric/admin/metadata-scanning-overview)
- Contact DevOps team

## 📄 License

MIT License - See LICENSE file

---

**Built for:** NVR Data Science Team  
**Demo Date:** January 2026  
**Version:** 1.0.0
