# Jenkins Fundamentals

## What Is Jenkins?

Jenkins is an open-source automation server used primarily for CI/CD. It's the most widely deployed CI/CD tool in enterprises, which is why migrating away from it is a common (and lucrative) skill.

## Core Concepts

### 1. Jenkins Controller (Master)
- The central server that manages jobs, configuration, and the UI
- Runs at `http://localhost:8080`
- Should NOT run builds directly (security + performance risk)
- Stores all job configurations, build history, credentials

### 2. Jenkins Agents (Nodes)
- Worker machines where builds actually execute
- Connect to controller via SSH, JNLP, or Docker
- Labelled for targeting (e.g., `linux`, `docker`, `gpu`)
- Can be permanent (always on) or ephemeral (spun up per build)

```
┌─────────────────────┐
│  Jenkins Controller  │  ← Manages jobs, UI, config
│   (port 8080)       │
└─────────┬───────────┘
          │ dispatches builds
    ┌─────┴──────┐
    │            │
┌───▼───┐  ┌───▼───┐
│Agent 1│  │Agent 2│  ← Where builds actually run
│(linux)│  │(docker)│
└───────┘  └───────┘
```

### 3. Jobs
- A "job" is a unit of work (build, test, deploy)
- Types:
  - **Freestyle**: configured via UI, limited flexibility
  - **Pipeline**: defined in code (Jenkinsfile), the modern approach
  - **Multibranch Pipeline**: auto-discovers branches and creates pipeline per branch

### 4. Jenkinsfile (Pipeline as Code)
Two flavours:

**Declarative** (structured, preferred for most cases):
```groovy
pipeline {
    agent { docker { image 'node:20' } }
    
    environment {
        APP_ENV = 'test'
    }
    
    stages {
        stage('Install') {
            steps {
                sh 'npm ci'
            }
        }
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }
        stage('Deploy') {
            when { branch 'main' }
            steps {
                sh 'echo deploying...'
            }
        }
    }
    
    post {
        always { cleanWs() }
        failure { echo 'Build failed!' }
        success { echo 'Build passed!' }
    }
}
```

**Scripted** (full Groovy, more flexible, harder to read):
```groovy
node('linux') {
    stage('Checkout') {
        checkout scm
    }
    stage('Test') {
        try {
            sh 'npm test'
        } catch (e) {
            currentBuild.result = 'FAILURE'
            throw e
        }
    }
}
```

### 5. Shared Libraries
Reusable Groovy code shared across pipelines. This is how enterprises avoid duplicating pipeline logic.

Structure:
```
shared-libraries/
├── vars/                    # Global variables/functions (called from Jenkinsfile)
│   ├── buildDocker.groovy   # Usage: buildDocker(image: 'myapp')
│   └── runTests.groovy      # Usage: runTests(lang: 'node')
└── src/org/lab/             # Helper classes (optional)
    └── Utils.groovy
```

Usage in Jenkinsfile:
```groovy
@Library('my-shared-lib') _

pipeline {
    stages {
        stage('Build') {
            steps {
                buildDocker(image: 'payment-service', tag: env.BUILD_NUMBER)
            }
        }
    }
}
```

**Why this matters for migration**: Shared libraries are the hardest part to migrate. They contain business logic, custom integrations, and organisational conventions. In GitHub Actions, these become reusable workflows or composite actions.

### 6. Plugins
Jenkins relies heavily on plugins (~1800 available). Common ones:
- **Git**: SCM integration
- **Pipeline**: Jenkinsfile support
- **Docker Pipeline**: `agent { docker {} }` support
- **Credentials Binding**: `withCredentials()` block
- **Blue Ocean**: modern UI
- **Workspace Cleanup**: `cleanWs()`
- **Slack/Email**: notifications

**Migration risk**: If a pipeline uses a niche plugin, there may be no direct GitHub Actions equivalent. You need to identify these early.

### 7. Credentials
Jenkins stores secrets in its own credential store:
```groovy
withCredentials([
    usernamePassword(credentialsId: 'docker-hub', usernameVariable: 'USER', passwordVariable: 'PASS'),
    string(credentialsId: 'api-key', variable: 'API_KEY')
]) {
    sh 'docker login -u $USER -p $PASS'
}
```

Scopes:
- **Global**: available to all jobs
- **System**: available to Jenkins internals only
- **Folder-level**: scoped to a folder of jobs

### 8. Triggers
```groovy
pipeline {
    triggers {
        cron('H */4 * * *')          // every 4 hours
        pollSCM('H/5 * * * *')      // poll git every 5 min
        upstream(upstreamProjects: 'base-lib', threshold: hudson.model.Result.SUCCESS)
    }
}
```

### 9. Agents in Detail
```groovy
// Run in a Docker container
agent { docker { image 'python:3.12' } }

// Run on a specific labelled node
agent { label 'linux && docker' }

// Run anywhere
agent any

// Don't allocate an agent at pipeline level (allocate per stage)
agent none
```

## Jenkins Architecture in Enterprise

```
┌──────────────────────────────────────────────────────┐
│                    ENTERPRISE JENKINS                  │
│                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │ Controller 1  │  │ Controller 2  │  │ Controller 3  ││
│  │ (Team A)     │  │ (Team B)     │  │ (Platform)   ││
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘│
│         │                  │                  │        │
│    ┌────┴────┐        ┌────┴────┐        ┌────┴────┐  │
│    │ Agents  │        │ Agents  │        │ Agents  │  │
│    │(EC2/K8s)│        │(EC2/K8s)│        │(Docker) │  │
│    └─────────┘        └─────────┘        └─────────┘  │
│                                                        │
│  Shared: Artifactory, SonarQube, Vault, Slack          │
│  Secrets: Jenkins Credential Store + Vault             │
│  Auth: LDAP/SSO integration                            │
└──────────────────────────────────────────────────────┘
```

## Key Differences: Jenkins vs GitHub Actions (Quick Reference)

| Jenkins | GitHub Actions |
|---------|---------------|
| Jenkinsfile | .github/workflows/*.yml |
| Shared Libraries | Reusable workflows + composite actions |
| Agents (persistent) | Runners (hosted or self-hosted) |
| Credentials plugin | GitHub Secrets + OIDC |
| Stages | Jobs + steps |
| Parallel stages | Matrix strategy + parallel jobs |
| Parameters | workflow_dispatch inputs |
| Artifacts plugin | actions/upload-artifact |
| Approval (input step) | Environment required reviewers |
| Cron trigger | schedule trigger |
| Webhook trigger | GitHub event trigger (push, PR, etc.) |
| Folders/views | Repository + org workflow structure |
| Plugins (~1800) | Marketplace actions (~20,000) |
| Groovy DSL | YAML + shell/scripts |
| Self-managed server | GitHub-managed (or self-hosted runners) |
