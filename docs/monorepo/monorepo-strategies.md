# Monorepo CI/CD Strategies

## What Is a Monorepo?

A single Git repository containing multiple projects, services, or packages. Examples:
- Google (billions of lines of code, one repo)
- Meta, Uber, Airbnb, Stripe
- Many enterprises with 5-50 services in one repo

```
monorepo/
├── services/
│   ├── api-gateway/        # Node.js
│   ├── payment-service/    # Python
│   ├── user-service/       # Go
│   └── frontend/           # React
├── libs/
│   ├── common-utils/       # Shared by multiple services
│   └── test-helpers/       # Shared test utilities
└── infrastructure/
    └── terraform/
```

## The Core Problem

**Without optimisation**: Every push triggers a full CI for every service.
- 4 services × 10 min each = 40 min CI per commit
- Wasted compute, slow feedback, expensive

**With optimisation**: Only build/test what changed.
- Change `services/payment-service/` → only payment CI runs (~10 min)
- This is the #1 skill for monorepo CI/CD

## Strategy 1: Path-Based Triggers (Native GitHub Actions)

The simplest approach — built into GitHub Actions:

```yaml
# .github/workflows/payment-service.yml
name: Payment Service CI
on:
  push:
    paths:
      - 'services/payment-service/**'
      - 'libs/common-utils/**'        # Shared dependency
      - '.github/workflows/payment-service.yml'
  pull_request:
    paths:
      - 'services/payment-service/**'
      - 'libs/common-utils/**'
```

**Pros**: Simple, no extra tools, native support
**Cons**: Static — you must manually list all dependency paths. Breaks when dependency graph changes.

## Strategy 2: Dynamic Change Detection (dorny/paths-filter)

Detect changes at runtime and conditionally run jobs:

```yaml
name: Monorepo CI
on: [push, pull_request]

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      api: ${{ steps.filter.outputs.api }}
      payment: ${{ steps.filter.outputs.payment }}
      user: ${{ steps.filter.outputs.user }}
      frontend: ${{ steps.filter.outputs.frontend }}
      shared: ${{ steps.filter.outputs.shared }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            api:
              - 'services/api-gateway/**'
            payment:
              - 'services/payment-service/**'
            user:
              - 'services/user-service/**'
            frontend:
              - 'services/frontend/**'
            shared:
              - 'libs/**'

  build-api:
    needs: detect-changes
    if: needs.detect-changes.outputs.api == 'true' || needs.detect-changes.outputs.shared == 'true'
    uses: ./.github/workflows/reusable-build.yml
    with:
      service: api-gateway

  build-payment:
    needs: detect-changes
    if: needs.detect-changes.outputs.payment == 'true' || needs.detect-changes.outputs.shared == 'true'
    uses: ./.github/workflows/reusable-build.yml
    with:
      service: payment-service
```

**Pros**: Dynamic, handles shared libs, single workflow orchestrates all
**Cons**: Still manual dependency mapping, doesn't understand code-level imports

## Strategy 3: Nx (Intelligent Build System)

[Nx](https://nx.dev) understands your dependency graph and only builds/tests affected projects.

```bash
# Install
npm install -g nx

# Detect affected projects based on git diff
nx affected -t build      # Only build what changed
nx affected -t test       # Only test what changed
nx affected -t lint       # Only lint what changed

# Visualise dependency graph
nx graph
```

**How it works**:
1. Nx reads `project.json` or `package.json` in each project
2. Analyses import statements to build a dependency graph
3. Compares current branch to `main` to find changed files
4. Calculates which projects are **affected** (changed + dependents)
5. Runs only those

**GitHub Actions integration**:
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0     # Need full history for nx affected
      - uses: actions/setup-node@v4
      - run: npm ci
      - uses: nrwl/nx-set-shas@v4   # Sets base/head SHAs for comparison
      - run: npx nx affected -t lint test build --parallel=3
```

**Nx Remote Cache**: Cache build outputs across CI runs and developer machines:
```bash
# Build output cached — next run skips unchanged projects
nx build payment-service   # 45s first time
nx build payment-service   # 0.2s (cache hit)
```

**Pros**: Understands real dependency graph, remote caching, parallel execution
**Cons**: Requires Nx setup, best for JS/TS ecosystems (but supports others)

## Strategy 4: Turborepo

Similar to Nx but simpler, focused on monorepo task running:

```json
// turbo.json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "test": {
      "dependsOn": ["build"]
    },
    "lint": {}
  }
}
```

```bash
# Only run affected tasks
turbo run build --filter=...[origin/main]

# Parallel with dependency awareness
turbo run build test lint --parallel
```

**Pros**: Simpler than Nx, good remote caching (Vercel), fast
**Cons**: Primarily JS/TS focused, less graph intelligence than Nx

## Strategy 5: Bazel (Google-Scale)

Build system designed for massive monorepos. Language-agnostic.

```python
# BUILD file
java_library(
    name = "user-service",
    srcs = glob(["src/**/*.java"]),
    deps = [
        "//libs/common-utils",
        "@maven//:com_google_guava_guava",
    ],
)
```

```bash
# Build only what changed
bazel build //services/payment-service/...

# Test only affected targets
bazel test //... --test_tag_filters=-manual
```

**Pros**: Language-agnostic, hermetic builds, massive scale, Google-proven
**Cons**: Steep learning curve, complex setup, overkill for <100 services

## Strategy 6: Custom Change Detection Script

Build your own (good for interviews — shows deep understanding):

```python
#!/usr/bin/env python3
"""Detect affected services based on git diff and a dependency map."""

import subprocess
import json
import sys

# Define dependency graph
DEPS = {
    "api-gateway": ["libs/common-utils"],
    "payment-service": ["libs/common-utils"],
    "user-service": ["libs/common-utils"],
    "frontend": ["libs/common-utils", "libs/test-helpers"],
}

SERVICE_PATHS = {
    "api-gateway": "services/api-gateway",
    "payment-service": "services/payment-service",
    "user-service": "services/user-service",
    "frontend": "services/frontend",
}

def get_changed_files(base_ref="origin/main"):
    result = subprocess.run(
        ["git", "diff", "--name-only", base_ref],
        capture_output=True, text=True
    )
    return result.stdout.strip().split("\n")

def get_affected_services(changed_files):
    affected = set()
    for service, path in SERVICE_PATHS.items():
        # Direct change
        if any(f.startswith(path) for f in changed_files):
            affected.add(service)
        # Dependency change
        for dep in DEPS.get(service, []):
            if any(f.startswith(dep) for f in changed_files):
                affected.add(service)
    return affected

if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    changed = get_changed_files(base)
    affected = get_affected_services(changed)
    print(json.dumps({"affected": sorted(affected), "changed_files": changed}))
```

**Pros**: Full control, no external dependencies, great interview demo
**Cons**: Must maintain dependency map manually, doesn't scale to hundreds of services

## Strategy Comparison

| Strategy | Complexity | Languages | Scale | Best For |
|----------|-----------|-----------|-------|----------|
| Path triggers | Low | Any | Small (< 10 services) | Simple monorepos |
| dorny/paths-filter | Low-Med | Any | Small-Med | GHA-native approach |
| Nx | Medium | JS/TS (+ others) | Med-Large | Node.js monorepos |
| Turborepo | Low-Med | JS/TS | Med | Simpler Node.js monorepos |
| Bazel | High | Any | Very Large | Google-scale, multi-language |
| Custom script | Medium | Any | Med | Full control, interview demos |

## Build Caching Strategies

### 1. GitHub Actions Cache
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      node_modules
    key: deps-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
```

### 2. Docker Layer Caching
```yaml
- uses: docker/build-push-action@v5
  with:
    context: services/api-gateway
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### 3. Nx/Turborepo Remote Cache
Build outputs cached remotely — if another developer or CI run already built the same code, skip it.

### 4. Gradle/Maven Build Cache
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
    key: gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
```

## Concurrency Control (Preventing Waste)

```yaml
# Cancel in-progress runs for the same PR
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

```yaml
# Per-service concurrency (don't cancel across services)
concurrency:
  group: payment-${{ github.ref }}
  cancel-in-progress: true
```

## Cost Control

1. **Only run what changed** (strategies above)
2. **Cancel duplicate runs** (concurrency groups)
3. **Set timeouts** on every job:
   ```yaml
   jobs:
     test:
       timeout-minutes: 15
   ```
4. **Use caching** aggressively
5. **Avoid full checkout** when possible:
   ```yaml
   - uses: actions/checkout@v4
     with:
       fetch-depth: 1    # Shallow clone (faster)
   ```
6. **Use smaller runners** for simple tasks
7. **Monitor usage**: Settings → Billing → Actions

## What to Implement in This Lab

We'll implement multiple strategies in our monorepo:

1. ✅ **Path-based triggers** — baseline for each service workflow
2. ✅ **dorny/paths-filter** — orchestrator workflow with dynamic detection
3. ✅ **Custom Python script** — `scripts/monorepo/detect_changes.py`
4. ✅ **Nx integration** — for the Node.js services (api-gateway, frontend)
5. ✅ **Docker layer caching** — for container builds
6. ✅ **Concurrency + cost controls** — on all workflows
