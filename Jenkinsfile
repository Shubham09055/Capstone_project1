pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = ''  // Set your registry URL
        PROJECT_NAME = 'capstone'
        COMPOSE_FILE = 'docker-compose.yml'
    }

    stages {
        // Stage 1: Checkout with retries
        stage('Checkout') {
            steps {
                retry(3) {
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: 'main']],
                        extensions: [[$class: 'CleanBeforeCheckout']],
                        userRemoteConfigs: [[
                            url: 'https://github.com/Shubham09055/Capstone_project1.git'
                            
                        ]]
                    ])
                }
            }
        }

        // Stage 2: Parallel Builds
        stage('Build Docker Images') {
            parallel {
                stage('Build Backend') {
                    steps {
                        dir('backend') {
                            script {
                                docker.build("${DOCKER_REGISTRY}/${PROJECT_NAME}-backend:latest").push()
                            }
                        }
                    }
                }

                stage('Build Frontend') {
                    steps {
                        dir('frontend') {
                            script {
                                docker.build("${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend:latest").push()
                            }
                        }
                    }
                }

                stage('Build ML Service') {
                    steps {
                        dir('ml-service') {
                            script {
                                docker.build("${DOCKER_REGISTRY}/${PROJECT_NAME}-ml-service:latest").push()
                            }
                        }
                    }
                }
            }
        }

        // Stage 3: Deploy with health checks
        stage('Deploy') {
            steps {
                script {
                    try {
                        // Stop and remove old containers
                        bat "docker-compose -f ${COMPOSE_FILE} down --remove-orphans || true"
                        
                        // Pull latest images
                        bat "docker-compose -f ${COMPOSE_FILE} pull"
                        
                        // Start services
                        bat "docker-compose -f ${COMPOSE_FILE} up -d"
                        
                        // Verify services are healthy
                        def services = ['backend', 'frontend', 'ml-service', 'mongo']
                        services.each { service ->
                            timeout(time: 2, unit: 'MINUTES') {
                                waitUntil {
                                    def status = bat(
                                        script: "docker inspect --format='{{.State.Health.Status}}' ${PROJECT_NAME}-${service}",
                                        returnStdout: true
                                    ).trim()
                                    echo "${service} status: ${status}"
                                    return status == 'healthy' || service == 'frontend'  // Frontend might not have health check
                                }
                            }
                        }
                    } catch (Exception e) {
                        error "Deployment failed: ${e.message}"
                    }
                }
            }
        }

        // Stage 4: Smoke Tests
        stage('Smoke Tests') {
            steps {
                script {
                    def testResults = bat(
                        script: "curl -s -o /dev/null -w \"%{http_code}\" http://localhost:3000/health",
                        returnStdout: true
                    ).trim()
                    
                    if (testResults != "200") {
                        error "Smoke test failed with status code ${testResults}"
                    }
                }
            }
        }
    }

    post {
        always {
            // Clean up workspace
            cleanWs()
            
            // Archive logs
            archiveArtifacts artifacts: '**/logs/*.log', allowEmptyArchive: true
        }
        
        success {
            slackSend(
                channel: '#devops',
                message: "✅ ${env.JOB_NAME} - Build #${env.BUILD_NUMBER} succeeded!",
                color: 'good'
            )
        }
        
        failure {
            slackSend(
                channel: '#devops',
                message: "❌ ${env.JOB_NAME} - Build #${env.BUILD_NUMBER} failed!",
                color: 'danger'
            )
            
            // Capture docker logs for debugging
            script {
                sh '''
                    docker ps -a > docker_containers.log
                    docker logs ${PROJECT_NAME}-ml-service > ml-service.log 2>&1 || true
                    docker logs ${PROJECT_NAME}-backend > backend.log 2>&1 || true
                '''
                archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
            }
        }
        
        unstable {
            slackSend(
                channel: '#devops',
                message: "⚠️ ${env.JOB_NAME} - Build #${env.BUILD_NUMBER} is unstable",
                color: 'warning'
            )
        }
    }
}