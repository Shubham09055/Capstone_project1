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

        // Stage 2: Build Docker images sequentially
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

        // Stage 3: Deploy with Docker Compose
        stage('Deploy') {
            steps {
                bat 'docker-compose down --remove-orphans || true'
                bat 'docker-compose up -d'
                
                // Wait for ML service to become healthy
                script {
                    timeout(time: 2, unit: 'MINUTES') {
                        waitUntil {
                            def status = bat(
                                script: 'docker inspect --format="{{.State.Health.Status}}" capstone-ml-service',
                                returnStdout: true
                            ).trim()
                            echo "ML Service status: ${status}"
                            return status == 'healthy'
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            // Clean up workspace
            cleanWs()
            
            // Archive logs if build failed
            script {
                if (currentBuild.result == 'FAILURE') {
                    bat '''
                        docker ps -a > containers.log
                        docker logs capstone-ml-service > ml-service.log 2>&1 || true
                    '''
                    archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
                }
            }
        }

        success {
            echo '✅ Pipeline succeeded!'
        }

        failure {
            echo '❌ Pipeline failed! Check the logs for details.'
        }
    }
}