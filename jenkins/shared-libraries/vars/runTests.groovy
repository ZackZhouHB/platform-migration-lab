// Jenkins Shared Library: runTests
// Usage in Jenkinsfile: runTests(lang: 'node', path: 'services/api-gateway')

def call(Map config = [:]) {
    def lang = config.lang ?: 'node'
    def path = config.path ?: '.'
    def reportDir = config.reportDir ?: 'test-results'

    echo "Running tests for ${path} (${lang})..."

    dir(path) {
        switch(lang) {
            case 'node':
                sh 'npm ci'
                sh 'npm test'
                break
            case 'python':
                sh 'python3 -m pytest tests/ -v || python3 tests/test_app.py'
                break
            case 'go':
                sh 'go test ./... -v'
                break
            default:
                error "Unsupported language: ${lang}"
        }
    }

    echo "Tests completed for ${path}"
}
