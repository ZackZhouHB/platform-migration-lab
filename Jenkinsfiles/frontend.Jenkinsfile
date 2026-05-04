// Frontend - Jenkins Pipeline
// Demonstrates Node.js build + artifact archiving

@Library('shared-pipeline-lib') _

pipeline {
    agent { docker { image 'node:20' } }

    environment {
        SERVICE_NAME = 'frontend'
        SERVICE_PATH = 'services/frontend'
    }

    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install') {
            steps {
                dir("${SERVICE_PATH}") {
                    sh 'npm ci || true'
                }
            }
        }

        stage('Lint') {
            steps {
                dir("${SERVICE_PATH}") {
                    sh 'npm run lint'
                }
            }
        }

        stage('Test') {
            steps {
                runTests(lang: 'node', path: "${SERVICE_PATH}")
            }
        }

        stage('Build') {
            steps {
                dir("${SERVICE_PATH}") {
                    sh 'npm run build'
                }
            }
        }

        stage('Archive Artifacts') {
            when { branch 'main' }
            steps {
                archiveArtifacts artifacts: "${SERVICE_PATH}/dist/**", fingerprint: true
            }
        }

        stage('Deploy') {
            when { branch 'main' }
            steps {
                deployToEnv(service: "${SERVICE_NAME}", env: 'dev')
            }
        }
    }

    post {
        always { cleanWs() }
        success { notifySlack(status: 'SUCCESS') }
        failure { notifySlack(status: 'FAILURE') }
    }
}
