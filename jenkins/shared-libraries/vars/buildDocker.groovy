// Jenkins Shared Library: buildDocker
// Usage in Jenkinsfile: buildDocker(service: 'api-gateway', tag: 'latest')

def call(Map config = [:]) {
    def service = config.service ?: error("service is required")
    def tag = config.tag ?: env.BUILD_NUMBER
    def registry = config.registry ?: 'localhost:5000'
    def dockerfile = config.dockerfile ?: "services/${service}/Dockerfile"
    def context = config.context ?: "services/${service}"

    echo "Building Docker image for ${service}..."
    
    sh """
        docker build \
            -t ${registry}/${service}:${tag} \
            -t ${registry}/${service}:latest \
            -f ${dockerfile} \
            ${context}
    """
    
    echo "Docker image built: ${registry}/${service}:${tag}"
    return "${registry}/${service}:${tag}"
}
