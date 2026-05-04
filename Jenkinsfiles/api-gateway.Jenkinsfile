// API Gateway - Jenkins Pipeline (Declarative)
// This is the "legacy" pipeline we will migrate to GitHub Actions

@Library('shared-pipeline-lib') _

pipeline {
    agent { docker { image 'node:20' } }

    environment {
        SERVICE_NAME = 'api-gateway'
        SERVICE_PATH = 'services/api-gateway'
    }

    options {
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                dir("${SERVICE_PATH}") {
                    sh 'npm ci'
                }
                dir('libs/common-utils') {
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

        stage('Build Docker Image') {
            when { branch 'main' }
            steps {
                buildDocker(service: "${SERVICE_NAME}")
            }
        }

        stage('Deploy to Dev') {
            when { branch 'main' }
            steps {
                deployToEnv(service: "${SERVICE_NAME}", env: 'dev')
            }
        }

        stage('Deploy to Production') {
            when { branch 'main' }
            steps {
                deployToEnv(service: "${SERVICE_NAME}", env: 'production')
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            notifySlack(status: 'SUCCESS')
        }
        failure {
            notifySlack(status: 'FAILURE', channel: '#alerts')
        }
    }
}
