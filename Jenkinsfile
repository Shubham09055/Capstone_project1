pipeline {
    agent any

    environment {
        COMPOSE_FILE = 'docker-compose.yml'
        COMPOSE_PROJECT_NAME = 'capstone'
        DOCKER_BUILDKIT = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', 
                url: 'https://github.com/Shubham09055/Capstone_project1.git'
            }
        }

        stage('Build') {
            steps {
                dir('backend') {
                    bat 'docker build -t capstone-backend .'
                }
                dir('frontend') {
                    bat 'docker build -t capstone-frontend .'
                }
                dir('ml-model') {
                    bat 'docker build -t capstone-ml-model .'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    try {
                        // Clean up previous deployment
                        bat 'docker-compose down --remove-orphans || echo "No containers to remove"'
                        
                        // Start services with proper initialization order
                        bat 'docker-compose up -d mongo'
                        
                        // Wait for MongoDB to become healthy with extended timeout
                        timeout(time: 2, unit: 'MINUTES') {
                            waitUntil {
                                def status = bat(
                                    script: 'docker inspect --format="{{.State.Health.Status}}" capstone-mongo 2> nul || echo "starting"',
                                    returnStdout: true
                                ).trim()
                                echo "MongoDB status: ${status}"
                                return status == 'healthy'
                            }
                        }
                        
                        
                        
                        // Additional health checks for other services
                        timeout(time: 2, unit: 'MINUTES') {
                            waitUntil {
                                def mlStatus = bat(
                                    script: 'docker inspect --format="{{.State.Health.Status}}" capstone-ml-model 2> nul || echo "starting"',
                                    returnStdout: true
                                ).trim()
                                echo "ML Model status: ${mlStatus}"
                                return mlStatus == 'healthy'
                            }
                        }
                        
                    } catch (Exception e) {
                        // Enhanced diagnostics
                        bat '''
                            echo "=== Docker Containers ===" > diagnostics.log
                            docker ps -a >> diagnostics.log 2>&1
                            echo. >> diagnostics.log
                            
                            echo "=== MongoDB Logs ===" >> diagnostics.log
                            docker logs capstone-mongo >> diagnostics.log 2>&1 || echo "No MongoDB logs" >> diagnostics.log
                            echo. >> diagnostics.log
                            
                            echo "=== ML Model Logs ===" >> diagnostics.log
                            docker logs capstone-ml-model >> diagnostics.log 2>&1 || echo "No ML Model logs" >> diagnostics.log
                            echo. >> diagnostics.log
                            
                            echo "=== Docker Compose Logs ===" >> diagnostics.log
                            docker-compose logs --no-color >> diagnostics.log 2>&1
                        '''
                        error("Deployment failed: ${e.message}")
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'diagnostics.log', allowEmptyArchive: true
            cleanWs()
        }

        failure {
            echo '❌ Pipeline failed! Check the diagnostics.log for details.'
            echo 'Common issues:'
            echo '- MongoDB not initializing properly'
            echo '- ML model service failing to start'
            echo '- Network connectivity issues between containers'
            echo '- Resource constraints (check Docker memory/CPU allocation)'
            
            // Additional debugging commands
            bat '''
                echo "=== Docker Network Inspection ===" >> network.log
                docker network inspect capstone_default >> network.log 2>&1
                echo. >> network.log
                
                echo "=== Docker Volume Inspection ===" >> network.log
                docker volume inspect capstone_mongodb_data >> network.log 2>&1
            '''
            archiveArtifacts artifacts: 'network.log', allowEmptyArchive: true
        }
    }
}