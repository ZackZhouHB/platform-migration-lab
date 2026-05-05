# Session Handoff — Platform Migration Lab

> Last updated: 2026-05-05 20:10 AEST

## Context

Hongbo (ZackZhouHB) is preparing for a **Platform Engineer** interview focused on **Jenkins → GitHub Actions migration**, monorepo CI/CD, and AI-assisted DevOps.

- **JD file**: `/Users/zz/zz/Documents/jenkins/jd.txt`
- **JD analysis**: `/Users/zz/zz/Documents/jenkins/analysis.md`
- **CV**: `/Users/zz/zz/Documents/jenkins/Hongbo Zhou_Resume_v2.pdf`
- **Full plan**: Session plan.md (in session state folder)

---

## Existing Experience (Prior to This Lab)

### Jenkins — Already Have (from zack-gitops-project)

Hongbo has **real Jenkins CI/CD experience** documented in two blog posts and a working Jenkinsfile. This is NOT on his CV but should be mentioned in interviews.

**Blog Post 80** — Universal CI Pipeline (https://zackblog.work/post/80/):
- ✅ Custom Jenkins Docker image — baked in: Docker CLI, Terraform, kubectl, Trivy, AWS CLI, Ansible
- ✅ Docker-in-Docker setup (socket mount + group-add)
- ✅ Multi-language build detection — Node.js, Java, Python, Go, .NET, PHP, Ruby, Rust, iOS, Android
- ✅ Security scanning — Trivy (Docker image scan) + Snyk (code analysis)
- ✅ Advanced pipeline patterns — try/catch, if/else, timeouts, env vars, post actions
- ✅ Docker build → push to DockerHub with tagging
- ✅ Email notifications on success/failure

**Blog Post 81** — CD Pipeline with Terraform & Ansible (https://zackblog.work/post/81/):
- ✅ Jenkins CD pipeline — Terraform provision EC2 → Ansible deploy Docker → validate with curl
- ✅ `withCredentials` — SSH keys, AWS credentials, DockerHub tokens
- ✅ Terraform init/apply within pipeline stages
- ✅ Ansible playbook execution from Jenkins
- ✅ EC2 readiness check (SSH retry loop)
- ✅ Web validation (curl health check after deploy)
- ✅ Multi-destination design (EC2, ECS, EKS)

**Jenkinsfile** (`/Users/zz/zz/Documents/zack-gitops-project/Jenkinsfile`):
- 248-line declarative pipeline with 12+ stages
- Terraform + Ansible + Docker + AWS integration

**What's MISSING from Jenkins experience:**
- ❌ Shared libraries (@Library, Groovy vars/)
- ❌ Multibranch pipeline (auto branch discovery)
- ❌ Jenkins agents (distributed builds, labels)
- ❌ Parallel stages
- ❌ Jenkins Configuration as Code (JCasC)
- ❌ Parameterised builds (input step, choice params)

### GitHub Actions — Already Have

**Workflow** (`/Users/zz/zz/Documents/zack-gitops-project/.github/workflows/zack-django.yaml`):
- ✅ Push + PR triggers with **path filters** (`django_project/**`)
- ✅ Branch filters (`editing`, `main`)
- ✅ Docker Buildx setup + multi-tag build
- ✅ Docker push to DockerHub
- ✅ GitHub Secrets (AWS keys, DockerHub token, SSH key)
- ✅ AWS credentials action (`aws-actions/configure-aws-credentials`)
- ✅ SSH remote deploy (`appleboy/ssh-action`)

**What's MISSING from GHA experience:**
- ❌ Matrix builds (multi-version testing)
- ❌ Reusable workflows (`workflow_call`)
- ❌ Composite actions
- ❌ GitHub Environments with approval gates
- ❌ Caching (`actions/cache`)
- ❌ Concurrency control
- ❌ Permissions block (least privilege)
- ❌ Self-hosted runners
- ❌ Custom JS actions
- ❌ Artifacts upload/download

### Also Strong On (from CV + projects)
- ✅ AWS (DOP, SAP, MLA certs) — deep hands-on
- ✅ Kubernetes (CKA, CKS) — EKS, Karpenter, Helm, ArgoCD
- ✅ Terraform, CloudFormation, Ansible
- ✅ AI/LLM — RAG, Bedrock, vllm, LangChain (production experience)
- ✅ Python, Bash scripting
- ✅ Docker & containerisation
- ✅ Security & compliance (APRA, Security Hub)

### Revised Gap Assessment

| Area | Level | What's Needed |
|------|-------|---------------|
| Jenkins pipelines | **Intermediate** | Add: shared libs, multibranch, agents, parallel |
| GitHub Actions | **Beginner-Intermediate** | Add: matrix, reusable workflows, environments, caching, permissions |
| Monorepo CI/CD | **Zero** | Full coverage needed (being built in lab) |
| Jenkins → GHA Migration | **Zero** | Core skill — Phase 3 of lab |
| AI-assisted DevOps | **Strong AI, Zero DevOps application** | Apply existing LLM skills to CI/CD domain |

---

## What We Built in This Lab

### GitHub Repo
- **URL**: https://github.com/ZackZhouHB/platform-migration-lab
- **Visibility**: Public (free unlimited GHA minutes)
- **Git remote**: HTTPS (SSH key belongs to TinaQi87, so we used `gh auth setup-git` for HTTPS push)
- **`workflow` scope**: Added to gh token via `gh auth refresh -s workflow`

### Jenkins (Remote Server)
- **Running at**: http://192.168.50.61:8080 (moved from local Mac to remote server)
- **Remote server**: root@192.168.50.61 (Ubuntu 24.04, i7-12700KF, 32GB RAM, 831GB disk)
- **Lab files on remote**: `/opt/platform-migration-lab/`
- **Login**: admin / admin
- **Start**: `ssh root@192.168.50.61 'cd /opt/platform-migration-lab/jenkins && docker compose up -d'`
- **Stop**: `ssh root@192.168.50.61 'cd /opt/platform-migration-lab/jenkins && docker compose down'`
- **JCasC**: Applied (system message, admin user, 2 executors)
- **Plugins**: Pipeline, Git, Docker, Credentials, Job DSL, CasC, Timestamper
- **Note**: Blue Ocean and nodejs plugins removed (compatibility issues). Filesystem SCM for shared libs removed from JCasC — shared libs need manual config or Job DSL.
- **Note**: Removed `credsStore: desktop.exe` from remote Docker config to fix build issue.

### Architecture Split
| Workload | Where | Why |
|----------|-------|-----|
| Code editing & git | Mac (local) | Keep Mac light and clean |
| GitHub Actions CI | GitHub (cloud) | Free, unlimited minutes (public repo) |
| Jenkins server | Remote server (192.168.50.61) | Heavy workload offloaded |
| Docker builds | Remote server | Heavy workload offloaded |
| Lightweight tests | Mac (local) | Quick feedback (node/python/go) |

### Monorepo Structure (4 services)
| Service | Language | Has Tests | Has Dockerfile | Has Jenkinsfile |
|---------|----------|-----------|----------------|-----------------|
| api-gateway | Node.js/Express | ✅ | ✅ | ✅ (declarative) |
| payment-service | Python | ✅ | ✅ | ✅ (scripted, parallel, approval) |
| user-service | Go | ✅ | ❌ | ✅ (declarative) |
| frontend | Node.js | ✅ | ❌ | ✅ (declarative, artifact archive) |

- **Shared lib**: `libs/common-utils/` (JS) — changes trigger ALL service builds
- **All 11 tests pass locally** (verified)

### Jenkins Shared Libraries (Groovy)
Located in `jenkins/shared-libraries/vars/`:
- `buildDocker.groovy` — build & tag Docker images
- `runTests.groovy` — run tests for node/python/go
- `deployToEnv.groovy` — deploy with optional approval gate
- `notifySlack.groovy` — simulated Slack notifications

### GitHub Actions Workflows
| Workflow | Purpose | Status |
|----------|---------|--------|
| `ci-orchestrator.yml` | Monorepo change detection → selective builds | ✅ First run passed |
| `reusable-node-build.yml` | Reusable: lint → test → build for Node.js services | ✅ Working |
| `reusable-python-build.yml` | Reusable: lint → test → build for Python services | ✅ Created (not yet triggered) |

**First CI run** (ID: 25326006390): Change detection correctly identified only `api-gateway` changed, built only that service, skipped the rest. This is the core monorepo pattern.

### Documentation Created
- `docs/fundamentals/jenkins-101.md` — Jenkins concepts, Jenkinsfile syntax, shared libs, plugins, enterprise architecture
- `docs/fundamentals/github-actions-101.md` — Events, jobs, matrix, reusable workflows, composite actions, secrets, permissions
- `docs/fundamentals/git-workflows.md` — GitFlow vs GitHub Flow vs Trunk-based, branch protection, CODEOWNERS
- `docs/monorepo/monorepo-strategies.md` — 6 strategies compared: path triggers, dorny/paths-filter, Nx, Turborepo, Bazel, custom script

### Other Files
- `scripts/monorepo/detect_changes.py` — Custom Python change detector (Strategy 6)
- `.github/CODEOWNERS` — Service ownership mapping
- `.gitignore` — Standard exclusions

### Tools Installed
- `act` (v0.2.88) — local GitHub Actions runner
- `jq` — JSON processor
- `yq` — YAML processor
- `pymupdf` — Python PDF parser (installed via pip3 --break-system-packages)

---

## System Notes

### Mac (local — coding only)
- **Machine**: Apple M5, 10 cores, 16GB RAM (Docker set to 8GB)
- **Disk**: 275GB free
- **Docker**: No Jenkins running locally anymore — offloaded to remote
- **Reclaimable Docker space**: ~14.5GB build cache (`docker builder prune`)

### Remote Server (192.168.50.61 — Docker workloads)
- **Machine**: Intel i7-12700KF, 20 threads, 32GB RAM
- **Disk**: 831GB free
- **OS**: Ubuntu 24.04 LTS
- **Docker**: 28.5.1, Jenkins + 8 other containers running
- **SSH**: `ssh root@192.168.50.61` (key-based, no password)
- **Lab path**: `/opt/platform-migration-lab/`

---

## Progress: 11/39 Tasks Done (28%)

| Phase | Done | Total | Status |
|-------|------|-------|--------|
| 0: Environment Setup | 3 | 3 | ✅ Complete |
| 1: Jenkins Deep Dive | 4 | 6 | 🟡 Agents + Multibranch remain |
| 2: GitHub Actions | 3 | 8 | 🟡 Matrix, composite, environments, self-hosted, JS action |
| 3: The Migration | 0 | 6 | 🔲 Not started |
| 4: Monorepo | 1 | 4 | 🟡 Path triggers done, change detection/caching/cost remain |
| 5: AI Integration | 0 | 4 | 🔲 Not started |
| 6: Security | 0 | 4 | 🔲 Not started |
| 7: Portfolio | 0 | 4 | 🔲 Not started |

---

## What To Do Next (Revised Priority — Based on Actual Gaps)

### Batch 1 — GHA Features You're Missing (Quick Wins)
These are features your existing `zack-django.yaml` doesn't use but the role requires:
1. **p2-matrix-builds** — Test across Node 18/20/22 (you already know triggers/secrets, this is just adding `strategy.matrix`)
2. **p2-composite-action** — Build reusable step-level action (new concept for you)
3. **p2-environments** — GitHub Environments with approval gates (replaces Jenkins `input` step)
4. **p2-self-hosted** — Register remote server as GHA runner (shows runner architecture knowledge)

### Batch 2 — Jenkins Features You're Missing
You have CI/CD pipelines but not enterprise patterns:
5. **p1-agents** — Docker agent config (you already use `agent any`, need to learn `agent { docker {} }` and labels)
6. **p1-multibranch** — Auto-discover branches (how enterprise Jenkins actually works)

### Batch 3 — The Migration (Core Interview Skill)
This is what the role IS — migrating Jenkins to GHA:
7. **p3-inventory-script** — Python parser that reads your Jenkinsfiles → JSON report (combines your Python skills + Jenkins knowledge)
8. **p3-migrate-shared-libs** — Convert Groovy shared libs → reusable workflows/composite actions
9. **p3-mapping-doc** — Document the migration: Jenkins concept → GHA equivalent, risk, rollback
10. **p3-migrate-services** — Actually migrate each service, run both in parallel
11. **p3-migrate-creds** — Map Jenkins credentials to GitHub secrets
12. **p3-parallel-validation** — Compare outputs from both systems

### Batch 4 — AI Integration (Your Strength, Applied to DevOps)
You already have LLM/RAG skills — just apply them:
13. **p5-jenkinsfile-analyzer** — Python+LLM script to analyse Jenkinsfiles and generate GHA YAML
14. **p5-pr-summary-bot** — GHA workflow that posts AI-generated PR summaries
15. **p5-build-rca** — AI root-cause analysis for build failures
16. **p5-test-selection** — Intelligent test selection based on git diff

### Batch 5 — Security & Polish
17. **p6-branch-protection** — Configure rules via `gh` CLI (quick)
18. **p6-permissions-audit** — Minimal permissions on all workflows
19. **p6-secrets-strategy** — Document Jenkins→GHA secrets mapping, OIDC
20. **p6-supply-chain** — Pin action versions to SHA, dependency review
21. **p4-caching** — Build caching strategy (npm, Docker layers)
22. **p4-cost-control** — Concurrency groups, timeouts, cancel in-progress

### Batch 6 — Portfolio & Interview
23. **p7-documentation** — README, architecture diagram, runbook
24. **p7-demo-script** — 10-min live demo script
25. **p7-interview-stories** — Answers for all 5 employer questions
26. **p7-theory-gaps** — Enterprise features, runner fleet, billing, compliance

### Blocked (need earlier tasks):
- Phase 3 migration (Batch 3) needs Batch 1+2 completion
- Phase 5 AI (Batch 4) needs the inventory script from Batch 3
- Phase 7 portfolio (Batch 6) needs most other phases

---

## How To Resume

```bash
# 1. Navigate to the lab
cd /Users/zz/zz/Documents/platform-migration-lab

# 2. Start Jenkins on remote (if not running)
ssh root@192.168.50.61 'cd /opt/platform-migration-lab/jenkins && docker compose up -d'

# 3. Verify Jenkins
curl -s -u admin:admin http://192.168.50.61:8080/api/json | jq '.mode'

# 4. Verify GitHub Actions
gh run list --repo ZackZhouHB/platform-migration-lab --limit 3

# 5. Sync lab files to remote (after local changes to jenkins/ or Jenkinsfiles/)
rsync -avz --exclude '.git' --exclude 'node_modules' /Users/zz/zz/Documents/platform-migration-lab/ root@192.168.50.61:/opt/platform-migration-lab/

# 6. Tell Copilot to continue
# "Continue with the platform-migration-lab. Pick up from the session handoff."
```
