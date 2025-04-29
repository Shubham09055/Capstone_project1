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

        // Stage 2: Verify Dockerfiles exist
        stage('Verify Files') {
            steps {
                script {
                    def requiredFiles = [
                        'backend/Dockerfile',
                        'frontend/Dockerfile',
                        'ml-service/Dockerfile',
                        'docker-compose.yml'
                    ]
                    
                    requiredFiles.each { file ->
                        if (!fileExists(file)) {
                            error("Missing required file: ${file}")
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
                bat 'docker-compose down --remove-orphans || exit 0'
                bat 'docker-compose up -d'
                
                // Wait for services to start
                script {
                    timeout(time: 2, unit: 'MINUTES') {
                        waitUntil {
                            try {
                                def mlStatus = bat(
                                    script: '@docker inspect --format="{{.State.Health.Status}}" capstone-ml-service || echo "starting"',
                                    returnStdout: true
                                ).trim()
                                echo "ML Service status: ${mlStatus}"
                                return mlStatus == 'healthy'
                            } catch (Exception e) {
                                echo "Waiting for services to start..."
                                return false
                            }
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
            
            // Collect logs on failure (Windows-compatible)
            script {
                if (currentBuild.result == 'FAILURE') {
                    bat '''
                        docker ps -a > containers.log
                        @docker logs capstone-ml-service 2>&1 > ml-service.log || echo "No logs available"
                    '''
                    archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
                }
            }
        }

        success {
            echo '✅ Pipeline succeeded!'
        }

        failure {
            echo '❌ Pipeline failed! Check the archived logs for details.'
        }
    }
}