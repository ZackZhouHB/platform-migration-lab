# Session Handoff — Platform Migration Lab

> Last updated: 2026-05-05 15:57 AEST

## Context

Hongbo (ZackZhouHB) is preparing for a **Platform Engineer** interview focused on **Jenkins → GitHub Actions migration**, monorepo CI/CD, and AI-assisted DevOps. His CV is strong on AWS/K8s/Terraform/AI but has **no Jenkins or GitHub Actions experience listed** — that's the main gap to close. The employer saw his AI/LLM skills as a differentiator and called him for interview.

- **JD file**: `/Users/zz/zz/Documents/jenkins/jd.txt`
- **JD analysis**: `/Users/zz/zz/Documents/jenkins/analysis.md`
- **CV**: `/Users/zz/zz/Documents/jenkins/Hongbo Zhou_Resume_v2.pdf`
- **Full plan**: Session plan.md (in session state folder)

---

## What We Built

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

## What To Do Next (Priority Order)

### Ready now (no blockers):
1. **p2-matrix-builds** — Add matrix build workflow (Node 18/20/22). Quick win.
2. **p2-environments** — Set up GitHub Environments (dev/staging/prod) with approval gates
3. **p2-composite-action** — Build the `setup-and-test` composite action
4. **p3-inventory-script** — Python Jenkinsfile parser (shows automation + AI-adjacent skill)
5. **p1-agents** — Configure Docker agent for Jenkins
6. **p1-multibranch** — Set up multibranch pipeline in Jenkins
7. **p2-self-hosted** — Register Mac as GHA self-hosted runner
8. **p6-branch-protection** — Configure branch protection rules

### Blocked (need earlier tasks):
- Phase 3 migration tasks need Phase 1+2 completion
- Phase 5 AI tasks need the inventory script (p3)
- Phase 7 portfolio needs most other phases

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
