// Jenkins Shared Library: notifySlack
// Usage: notifySlack(channel: '#deployments', status: 'SUCCESS')

def call(Map config = [:]) {
    def channel = config.channel ?: '#ci-cd'
    def status = config.status ?: currentBuild.currentResult
    def message = config.message ?: "${env.JOB_NAME} #${env.BUILD_NUMBER}: ${status}"

    echo "Slack notification: [${channel}] ${message}"
    // In real env: slackSend(channel: channel, message: message, color: statusColor(status))
}

def statusColor(String status) {
    switch(status) {
        case 'SUCCESS': return 'good'
        case 'FAILURE': return 'danger'
        case 'UNSTABLE': return 'warning'
        default: return '#439FE0'
    }
}
