// Jenkins Shared Library: deployToEnv
// Usage in Jenkinsfile: deployToEnv(service: 'api-gateway', env: 'staging')

def call(Map config = [:]) {
    def service = config.service ?: error("service is required")
    def targetEnv = config.env ?: 'dev'
    def version = config.version ?: env.BUILD_NUMBER
    def requireApproval = config.requireApproval ?: (targetEnv == 'production')

    echo "Deploying ${service}:${version} to ${targetEnv}..."

    if (requireApproval) {
        input message: "Deploy ${service}:${version} to ${targetEnv}?",
              ok: 'Deploy',
              submitter: 'admin,platform-team'
    }

    // Simulate deployment
    sh """
        echo "Deploying ${service}:${version} to ${targetEnv}"
        echo "Target: ${targetEnv}.example.com"
        echo "Deployment successful"
    """

    echo "Successfully deployed ${service}:${version} to ${targetEnv}"
}
