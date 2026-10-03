pipeline {
    agent any

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }

    environment {
        DOCKER_IMAGE    = 'mariamas32/aiops-backend'
        DOCKER_CREDS_ID = 'docker-registry-creds'
        K8S_NAMESPACE   = 'dev'
        K8S_DIR         = 'K8s_YAML'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/zeyadmvtr/AI-logs-metrics-monitor-system.git'
            }
        }

        stage('Run Unit Tests') {
            steps {
                // --volumes-from: the docker daemon runs on the host, so a plain
                // "-v $(pwd):/app" would mount a host path that does not exist.
                // Sharing the Jenkins container's volumes makes the workspace visible.
                // No "|| echo": a failing test must fail the build.
                sh '''
                    docker run --rm --volumes-from jenkins-server \
                        -w "$WORKSPACE/backend" python:3.11-slim \
                        sh -c "pip install --no-cache-dir -r requirements.txt && pytest tests/"
                '''
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                dir('backend') {
                    script {
                        docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_CREDS_ID}") {
                            def appImage = docker.build("${DOCKER_IMAGE}:${BUILD_NUMBER}")
                            appImage.push()
                            appImage.push('latest')
                        }
                    }
                    // keep the VM disk from filling up with old images
                    sh "docker rmi ${DOCKER_IMAGE}:${BUILD_NUMBER} || true"
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    kubectl create namespace ${K8S_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                    sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${BUILD_NUMBER}|g" ${K8S_DIR}/05-backend-deployment.yaml
                    kubectl apply -f ${K8S_DIR}/ -n ${K8S_NAMESPACE}
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    kubectl rollout status deployment/aiops-backend -n ${K8S_NAMESPACE} --timeout=180s
                '''
            }
        }
    }

    post {
        failure {
            // shows why a rollout failed (ImagePullBackOff, CrashLoopBackOff, ...)
            sh '''
                kubectl get pods -n ${K8S_NAMESPACE} || true
                kubectl describe pods -n ${K8S_NAMESPACE} | tail -60 || true
            '''
        }
        cleanup {
            cleanWs()
        }
    }
}