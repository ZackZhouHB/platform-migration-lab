# Git Workflows & Branching Strategies

## Why This Matters for the Role

The migration isn't just Jenkins → GHA. It's also Bitbucket → GitHub. The client likely has established Git workflows that must be preserved or improved. Understanding branching strategies is essential for designing the right CI/CD triggers.

## Common Git Workflows

### 1. GitFlow (Traditional Enterprise)

```
main ─────────────────●───────────────●──────── (production releases)
                     / \             / \
release/1.0 ────────●   \  release/1.1   \
                   /     \       /         \
develop ──●──●──●──●──●───●──●──●───────────●── (integration branch)
          │  │     │        │
feature/  │  │     │        │
  auth ───●  │     │        │
  pay ───────●     │        │
  ui ──────────────●        │
hotfix/                     │
  fix-123 ──────────────────●
```

**Branches**: main, develop, feature/*, release/*, hotfix/*
**CI/CD mapping**:
- `feature/*` → run tests
- `develop` → run tests + deploy to dev
- `release/*` → run tests + deploy to staging
- `main` → deploy to production
- `hotfix/*` → fast-track to production

**Common in**: Banks, government, risk-averse enterprises
**Jenkins setup**: Multibranch pipeline with branch-specific stages

### 2. GitHub Flow (Simple, Modern)

```
main ──●──●──●──●──●──●──●──●──●── (always deployable)
       │     │        │
       │     │        └─ PR #3: fix-bug
       │     └────────── PR #2: add-payment
       └──────────────── PR #1: new-feature
```

**Branches**: main + short-lived feature branches
**CI/CD mapping**:
- `feature branch` → run tests on PR
- `main` (after merge) → deploy to production

**Common in**: SaaS companies, modern teams
**Best for GitHub Actions**: native PR triggers, branch protection, environments

### 3. Trunk-Based Development (High-Performing Teams)

```
main ──●──●──●──●──●──●──●──●──●── (everyone commits here)
       │     │
       │     └── short-lived branch (< 1 day)
       └────── short-lived branch (< 1 day)
```

**Branches**: main only (or very short-lived branches)
**CI/CD mapping**:
- Every commit → full CI + deploy behind feature flags
- Requires: feature flags, good test coverage, fast CI

**Common in**: Google, high-velocity teams

## Branch Protection Rules (GitHub)

Essential for migration — replacing Jenkins job permissions:

```
Repository Settings → Branches → Branch protection rules

✅ Require pull request before merging
  ✅ Required approvals: 1
  ✅ Dismiss stale reviews on new commits
✅ Require status checks to pass
  ✅ ci / test (required)
  ✅ ci / lint (required)
✅ Require linear history (no merge commits)
✅ Restrict who can push to matching branches
```

## CODEOWNERS

Automatically request reviews from the right team:

```
# .github/CODEOWNERS

# Default
* @platform-team

# Service ownership
/services/api-gateway/    @api-team
/services/payment-service/ @payments-team
/services/user-service/    @identity-team
/services/frontend/        @frontend-team

# Shared libs need platform review
/libs/                     @platform-team

# CI/CD changes need platform review
/.github/                  @platform-team
/Jenkinsfiles/             @platform-team
```

## Git Workflow in This Lab

We'll use **GitHub Flow** (the most natural fit for GitHub Actions):

1. `main` is always deployable
2. Create feature branches for changes
3. Open PRs → CI runs automatically
4. Merge to main → deploy workflows trigger
5. Environments (dev/staging/prod) controlled via GitHub Environments

This mirrors what the client will likely adopt post-migration.
