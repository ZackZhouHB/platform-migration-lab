// User Service - Jenkins Pipeline (Go)
// Demonstrates Go build patterns in Jenkins

@Library('shared-pipeline-lib') _

pipeline {
    agent { docker { image 'golang:1.22' } }

    environment {
        SERVICE_NAME = 'user-service'
        SERVICE_PATH = 'services/user-service'
        GOPATH = "${WORKSPACE}/go"
        CGO_ENABLED = '0'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Lint') {
            steps {
                dir("${SERVICE_PATH}") {
                    sh 'go vet ./...'
                }
            }
        }

        stage('Test') {
            steps {
                runTests(lang: 'go', path: "${SERVICE_PATH}")
            }
        }

        stage('Build Binary') {
            steps {
                dir("${SERVICE_PATH}") {
                    sh 'go build -o bin/user-service ./src/'
                }
            }
        }

        stage('Build Docker Image') {
            when { branch 'main' }
            steps {
                buildDocker(service: "${SERVICE_NAME}")
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
