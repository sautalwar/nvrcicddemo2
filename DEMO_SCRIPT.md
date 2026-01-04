# 🎬 DEMO EXECUTION SCRIPT
## Fabric CI/CD Demo - NVR Data Science Team

**Total Duration:** 30 minutes  
**Presenter:** Solutions Architect  
**Audience:** Data Science Team Manager

---

## 🎯 DEMO OBJECTIVES

By the end of this demo, the manager should understand:
1. How GitHub + Fabric eliminates manual deployment
2. How automated validation prevents errors
3. How approval gates ensure governance
4. The exact time savings their team will gain

---

## ⏰ MINUTE-BY-MINUTE BREAKDOWN

### **MINUTES 0-3: OPENING & CONTEXT** ⏱️ 3 min

**SCRIPT:**
> "Thank you for meeting with me today. I understand your Data Science team is spending significant time manually uploading notebooks to Fabric, and you want to automate this with CI/CD. Today I'll show you exactly how GitHub Actions + Microsoft Fabric work together to eliminate that manual work."

**ACTIONS:**
1. Share screen showing GitHub repository
2. Point out the structure:
   ```
   ✅ notebooks/     ← Your data scientists' work
   ✅ pipelines/     ← Fabric pipelines
   ✅ .github/workflows/ ← CI/CD automation
   ```

**KEY POINTS:**
- "This is a real working demo, not slides"
- "We'll make a live code change and watch it deploy automatically"
- "Everything we do today leaves an audit trail"

**TRANSITION:** *"Let me show you how this works in practice..."*

---

### **MINUTES 3-5: LOCAL DEVELOPMENT** ⏱️ 2 min

**SCRIPT:**
> "Imagine I'm a data scientist on your team. I want to improve our model training notebook by adding better logging. Let me show you how simple this is..."

**ACTIONS:**

1. **Open VS Code** (or show GitHub web editor)
2. **Navigate to:** `notebooks/model_training.ipynb`
3. **Add a new cell** (use pre-prepared code):

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

4. **Save the file**

5. **Create feature branch:**
```bash
git checkout -b feature/enhanced-logging
git add notebooks/model_training.ipynb
git commit -m "feat: Add enhanced logging to model training"
git push origin feature/enhanced-logging
```

**KEY POINTS:**
- "Normal Git workflow your team may already know"
- "No manual uploads to Fabric yet"
- "Everything is version controlled"

**TIMING TIP:** Have the code snippet ready to paste - don't type it live

**TRANSITION:** *"Now watch what happens when I open a Pull Request..."*

---

### **MINUTES 5-8: PULL REQUEST VALIDATION** ⏱️ 3 min

**SCRIPT:**
> "As soon as I open a Pull Request, GitHub automatically runs quality checks. This prevents bad code from reaching production."

**ACTIONS:**

1. **Open Pull Request on GitHub:**
   - Click "Compare & pull request"
   - Title: `feat: Add enhanced logging to model training`
   - Description: `Adds production-ready logging for better observability`
   - Click "Create pull request"

2. **Show PR Validation Running:**
   - Navigate to "Checks" tab
   - Point out running checks:
     ```
     ✅ Black code formatting
     ✅ Flake8 linting
     ✅ Notebook structure validation
     ✅ Unit tests
     ```

3. **Show validation passing** (should take ~2 min)

4. **Show validation details:**
   - Click on a check to show logs
   - Highlight: "This caught errors before they reached Fabric"

**KEY POINTS:**
- "Catches errors in 2 minutes, not 2 hours after deployment"
- "Your team gets immediate feedback"
- "Only validated code can be merged"

**DEMO TIP:** If checks take too long, have a pre-validated PR ready as backup

**TRANSITION:** *"Now I'll approve and merge this PR. Watch what happens automatically..."*

---

### **MINUTES 8-12: AUTOMATIC DEPLOYMENT TO DEV** ⏱️ 4 min

**SCRIPT:**
> "The moment I click merge, GitHub automatically deploys to your Dev Fabric workspace. No manual steps. No tickets. Just automation."

**ACTIONS:**

1. **Merge the PR:**
   - Click "Merge pull request"
   - Click "Confirm merge"
   - ⏰ **Note the time**

2. **Navigate to Actions tab immediately:**
   - Show "Deploy to Fabric Dev" workflow starting
   - Expand workflow to show steps:
     ```
     🔐 Authenticate to Azure
     🎫 Get Fabric access token
     🚀 Deploy notebooks to Fabric
     ✅ Validate deployment
     ```

3. **Watch deployment progress:**
   - Point out: "Authenticating securely..."
   - Point out: "Deploying only changed notebooks..."
   - Point out: "Validating everything deployed correctly..."

4. **When complete (~3-4 min):**
   - ⏰ **Note the time** 
   - Show green checkmark
   - Click into job to show logs
   - Highlight: "✅ Notebooks deployed successfully"

**KEY POINTS:**
- "From merge to deployed: **4 minutes**"
- "Zero manual steps"
- "Full audit trail in GitHub"
- "Your team can keep working - no waiting"

**TIMING TIP:** If deployment is slow, talk through the architecture while waiting

**TRANSITION:** *"Let's verify this is actually in Fabric..."*

---

### **MINUTES 12-14: VERIFY IN FABRIC WORKSPACE** ⏱️ 2 min

**SCRIPT:**
> "Let me show you this is real. We'll open the Dev Fabric workspace and see our changes live."

**ACTIONS:**

1. **Open Fabric** in new tab:
   - Navigate to Dev workspace
   - Show workspace overview

2. **Open the deployed notebook:**
   - Click on "model_training" notebook
   - Scroll to the **new cell** with enhanced logging
   - Point out: "This is the exact code we just committed"

3. **(Optional) Run a cell:**
   - Execute the new logging cell
   - Show output:
     ```
     ==================================================
     🚀 Model Training v2.0 - Enhanced Logging
     ==================================================
     Training started: 2026-01-03 14:23:15
     Environment: dev
     Model version: 2.0
     ==================================================
     ```

**KEY POINTS:**
- "4 minutes from commit to live in Fabric"
- "Same code, deployed automatically"
- "Your data scientists don't touch Fabric UI for deployment"

**POWER STATEMENT:**
> "What used to take your team 30 minutes of manual uploading now happens automatically in 4 minutes."

**TRANSITION:** *"That's Dev. Let me show you how we control promotions to Test and Production..."*

---

### **MINUTES 14-17: TEST & PRODUCTION PROMOTION** ⏱️ 3 min

**SCRIPT:**
> "Dev auto-deploys for fast iteration. But Test and Production require controls. Let me show you the governance we've built in."

**ACTIONS:**

1. **Show Test Deployment Workflow:**
   - Navigate to `.github/workflows/deploy-test.yml`
   - Highlight key sections:
     ```yaml
     environment: 
       name: test  # ← Requires approval
     ```
   - Explain: "Test requires manual trigger OR approval"

2. **Show Test deployment options:**
   - Go to Actions → "Deploy to Fabric Test"
   - Show manual trigger: "Run workflow"
   - Show parameters:
     ```
     deployment_reason: "Validated in Dev, ready for UAT"
     ```

3. **Show Production Workflow:**
   - Navigate to `.github/workflows/deploy-prod.yml`
   - Highlight security features:
     ```yaml
     ✅ Pre-deployment validation
     ✅ Approval gate (manager must approve)
     ✅ Change management ticket required
     ✅ Automatic backup before deployment
     ✅ Smoke tests after deployment
     ✅ Automatic rollback on failure
     ```

4. **Show approval gate:**
   - Navigate to Settings → Environments → production
   - Show required reviewers: "Manager approval required"

**KEY POINTS:**
- "Dev: Fast & automatic"
- "Test: Controlled & validated"
- "Prod: Gated, backed up, and audited"

**VISUAL:**
```
Dev ──automatic──> [4 min]
Test ──manual approval──> [8 min]
Prod ──manager approval + ticket──> [15 min with backup]
```

**TRANSITION:** *"Let me show you the governance and audit trail this creates..."*

---

### **MINUTES 17-20: GOVERNANCE & AUDIT TRAIL** ⏱️ 3 min

**SCRIPT:**
> "Every single change is tracked. Every deployment is auditable. Let me show you what this looks like for compliance..."

**ACTIONS:**

1. **Show Git Commit History:**
   - Navigate to repository commits
   - Point out:
     ```
     ✅ Who made the change (author)
     ✅ When it was made (timestamp)
     ✅ What was changed (diff)
     ✅ Why it was changed (commit message)
     ```

2. **Show Pull Request Trail:**
   - Go to merged PR
   - Show:
     ```
     ✅ Who requested the change
     ✅ Who reviewed it
     ✅ When it was approved
     ✅ What checks passed
     ✅ Full discussion thread
     ```

3. **Show Deployment Logs:**
   - Navigate to Actions → successful deployment
   - Show timestamped log:
     ```
     [2026-01-03 14:20:15] 🔐 Authenticated to Azure
     [2026-01-03 14:20:47] 🚀 Deploying notebook: model_training
     [2026-01-03 14:22:33] ✅ Deployment validated
     ```

4. **Show Environment History:**
   - Go to Deployments tab
   - Show which version is in each environment:
     ```
     Dev:  v1.2.3 (deployed 4 min ago by alice)
     Test: v1.2.2 (deployed 2 days ago by bob)
     Prod: v1.2.1 (deployed 1 week ago by manager)
     ```

**KEY POINTS:**
- "Complete audit trail for compliance"
- "Can answer: Who deployed what, when, and why?"
- "Can roll back to any previous version"

**GOVERNANCE TABLE:**

| Requirement | Implementation |
|-------------|----------------|
| Code review | Pull Request approval (2 reviewers) |
| Testing | Automated validation + integration tests |
| Change approval | GitHub environment protection |
| Change tracking | Git commit history |
| Deployment logs | GitHub Actions artifacts |
| Rollback | Automated backup + restore scripts |

**TRANSITION:** *"Now let me show you the operating model for your team..."*

---

### **MINUTES 20-23: OPERATING MODEL** ⏱️ 3 min

**SCRIPT:**
> "Here's how your team would work day-to-day with this system..."

**SHOW DIAGRAM:**

```
┌─────────────────────────────────────────────────────────┐
│                  DATA SCIENTIST WORKFLOW                 │
└─────────────────────────────────────────────────────────┘

1. Local Development
   └─> Edit notebook in VS Code or Jupyter
   └─> Test locally
   └─> Commit to feature branch
   └─> Push to GitHub
                    ↓
2. Pull Request
   └─> Open PR to main branch
   └─> Automated validation runs (2-3 min)
   └─> Team reviews code
   └─> Approve & merge
                    ↓
3. Auto-Deploy to Dev
   └─> GitHub Actions triggers (on merge)
   └─> Deploys to Dev workspace (4 min)
   └─> Team validates in Dev
                    ↓
4. Promote to Test (Manual)
   └─> Lead approves deployment
   └─> Integration tests run (8 min)
   └─> UAT validation
                    ↓
5. Promote to Prod (Gated)
   └─> Manager approval + Change ticket
   └─> Backup created automatically
   └─> Deploy + smoke tests (15 min)
   └─> Monitored for 24 hours
```

**BRANCHING STRATEGY:**

```
main ──────●───────●───────●──────> [Auto-deploys to Dev]
            │       │       │
feature/A ──┘       │       │
feature/B ──────────┘       │
hotfix/C ────────────────────┘
```

**ROLES & PERMISSIONS:**

| Role | Permissions |
|------|-------------|
| Data Scientist | Create branches, open PRs, deploy to Dev |
| Senior DS | Approve PRs, deploy to Test |
| Manager | Approve Prod deployments |
| DevOps | Manage workflows, secrets, infrastructure |

**KEY POINTS:**
- "Your team learns Git (many already know it)"
- "No direct Fabric deployments - automation handles it"
- "Clear separation: Dev (fast) → Test (validated) → Prod (controlled)"

**TRANSITION:** *"Let's talk about what this means for your team specifically..."*

---

### **MINUTES 23-25: BUSINESS VALUE & ROI** ⏱️ 2 min

**SCRIPT:**
> "Let me show you the concrete benefits for NVR..."

**SHOW ROI TABLE:**

| Metric | Current (Manual) | With CI/CD | Savings |
|--------|------------------|------------|---------|
| **Time to deploy 1 notebook** | 30 min | 4 min | **87% faster** |
| **Manual steps per deployment** | 15 steps | 0 steps | **100% automated** |
| **Human errors** | ~1 per week | Near zero | **Error reduction** |
| **Rollback time** | 2-4 hours | 5 min | **95% faster** |
| **Audit preparation** | Days | Instant | **Compliance ready** |

**MONTHLY IMPACT (assuming 20 deployments/month):**

```
Current: 20 deployments × 30 min = 10 hours/month
With CI/CD: 20 deployments × 4 min = 1.3 hours/month

TIME SAVED: 8.7 hours/month per data scientist
```

**For a team of 5 data scientists:**
```
8.7 hours × 5 people = 43.5 hours/month saved
= ~5.4 working days/month
= ~65 working days/year
```

**ADDITIONAL BENEFITS:**

✅ **Consistency:** Same deployment process every time  
✅ **Traceability:** Complete audit trail automatically  
✅ **Collaboration:** Code reviews improve quality  
✅ **Confidence:** Automated testing catches errors  
✅ **Compliance:** Built-in governance controls  

**TRANSITION:** *"Now let's discuss next steps and any questions you have..."*

---

### **MINUTES 25-30: Q&A & NEXT STEPS** ⏱️ 5 min

**SCRIPT:**
> "Let me pause here. What questions do you have about what we've shown?"

**ANTICIPATED QUESTIONS & ANSWERS:**

**Q: "How long would it take to set this up for our team?"**
> A: "4-6 weeks for a full POC:
> - Week 1: Set up environments and service principals
> - Weeks 2-3: Migrate 2-3 pilot notebooks
> - Week 4: Team training on Git workflow
> - Weeks 5-6: Expand to full notebook library"

**Q: "What about our existing notebooks in Fabric?"**
> A: "We can export them to Git using the Fabric API. I'll provide a script that automates this. Typically takes a day to migrate existing notebooks."

**Q: "How do we handle secrets and credentials?"**
> A: "GitHub Secrets (encrypted) + Azure Key Vault. Your notebooks reference secrets without exposing them. I can show you the pattern."

**Q: "What if GitHub is down?"**
> A: "Your Fabric workspaces keep running normally. Deployments are queued until GitHub recovers. For emergencies, we can deploy manually using the same scripts."

**Q: "Can we customize the validation rules?"**
> A: "Absolutely. You can add custom checks for your team's standards - naming conventions, required libraries, data quality tests, etc."

**Q: "How much does this cost?"**
> A: "GitHub Actions free tier covers most teams. For your scale, estimate $50-100/month for GitHub. All Azure/Fabric costs you're already paying."

**Q: "Who maintains this?"**
> A: "Initially: DevOps team sets it up. Ongoing: Very low maintenance. Your team occasionally updates validation rules as standards evolve."

---

### **CLOSING: CONCRETE NEXT STEPS** ⏱️ 2 min

**SCRIPT:**
> "Based on what we've discussed, here's what I recommend..."

**PROPOSED TIMELINE:**

```
┌─────────────────────────────────────────────────────┐
│  WEEK 1-2: POC Setup                                │
│  ├─ Create Dev/Test/Prod Fabric workspaces          │
│  ├─ Set up GitHub repository                        │
│  ├─ Configure service principal & secrets           │
│  └─ Deliverable: Working deployment pipeline        │
├─────────────────────────────────────────────────────┤
│  WEEK 3-4: Pilot with 2 Notebooks                   │
│  ├─ Migrate 2 critical notebooks                    │
│  ├─ Test full deployment cycle                      │
│  ├─ Validate with 2 data scientists                 │
│  └─ Deliverable: Proven workflow                    │
├─────────────────────────────────────────────────────┤
│  WEEK 5: Team Training                              │
│  ├─ Git basics workshop (2 hours)                   │
│  ├─ PR workflow training (1 hour)                   │
│  ├─ Troubleshooting session (1 hour)                │
│  └─ Deliverable: Trained team                       │
├─────────────────────────────────────────────────────┤
│  WEEK 6+: Full Rollout                              │
│  ├─ Migrate remaining notebooks                     │
│  ├─ Add custom validation rules                     │
│  ├─ Integrate with team's tools                     │
│  └─ Deliverable: Production-ready CI/CD             │
└─────────────────────────────────────────────────────┘
```

**IMMEDIATE ACTIONS:**

**For NVR Team:**
1. ✅ Confirm approval to proceed with POC
2. ✅ Provide list of 2-3 pilot notebooks
3. ✅ Identify 2 data scientists for pilot
4. ✅ Provide Fabric workspace access

**For Microsoft:**
1. ✅ Send POC proposal & SOW
2. ✅ Set up initial meeting with DevOps team
3. ✅ Provide setup documentation
4. ✅ Schedule week 1 kickoff

**SUCCESS CRITERIA:**

By end of POC, you should have:
- ✅ 2-3 notebooks deploying automatically
- ✅ Full Dev → Test → Prod pipeline working
- ✅ Team comfortable with Git workflow
- ✅ Documented audit trail
- ✅ Measurable time savings

**FINAL QUESTION:**
> "Does this approach address your team's needs? Any concerns before we move to POC?"

---

## 📋 PRE-DEMO CHECKLIST

### 🔧 Technical Setup (1 hour before)

- [ ] **Repository ready**
  - [ ] All workflows committed and pushed
  - [ ] Sample notebooks validated
  - [ ] Secrets configured (or use mock values)

- [ ] **Browser tabs prepared**
  - [ ] Tab 1: GitHub repository (main page)
  - [ ] Tab 2: VS Code (or GitHub web editor)
  - [ ] Tab 3: GitHub Actions page
  - [ ] Tab 4: Fabric Dev workspace
  - [ ] Tab 5: Fabric Test workspace (optional)
  - [ ] Tab 6: This demo script

- [ ] **Code snippets ready**
  - [ ] Enhanced logging code snippet in clipboard manager
  - [ ] Git commands in text file for copy-paste

- [ ] **Backup plan**
  - [ ] Pre-recorded screen capture of full demo (in case of network issues)
  - [ ] Pre-validated PR ready to show (if live validation is slow)
  - [ ] Screenshots of key steps

### 📊 Materials Prepared

- [ ] **Demo script** (this document)
- [ ] **ROI calculator** (Excel showing time savings)
- [ ] **Architecture diagram** (Dev/Test/Prod flow)
- [ ] **POC proposal** (ready to send after demo)

### 🎯 Talking Points Memorized

- [ ] Opening hook: "Eliminate manual deployments"
- [ ] Key metric: "87% faster deployments"
- [ ] Governance: "Complete audit trail"
- [ ] Timeline: "4-6 weeks to production-ready"

---

## ⚠️ TROUBLESHOOTING DURING DEMO

### If GitHub Actions is slow:
> "While this deploys, let me explain the architecture..." (show diagram)

### If workflow fails:
> "This is actually perfect - let me show you how we'd troubleshoot this..." (show logs, error handling)

### If customer asks complex technical question:
> "Great question. Let me make note of that and provide detailed answer after the demo. For now, let me show you..."

### If running out of time:
**Skip:** Integration tests, smoke tests details  
**Keep:** PR validation, Dev deployment, Prod governance

---

## 🎯 DEMO SUCCESS METRICS

After demo, you should have:
- [ ] Customer understands end-to-end flow
- [ ] Customer sees time savings clearly
- [ ] Customer agrees to POC
- [ ] Next meeting scheduled
- [ ] POC timeline agreed upon

**GOAL:** Get verbal commitment to POC by end of call

---

## 📞 POST-DEMO FOLLOW-UP

**Within 24 hours:**
- [ ] Send demo recording
- [ ] Send this GitHub repository link
- [ ] Send POC proposal document
- [ ] Send calendar invite for kickoff meeting

**Within 48 hours:**
- [ ] Schedule technical deep-dive with DevOps team
- [ ] Provide setup documentation
- [ ] Answer any follow-up questions

---

**Good luck with your demo! 🚀**

*Remember: This isn't about showing off technology. It's about solving their problem (manual deployments) with measurable results (87% time savings).*
