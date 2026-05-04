# Platform Migration Lab

> Jenkins → GitHub Actions migration lab with monorepo CI/CD, AI-assisted DevOps, and hands-on pipeline migration.

## What Is This?

A complete hands-on lab simulating an enterprise CI/CD migration from **Jenkins + Bitbucket** to **GitHub + GitHub Actions**, built around a realistic **monorepo** with multiple services.

## Architecture

```
platform-migration-lab/
│
├── jenkins/                          # The "legacy" — Jenkins Docker setup
│   ├── docker-compose.yml            # Jenkins controller + Docker agent
│   ├── Dockerfile                    # Custom Jenkins with plugins
│   ├── casc/                         # Jenkins Configuration as Code
│   └── shared-libraries/             # Groovy shared libs (what we migrate FROM)
│
├── services/                         # Monorepo application code
│   ├── api-gateway/                  # Node.js service
│   ├── payment-service/              # Python service
│   ├── user-service/                 # Go service
│   └── frontend/                     # React app
│
├── libs/                             # Shared libraries used by services
│   ├── common-utils/
│   └── test-helpers/
│
├── Jenkinsfiles/                     # Legacy Jenkins pipelines (migrate FROM)
│
├── .github/
│   ├── workflows/                    # Migrated GitHub Actions (migrate TO)
│   └── actions/                      # Custom reusable actions
│
├── scripts/
│   ├── migration/                    # Python: Jenkinsfile parser, GHA generator
│   ├── ai/                           # AI: PR summariser, build RCA, test selector
│   └── monorepo/                     # Monorepo: change detection, dependency graph
│
├── terraform/                        # IaC for runners (bonus)
└── docs/                             # Fundamentals, migration guides, runbooks
    ├── fundamentals/                 # Jenkins 101, GHA 101, Git workflows
    ├── migration/                    # Migration plan, mapping, runbook
    └── monorepo/                     # Monorepo strategies, tools comparison
```

## Learning Path

| Phase | Focus | Status |
|-------|-------|--------|
| 0 | Environment Setup (Docker Jenkins, tooling) | 🔲 |
| 1 | Jenkins Deep Dive — build the legacy pipelines | 🔲 |
| 2 | GitHub Actions Deep Dive — build the target | 🔲 |
| 3 | The Migration — Jenkins → GHA, service by service | 🔲 |
| 4 | Monorepo Optimisation — change detection, caching, builds | 🔲 |
| 5 | AI Integration — LLM-assisted DevOps tooling | 🔲 |
| 6 | Security & Compliance | 🔲 |
| 7 | Portfolio & Interview Prep | 🔲 |

## Quick Start

```bash
# 1. Start Jenkins locally
cd jenkins && docker compose up -d

# 2. Access Jenkins at http://localhost:8080
#    Default admin password: see docker logs

# 3. GitHub Actions workflows run automatically on push
```

## Prerequisites

- Docker Desktop
- GitHub account with Actions enabled
- Python 3.x
- Node.js 20+
- `gh` CLI, `act`, `jq`, `yq`
