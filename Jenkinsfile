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
                    // Manually build Docker images
                    dir('ml-model') {
                        bat 'docker build -t capstone-ml-model .'
                    }
                    dir('backend') {
                        bat 'docker build -t capstone-backend .'
                    }
                    dir('frontend') {
                        bat 'docker build -t capstone-frontend .'
                    }
                }
            }
        }

        stage("Stop & Remove Existing Containers") {
            steps {
                script {
                    echo "Cleaning up existing containers if present..."
                    def containers = ['capstone-ml-model', 'capstone-backend', 'capstone-frontend']
                    containers.each { container ->
                        bat "docker rm -f ${container} || echo Not running"
                    }

                    // Optionally remove unused networks or volumes
                    bat 'docker network prune -f'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    bat 'docker-compose up -d'

                    def services = [
                        [name: 'ml-model', container: 'capstone-ml-model', timeout: 2],
                        [name: 'backend', container: 'capstone-backend', timeout: 2],
                        [name: 'frontend', container: 'capstone-frontend', timeout: 1]
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
            echo '❌ Pipeline failed! Check logs.'
            script {
                bat '''
                    echo === Diagnostics === > diagnostics.log
                    for /f "tokens=*" %%i in ('docker-compose ps --services') do (
                        echo === Logs for %%i === >> diagnostics.log
                        docker-compose logs --no-color %%i >> diagnostics.log 2>&1
                        echo. >> diagnostics.log
                    )

                    echo === Network Info === >> diagnostics.log
                    docker network inspect %COMPOSE_PROJECT_NAME%_default >> diagnostics.log 2>&1

                    echo === Volume Info === >> diagnostics.log
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
