// Payment Service - Jenkins Pipeline (Scripted — more complex)
// Demonstrates scripted pipeline patterns: parallel, try/catch, conditional

@Library('shared-pipeline-lib') _

node {
    def SERVICE_NAME = 'payment-service'
    def SERVICE_PATH = 'services/payment-service'

    try {
        stage('Checkout') {
            checkout scm
        }

        stage('Quality Gates') {
            parallel(
                'Lint': {
                    echo "Linting ${SERVICE_NAME}..."
                    sh "cd ${SERVICE_PATH} && echo 'Lint passed'"
                },
                'Security Scan': {
                    echo "Running security scan on ${SERVICE_NAME}..."
                    sh "echo 'No vulnerabilities found'"
                }
            )
        }

        stage('Test') {
            runTests(lang: 'python', path: "${SERVICE_PATH}")
        }

        stage('Build Docker Image') {
            if (env.BRANCH_NAME == 'main') {
                buildDocker(service: "${SERVICE_NAME}")
            } else {
                echo "Skipping Docker build for branch: ${env.BRANCH_NAME}"
            }
        }

        stage('Deploy to Staging') {
            if (env.BRANCH_NAME == 'main') {
                deployToEnv(service: "${SERVICE_NAME}", env: 'staging')
            }
        }

        stage('Integration Tests') {
            if (env.BRANCH_NAME == 'main') {
                echo "Running integration tests against staging..."
                sh "echo 'Integration tests passed'"
            }
        }

        stage('Deploy to Production') {
            if (env.BRANCH_NAME == 'main') {
                deployToEnv(
                    service: "${SERVICE_NAME}",
                    env: 'production',
                    requireApproval: true
                )
            }
        }

        currentBuild.result = 'SUCCESS'

    } catch (e) {
        currentBuild.result = 'FAILURE'
        throw e

    } finally {
        notifySlack(status: currentBuild.result)
        cleanWs()
    }
}
