FROM jenkins/jenkins:lts-jdk17

# Skip initial setup wizard
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"

# Install plugins
COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# Copy Configuration as Code
COPY --chown=jenkins:jenkins casc/ /var/jenkins_home/casc_configs/
ENV CASC_JENKINS_CONFIG=/var/jenkins_home/casc_configs

USER root

# Install Docker CLI (for Docker-in-Docker builds)
RUN apt-get update && apt-get install -y \
    docker.io \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

USER jenkins
