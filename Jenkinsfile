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
                script {
                    // Build all services in sequence (parallel not recommended on Windows)
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
        }

        stage("Stop Existing Containers") {
            steps {
                script {
                    // Check if containers are running
                    def running = bat(script: 'docker-compose ps -q', returnStdout: true).trim()
                    if (running) {
                        echo "Stopping running containers..."
                        bat 'docker-compose down --remove-orphans'
                    } else {
                        echo "No containers to stop"
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // Start services
                    bat 'docker-compose up -d'
                    
                    // Health checks for Windows
                    def services = [
                        [name: 'backend', container: 'capstone-backend', timeout: 2],
                        [name: 'frontend', container: 'capstone-frontend', timeout: 1],
                        [name: 'ml-model', container: 'capstone-ml-model', timeout: 2]
                    ]
                    
                    services.each { service ->
                        timeout(time: service.timeout, unit: 'MINUTES') {
                            waitUntil {
                                try {
                                    def status = bat(
                                        script: "@docker inspect --format=\"{{.State.Health.Status}}\" ${service.container} 2> nul || echo starting",
                                        returnStdout: true
                                    ).trim()
                                    echo "${service.name} status: ${status}"
                                    return status == 'healthy'
                                } catch (Exception e) {
                                    echo "Error checking ${service.name} status: ${e.getMessage()}"
                                    return false
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            // Collect logs from all containers
            script {
                bat '''
                    echo === Docker Compose Logs === > all_logs.log
                    docker-compose logs --no-color >> all_logs.log 2>&1
                    echo. >> all_logs.log
                    
                    echo === Docker Container List === >> all_logs.log
                    docker ps -a >> all_logs.log 2>&1
                '''
                archiveArtifacts artifacts: 'all_logs.log', allowEmptyArchive: true
                cleanWs()
            }
        }

        failure {
            echo '❌ Pipeline failed! Check the logs for details.'
            
            // Enhanced debugging information for Windows
            script {
                bat '''
                    echo === Failed Container Logs === > diagnostics.log
                    for /f "tokens=*" %%i in ('docker-compose ps --services') do (
                        docker inspect --format="{{.State.Status}}" capstone_%%i_1 | find /i "running" > nul
                        if errorlevel 1 (
                            echo === Logs for %%i === >> diagnostics.log
                            docker-compose logs --no-color %%i >> diagnostics.log 2>&1
                            echo. >> diagnostics.log
                        )
                    )
                    
                    echo === Network Inspection === >> diagnostics.log
                    docker network inspect %COMPOSE_PROJECT_NAME%_default >> diagnostics.log 2>&1
                    
                    echo === Volume Inspection === >> diagnostics.log
                    docker volume ls -f name=%COMPOSE_PROJECT_NAME% >> diagnostics.log 2>&1
                '''
                archiveArtifacts artifacts: 'diagnostics.log', allowEmptyArchive: true
            }
        }
        
        success {
            echo '✅ Pipeline succeeded! All services are up and healthy.'
        }
    }
}