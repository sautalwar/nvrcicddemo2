# 🎯 Complete CI/CD Demo Script - Model Training Bug Fix

## Demo Overview
This demo showcases a complete end-to-end workflow for fixing a critical bug in production, from issue discovery through to production deployment using GitHub + Microsoft Fabric CI/CD integration.

---

## 📋 Demo Steps

### **Step 1: Customer Discovers Critical Bug** 🐛

**Scenario**: The model training pipeline is failing in production when processing new customer data.

**Action**: Navigate to GitHub Issues
- Open: https://github.com/sautalwar/nvrcicddemo1/issues/3
- **Issue #3**: 🐛 Critical Bug: Division by Zero in Model Training Feature Engineering
  
**Explain to Audience**:
- Production pipeline crashes when `customer_age_days = 0` (new customers)
- Feature engineering code has division by zero: 
  ```python
  data['purchase_frequency'] = data['total_purchases'] / (data['customer_age_days'] / 30)
  data['engagement_score'] = (data['total_purchases'] * data['avg_purchase_value']) / data['customer_age_days']
  ```
- This is blocking daily ML model updates
- **Impact**: Critical - Production down

---

### **Step 2: Add Issue to GitHub Project Board** 📊

**Action**: Task Management with GitHub Projects
1. Open: https://github.com/users/sautalwar/projects/1/views/1
2. Show Issue #3 in the project board
3. Demonstrate:
   - Issue is tracked in "ML Pipeline Development" project
   - Move issue to "In Progress" column
   - Add labels: `bug`, `priority-high`, `production`
   - Assign to yourself

**Explain to Audience**:
- GitHub Projects provides visual task management
- Team visibility into what's being worked on
- Integration with issues enables automatic updates

---

### **Step 3: Developer Examines the Notebook** 🔍

**Action**: Review the problematic code
- Open file: `notebooks/model_training.Notebook/notebook-content.py`
- Navigate to lines 88-90 (Feature Engineering section)
- Show the buggy code:
  ```python
  # Feature engineering
  print("🔧 Engineering features...")

  data['purchase_frequency'] = data['total_purchases'] / (data['customer_age_days'] / 30)
  data['engagement_score'] = (data['total_purchases'] * data['avg_purchase_value']) / data['customer_age_days']
  data['recency_score'] = 1 / (data['days_since_last_purchase'] + 1)
  ```

**Explain to Audience**:
- Identified root cause: No protection against zero division
- Need to handle edge case gracefully
- Solution: Use `np.maximum()` to set minimum divisor value

---

### **Step 4: Create Fix Branch** 🌿

**Action**: Create branch for the fix
- Branch name: `fix/division-zero-feature-engineering`
- Already created: ✅

**Terminal Command**:
```powershell
git checkout fix/division-zero-feature-engineering
```

**Explain to Audience**:
- Branching strategy keeps main branch stable
- Enables parallel development
- Allows testing before merging to production

---

### **Step 5: Implement the Fix** 🔧

**Action**: Fix the code
- Show the corrected code (already applied):
  ```python
  # Feature engineering
  print("🔧 Engineering features...")

  # Prevent division by zero for new customers (customer_age_days = 0)
  data['purchase_frequency'] = data['total_purchases'] / np.maximum(data['customer_age_days'] / 30, 1)
  data['engagement_score'] = (data['total_purchases'] * data['avg_purchase_value']) / np.maximum(data['customer_age_days'], 1)
  data['recency_score'] = 1 / (data['days_since_last_purchase'] + 1)
  ```

**Explain to Audience**:
- `np.maximum()` ensures minimum value of 1
- Prevents ZeroDivisionError
- Maintains mathematical correctness for valid data
- Added comment for future maintainability

---

### **Step 6: Link Issue to Pull Request** 🔗

**Action**: Create Pull Request linking to issue
- Open: https://github.com/sautalwar/nvrcicddemo1/pull/14
- **PR #14**: 🔧 Fix: Prevent division by zero in model training feature engineering

**Show the PR Description**:
- Links to Issue #3 with "Closes #3"
- Detailed change description
- Testing checklist
- Deployment plan
- Impact assessment

**Explain to Audience**:
- PR automatically links to Issue #3
- Using "Closes #3" will auto-close issue when PR merges
- Code review process before deployment
- All changes are tracked and auditable

---

### **Step 7: Test in Dev Fabric Workspace** 🧪

**Action**: Manual or automated testing in Development environment

**Option A - Manual Testing**:
1. Open Microsoft Fabric workspace (Dev)
2. Navigate to the model_training notebook
3. Run the notebook with test data including `customer_age_days = 0`
4. Verify no errors occur
5. Check model training completes successfully

**Option B - Automated Testing**:
```powershell
# Run validation tests
python scripts/validate_notebooks.py

# Run smoke tests
python scripts/run_smoke_tests.py
```

**Explain to Audience**:
- Dev workspace is isolated from production
- Safe environment for testing changes
- Validate fix works before deployment
- Multiple testing layers (unit, integration, smoke tests)

---

### **Step 8: Merge Fix from Fabric to GitHub** 🔄

**Action**: Sync changes from Fabric workspace back to GitHub
- Show the Git integration in Fabric
- Commit changes with message referencing issue number
- Push to remote branch

**Alternative - Already done via GitHub**:
- Changes were made directly in GitHub
- Demonstrate bidirectional sync capability

**Explain to Audience**:
- Fabric and GitHub stay synchronized
- Changes can originate from either platform
- Version control for notebooks and pipelines
- Collaboration between data scientists and engineers

---

### **Step 9: Run Test Pipeline** 🧪

**Action**: Execute CI/CD pipeline for Test environment

**GitHub Actions Workflow**:
1. Go to: Actions tab in GitHub
2. Look for workflow: `Deploy to Test` or `deploy-test.yml`
3. Trigger manually or show auto-trigger on PR

**Expected Flow**:
```yaml
Test Pipeline:
├── Validate code quality
├── Run unit tests
├── Deploy to Test Fabric workspace
├── Run integration tests
├── Generate test report
└── Post results to PR
```

**Terminal Command** (if triggering manually):
```powershell
# Trigger test deployment pipeline
python scripts/trigger_fabric_deployment_pipeline.py --environment test
```

**Explain to Audience**:
- Automated deployment to Test workspace
- Runs full test suite
- Validates deployment process
- Gate before production deployment

---

### **Step 10: Review and Approve PR** ✅

**Action**: Code Review Process
1. Navigate to PR #14
2. Review the changes (Files changed tab)
3. Add review comments if needed
4. Approve the PR

**Optional - Request Copilot Review**:
```
Use GitHub Copilot to auto-review code quality
```

**Explain to Audience**:
- Peer review ensures code quality
- Automated checks run (linting, tests, security scans)
- Approval required before merge
- Best practice for production changes

---

### **Step 11: Merge to Main Branch** 🎯

**Action**: Merge the PR
1. Click "Merge pull request" on PR #14
2. Select merge type: "Squash and merge" (recommended)
3. Confirm merge
4. Observe:
   - Issue #3 automatically closes
   - Branch can be deleted
   - Main branch updated

**Explain to Audience**:
- Merge triggers production deployment workflow
- Issue automatically closed via "Closes #3" keyword
- Git history remains clean
- Audit trail maintained

---

### **Step 12: Execute Production Pipeline** 🚀

**Action**: Deploy to Production Fabric workspace

**GitHub Actions Workflow**:
1. Go to: Actions tab
2. Workflow: `Deploy to Production` or `deploy-prod.yml`
3. Show workflow execution:
   ```yaml
   Production Pipeline:
   ├── Checkout code from main branch
   ├── Validate deployment
   ├── Backup current production state
   ├── Deploy to Production Fabric workspace
   ├── Run smoke tests
   ├── Monitor deployment
   └── Send notifications
   ```

**Key Files**:
- `.github/workflows/deploy-prod.yml` - Production workflow
- `scripts/deploy_to_fabric.py` - Deployment script
- `scripts/validate_deployment.py` - Validation script
- `scripts/run_smoke_tests.py` - Smoke tests

**Explain to Audience**:
- Automated production deployment
- Includes rollback capability
- Production validation tests
- Monitoring and alerting
- Zero-downtime deployment

---

### **Step 13: Verify Production Deployment** ✅

**Action**: Confirm successful deployment

**Verification Steps**:
1. **Check GitHub Actions**: All steps green ✅
2. **Fabric Workspace**: Open Production workspace
   - Navigate to `model_training.Notebook`
   - Verify latest version deployed
   - Check timestamp/version number

3. **Run Production Test**:
   ```powershell
   python scripts/run_smoke_tests.py --environment production
   ```

4. **Monitor Pipeline**:
   - Trigger a model training run
   - Verify it completes successfully
   - Check logs for the fix working
   - Confirm no division by zero errors

**Explain to Audience**:
- Multi-layer verification
- Automated smoke tests in production
- Continuous monitoring
- Quick rollback if issues detected

---

## 🎬 Demo Talking Points

### Key Highlights:
1. **Issue Tracking**: GitHub Issues for bug tracking and project management
2. **Project Management**: Visual task management with GitHub Projects
3. **Version Control**: Git branching strategy and PR workflow
4. **Code Review**: Collaborative review process before deployment
5. **CI/CD Integration**: Automated testing and deployment pipelines
6. **Fabric Integration**: Bidirectional sync between GitHub and Microsoft Fabric
7. **Testing Strategy**: Multi-environment testing (Dev → Test → Prod)
8. **Automation**: Minimal manual intervention, maximum reliability
9. **Audit Trail**: Complete history of changes and deployments
10. **Rollback Capability**: Safe deployment with rollback options

### Benefits Demonstrated:
- ✅ Faster time to resolution
- ✅ Reduced human error
- ✅ Better collaboration
- ✅ Complete audit trail
- ✅ Production safety
- ✅ Automated testing
- ✅ Continuous deployment

---

## 📚 Reference Links

- **Issue**: https://github.com/sautalwar/nvrcicddemo1/issues/3
- **Pull Request**: https://github.com/sautalwar/nvrcicddemo1/pull/14
- **Project Board**: https://github.com/users/sautalwar/projects/1/views/1
- **Repository**: https://github.com/sautalwar/nvrcicddemo1
- **Workflows**: https://github.com/sautalwar/nvrcicddemo1/actions

---

## 🔧 Troubleshooting

### If workflows don't trigger:
```powershell
# Manually trigger workflow
gh workflow run deploy-test.yml
gh workflow run deploy-prod.yml
```

### If tests fail:
```powershell
# Check test logs
python scripts/run_integration_tests.py --verbose

# Rollback if needed
python scripts/rollback_deployment.py --environment production
```

### If sync issues between Fabric and GitHub:
1. Check Git integration settings in Fabric workspace
2. Verify credentials are valid
3. Manual pull/push if needed

---

## ⏱️ Demo Timeline

Total demo time: **15-20 minutes**

1. Issue Discovery (2 min)
2. Project Management (2 min)
3. Code Review (2 min)
4. Fix Implementation (3 min)
5. Testing in Dev (2 min)
6. PR Review (2 min)
7. Production Deployment (4 min)
8. Verification (3 min)

---

## 🎓 Q&A Preparation

**Expected Questions**:
1. Q: How do you handle schema changes?
   - A: `scripts/detect_schema_changes.py` validates before deployment

2. Q: What happens if production deployment fails?
   - A: Automated rollback via `scripts/rollback_deployment.py`

3. Q: How do you manage secrets?
   - A: GitHub Secrets + Azure Key Vault integration

4. Q: Can you deploy to multiple environments?
   - A: Yes - Dev, Test, Prod with separate workflows

5. Q: How do you handle hotfixes?
   - A: Same workflow, expedited approval process

---

## ✅ Pre-Demo Checklist

- [ ] All GitHub secrets configured
- [ ] Fabric workspaces (Dev, Test, Prod) accessible
- [ ] Service principal credentials valid
- [ ] GitHub Actions enabled
- [ ] Project board set up
- [ ] Test data available
- [ ] Backup of production state
- [ ] Network connectivity verified
- [ ] Browser tabs pre-opened
- [ ] PowerShell terminal ready

---

**Good luck with your demo! 🚀**
