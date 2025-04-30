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
                retry(3) {
                    git branch: 'main', 
                    url: 'https://github.com/Shubham09055/Capstone_project1.git'
                }
            }
        }

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
                            def size = bat(script: "@echo off\nfor %%F in (${file}) do @echo %%~zF", returnStdout: true).trim()
                            if (size == "0") {
                                error("🚨 Empty file detected: ${description} (${file})")
                            }
                            echo "✅ Found valid ${description} (${size} bytes)"
                        }
                    }
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    def buildStages = [
                        'backend': 'capstone-backend',
                        'frontend': 'capstone-frontend',
                        'ml-model': 'capstone-ml-model'
                    ]

                    buildStages.each { dirName, imageName ->
                        dir(dirName) {
                            bat """
                                docker build ^
                                --build-arg BUILDKIT_INLINE_CACHE=1 ^
                                --cache-from ${imageName} ^
                                -t ${imageName} .
                            """
                        }
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    try {
                        // Clean up previous deployment
                        bat 'docker-compose down --remove-orphans --volumes || echo "No previous containers to remove"'
                        
                        // Start services in order
                        bat 'docker-compose up -d mongo'
                        
                        // Wait for MongoDB
                        timeout(time: 3, unit: 'MINUTES') {
                            waitUntil {
                                def status = bat(
                                    script: 'docker inspect --format="{{.State.Health.Status}}" capstone-mongo 2> nul || echo "starting"',
                                    returnStdout: true
                                ).trim()
                                echo "MongoDB status: ${status}"
                                return status == 'healthy'
                            }
                        }
                        
                        // Start remaining services
                        bat 'docker-compose up -d'
                        
                    } catch (Exception e) {
                        // Collect diagnostics
                        bat '''
                            docker ps -a > containers.log 2>&1
                            docker inspect capstone-mongo > mongo-inspect.log 2>&1
                            docker logs capstone-mongo > mongo.log 2>&1 || echo "No MongoDB logs" > mongo.log
                            docker inspect capstone-ml-model > ml-model-inspect.log 2>&1
                            docker logs capstone-ml-model > ml-model.log 2>&1 || echo "No ML model logs" > ml-model.log
                            docker-compose logs --no-color > compose.log 2>&1
                        '''
                        error("Deployment failed: ${e.message}")
                    }
                }
            }
        }
    }

    post {
        always {
            // Archive logs
            archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
            
            // Clean workspace
            cleanWs()
        }

        success {
            echo '✅ Pipeline succeeded! All services are up and running.'
        }

        failure {
            echo '❌ Pipeline failed! Check the archived logs for details.'
            echo 'Common issues:'
            echo '- MongoDB initialization failure (check mongo.log)'
            echo '- ML model dependencies not installed (check ml-model.log)'
            echo '- Health check timeouts (adjust wait times in pipeline)'
        }
    }
}