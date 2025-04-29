pipeline {
    agent any

    stages {
        // Stage 1: Checkout code
        stage('Checkout') {
            steps {
                git branch: 'main', 
                url: 'https://github.com/Shubham09055/Capstone_project1.git'
            }
        }

        // Stage 2: Verify Files (with better error message)
        stage('Verify Files') {
            steps {
                script {
                    def requiredFiles = [
                        'backend/Dockerfile': 'Backend Dockerfile',
                        'frontend/Dockerfile': 'Frontend Dockerfile',
                        'ml-model/Dockerfile': 'ML-model Dockerfile',
                        'docker-compose.yml': 'Docker Compose file'
                    ]
                    
                    requiredFiles.each { file, description ->
                        if (!fileExists(file)) {
                            error("🚨 Missing required file: ${description} (${file})")
                        } else {
                            echo "✅ Found ${description}"
                        }
                    }
                }
            }
        }

        // Stage 3: Build Docker images
        stage('Build') {
            steps {
                dir('backend') {
                    bat 'docker build -t capstone-backend .'
                }
                dir('frontend') {
                    bat 'docker build -t capstone-frontend .'
                }
                dir('ml-service') {
                    bat 'docker build -t capstone-ml-service .'
                }
            }
        }

        // Stage 4: Deploy
        stage('Deploy') {
            steps {
                script {
                    try {
                        // Stop and clean up any existing containers
                        bat 'docker-compose down --remove-orphans || echo "No containers to remove"'
                        
                        // Start new containers
                        bat 'docker-compose up -d'
                        
                        // Wait for ML service to become healthy
                        timeout(time: 2, unit: 'MINUTES') {
                            waitUntil {
                                def status = bat(
                                    script: 'docker inspect --format="{{.State.Health.Status}}" capstone-ml-service 2> nul || echo "starting"',
                                    returnStdout: true
                                ).trim()
                                echo "ML Service status: ${status}"
                                return status == 'healthy'
                            }
                        }
                    } catch (Exception e) {
                        error("Deployment failed: ${e.message}")
                    }
                }
            }
        }
    }

    post {
        always {
            // Clean up workspace
            cleanWs()
            
            // Collect logs on failure (Windows-compatible)
            script {
                if (currentBuild.result == 'FAILURE') {
                    bat '''
                        docker ps -a > containers.log 2>&1
                        docker logs capstone-ml-service > ml-service.log 2>&1 || echo "No logs available" > ml-service.log
                    '''
                    archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
                }
            }
        }

        success {
            echo '✅ Pipeline succeeded! All services are up and running.'
        }

        failure {
            echo '❌ Pipeline failed! Check the archived logs for details.'
            echo 'Possible issues:'
            echo '- Missing Dockerfile in ml-service directory'
            echo '- Docker build errors'
            echo '- Container health check failures'
        }
    }
}