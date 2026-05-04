# GitHub Actions Fundamentals

## What Is GitHub Actions?

GitHub's built-in CI/CD platform. Workflows are YAML files triggered by GitHub events (push, PR, schedule, etc.). No server to manage — GitHub runs it for you.

## Core Concepts

### 1. Workflow
A YAML file in `.github/workflows/`. Each file is an independent workflow.

```yaml
name: CI Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test
```

### 2. Events (Triggers)
```yaml
on:
  push:                          # Any push
    branches: [main, develop]    # Only these branches
    paths: ['services/api/**']   # Only when these files change
  
  pull_request:
    types: [opened, synchronize, reopened]
  
  workflow_dispatch:              # Manual trigger
    inputs:
      environment:
        type: choice
        options: [dev, staging, prod]
  
  schedule:
    - cron: '0 2 * * 1'         # Every Monday at 2am UTC
  
  workflow_run:                   # After another workflow completes
    workflows: [Build]
    types: [completed]
```

### 3. Jobs & Steps
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4    # Action (reusable)
      - run: npm run lint             # Shell command

  test:
    needs: lint                       # Dependency chain
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test

  deploy:
    needs: [lint, test]               # Wait for both
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploying..."
```

### 4. Runners
Where jobs execute:
- **GitHub-hosted**: `ubuntu-latest`, `macos-latest`, `windows-latest` — managed by GitHub
- **Self-hosted**: your own machine — `runs-on: self-hosted`
- **Larger runners**: GitHub-managed with more CPU/RAM (paid)

### 5. Actions (The Ecosystem)
Reusable units from the marketplace:
```yaml
steps:
  - uses: actions/checkout@v4              # Official
  - uses: docker/build-push-action@v5      # Docker official
  - uses: dorny/paths-filter@v3            # Community
  - uses: ./.github/actions/my-action      # Local (in your repo)
```

**Always pin to SHA for security**:
```yaml
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
```

### 6. Matrix Strategy
Run the same job across multiple configurations:
```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        node: [18, 20, 22]
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm test
```

### 7. Secrets & Environments
```yaml
jobs:
  deploy:
    environment: production        # Links to GitHub Environment
    runs-on: ubuntu-latest
    steps:
      - run: deploy.sh
        env:
          API_KEY: ${{ secrets.API_KEY }}           # Repo secret
          AWS_ROLE: ${{ secrets.AWS_DEPLOY_ROLE }}   # Environment secret
```

**Environments** can require:
- Manual approval (required reviewers)
- Wait timers
- Branch restrictions (only `main` can deploy to prod)

### 8. Reusable Workflows
The GHA equivalent of Jenkins shared libraries:

**Define** (`.github/workflows/reusable-build.yml`):
```yaml
name: Reusable Build
on:
  workflow_call:
    inputs:
      service:
        required: true
        type: string
      node-version:
        required: false
        type: string
        default: '20'
    secrets:
      DEPLOY_KEY:
        required: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
      - run: cd services/${{ inputs.service }} && npm ci && npm run build
```

**Call**:
```yaml
jobs:
  build-api:
    uses: ./.github/workflows/reusable-build.yml
    with:
      service: api-gateway
    secrets:
      DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
```

### 9. Composite Actions
Reusable at the step level (finer-grained than reusable workflows):

**Define** (`.github/actions/setup-and-test/action.yml`):
```yaml
name: Setup and Test
description: Checkout, install deps, run tests
inputs:
  working-directory:
    required: true
  node-version:
    required: false
    default: '20'
outputs:
  coverage:
    description: Test coverage percentage
    value: ${{ steps.test.outputs.coverage }}

runs:
  using: composite
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
    - shell: bash
      working-directory: ${{ inputs.working-directory }}
      run: npm ci
    - id: test
      shell: bash
      working-directory: ${{ inputs.working-directory }}
      run: |
        npm test -- --coverage
        echo "coverage=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')" >> $GITHUB_OUTPUT
```

### 10. Caching
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: npm-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      npm-${{ runner.os }}-
```

### 11. Artifacts
```yaml
# Upload
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/
    retention-days: 7

# Download (in another job)
- uses: actions/download-artifact@v4
  with:
    name: build-output
```

### 12. Concurrency Control
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true   # Cancel old runs when new commit pushed
```

### 13. Permissions (Least Privilege)
```yaml
permissions:
  contents: read
  pull-requests: write
  id-token: write    # Needed for OIDC
```

**Best practice**: Set `permissions: read-all` at the top, then grant specific permissions per job.

## Workflow Execution Model

```
GitHub Event (push/PR/schedule/manual)
    │
    ▼
┌─────────────────────────────────┐
│  .github/workflows/*.yml         │
│  (all matching workflows run)    │
└──────────────┬──────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼───┐           ┌───▼───┐
│ Job A │           │ Job B │    ← Jobs run in parallel by default
│       │           │       │       unless `needs:` creates dependency
└───┬───┘           └───┬───┘
    │                   │
┌───▼───┐           ┌───▼───┐
│Step 1 │           │Step 1 │    ← Steps run sequentially within a job
│Step 2 │           │Step 2 │
│Step 3 │           │Step 3 │
└───────┘           └───────┘
```

## GitHub Actions vs Jenkins: Mental Model Shift

| Concept | Jenkins Thinking | GitHub Actions Thinking |
|---------|-----------------|----------------------|
| Server | "I manage my Jenkins server" | "There is no server — GitHub runs it" |
| Config | "I configure jobs in the UI" | "Everything is YAML in the repo" |
| Plugins | "I install plugins on the server" | "I reference actions in YAML" |
| Agents | "I provision and maintain agents" | "Runners are ephemeral and disposable" |
| Shared code | "I write Groovy shared libraries" | "I create reusable workflows + composite actions" |
| Secrets | "I store in Jenkins credential store" | "I use GitHub Secrets or OIDC federation" |
| Approval | "I use input step to pause pipeline" | "I use Environment with required reviewers" |
| Debugging | "I SSH into agent and check" | "I read logs in Actions tab or use tmate for SSH" |
