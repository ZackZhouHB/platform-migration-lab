#!/usr/bin/env python3
"""
Monorepo Change Detector — Custom script for detecting affected services.

This is the "custom approach" (Strategy 6 from docs/monorepo/monorepo-strategies.md).
Demonstrates deep understanding of dependency-based builds without external tools.

Usage:
    python3 detect_changes.py                    # Compare against origin/main
    python3 detect_changes.py origin/develop     # Compare against specific ref
    python3 detect_changes.py HEAD~1             # Compare against previous commit
"""

import subprocess
import json
import sys
import os

# Service registry: each service and its source paths
SERVICES = {
    "api-gateway": {
        "paths": ["services/api-gateway"],
        "language": "node",
        "dockerfile": "services/api-gateway/Dockerfile",
    },
    "payment-service": {
        "paths": ["services/payment-service"],
        "language": "python",
        "dockerfile": "services/payment-service/Dockerfile",
    },
    "user-service": {
        "paths": ["services/user-service"],
        "language": "go",
        "dockerfile": None,
    },
    "frontend": {
        "paths": ["services/frontend"],
        "language": "node",
        "dockerfile": None,
    },
}

# Dependency graph: service → list of shared dependency paths
DEPENDENCIES = {
    "api-gateway": ["libs/common-utils"],
    "payment-service": ["libs/common-utils"],
    "user-service": ["libs/common-utils"],
    "frontend": ["libs/common-utils", "libs/test-helpers"],
}

# Infrastructure paths that should trigger ALL services
GLOBAL_TRIGGERS = [
    ".github/workflows/ci-orchestrator.yml",
    "scripts/monorepo/",
]


def get_changed_files(base_ref: str = "origin/main") -> list[str]:
    """Get list of changed files compared to base ref."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref],
            capture_output=True, text=True, check=True
        )
        files = [f for f in result.stdout.strip().split("\n") if f]
        return files
    except subprocess.CalledProcessError:
        # If base ref doesn't exist (first commit), return all files
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, check=True
        )
        return [f for f in result.stdout.strip().split("\n") if f]


def is_global_change(changed_files: list[str]) -> bool:
    """Check if any changed file triggers all services."""
    for f in changed_files:
        for trigger in GLOBAL_TRIGGERS:
            if f.startswith(trigger):
                return True
    return False


def get_affected_services(changed_files: list[str]) -> dict:
    """Determine which services are affected by the changes."""
    affected = {}

    # Check for global triggers
    if is_global_change(changed_files):
        for service in SERVICES:
            affected[service] = {
                "reason": "global_trigger",
                "trigger_files": [f for f in changed_files if any(f.startswith(t) for t in GLOBAL_TRIGGERS)],
            }
        return affected

    for service, config in SERVICES.items():
        trigger_files = []
        reason = None

        # Check direct changes
        for f in changed_files:
            for path in config["paths"]:
                if f.startswith(path):
                    trigger_files.append(f)
                    reason = "direct_change"

        # Check dependency changes
        for f in changed_files:
            for dep_path in DEPENDENCIES.get(service, []):
                if f.startswith(dep_path):
                    trigger_files.append(f)
                    if reason is None:
                        reason = "dependency_change"
                    elif reason == "direct_change":
                        reason = "direct_and_dependency_change"

        if trigger_files:
            affected[service] = {
                "reason": reason,
                "trigger_files": list(set(trigger_files)),
            }

    return affected


def main():
    base_ref = sys.argv[1] if len(sys.argv) > 1 else "origin/main"

    changed_files = get_changed_files(base_ref)
    affected = get_affected_services(changed_files)

    result = {
        "base_ref": base_ref,
        "changed_files_count": len(changed_files),
        "changed_files": changed_files,
        "affected_services": list(affected.keys()),
        "affected_count": len(affected),
        "details": affected,
        "all_services": list(SERVICES.keys()),
        "skipped_services": [s for s in SERVICES if s not in affected],
    }

    # Output as JSON (consumable by GitHub Actions)
    print(json.dumps(result, indent=2))

    # Also output GitHub Actions compatible outputs
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"affected={json.dumps(list(affected.keys()))}\n")
            f.write(f"affected_count={len(affected)}\n")
            for service in SERVICES:
                f.write(f"{service}={'true' if service in affected else 'false'}\n")


if __name__ == "__main__":
    main()
