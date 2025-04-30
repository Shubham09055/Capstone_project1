pipeline {
    agent any

    environment {
        COMPOSE_FILE = 'docker-compose.yml'
        COMPOSE_PROJECT_NAME = 'capstone'
        DOCKER_BUILDKIT = '1'  // Enable Docker BuildKit for faster builds
    }

    stages {
        // Stage 1: Checkout code with retries
        stage('Checkout') {
            steps {
                retry(3) {
                    git branch: 'main', 
                    url: 'https://github.com/Shubham09055/Capstone_project1.git',
                    credentialsId: 'github-credentials'  // Add your credentials ID
                }
            }
        }

        // Stage 2: Verify Files with detailed validation
        stage('Verify Files') {
            steps {
                script {
                    def requiredFiles = [
                        'backend/Dockerfile': 'Backend Dockerfile',
                        'frontend/Dockerfile': 'Frontend Dockerfile',
                        'ml-model/Dockerfile': 'ML-model Dockerfile',
                        'docker-compose.yml': 'Docker Compose file',
                        'ml-model/requirements.txt': 'ML model requirements'
                    ]
                    
                    requiredFiles.each { file, description ->
                        if (!fileExists(file)) {
                            error("🚨 Missing required file: ${description} (${file})")
                        } else {
                            def size = new File(file).size()
                            if (size == 0) {
                                error("🚨 Empty file detected: ${description} (${file})")
                            }
                            echo "✅ Found valid ${description} (${size} bytes)"
                        }
                    }
                }
            }
        }

        // Stage 3: Build Docker images with cache optimization
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
                            try {
                                bat """
                                    docker build \
                                    --build-arg BUILDKIT_INLINE_CACHE=1 \
                                    --cache-from ${imageName} \
                                    -t ${imageName} .
                                """
                            } catch (Exception e) {
                                error("Failed to build ${imageName}: ${e.message}")
                            }
                        }
                    }
                }
            }
        }

        // Stage 4: Deploy with comprehensive health checks
        stage('Deploy') {
            steps {
                script {
                    try {
                        // Clean up previous deployment
                        bat 'docker-compose down --remove-orphans --volumes || echo "No previous containers to remove"'
                        
                        // Start services with proper initialization order
                        bat 'docker-compose up -d mongo'
                        
                        // Wait for MongoDB to become healthy
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
                        
                        // Start ML model after MongoDB is ready
                        bat 'docker-compose up -d ml-model'
                        
                        // Wait for ML model to become healthy
                        timeout(time: 5, unit: 'MINUTES') {  // ML models may need more time
                            waitUntil {
                                def status = bat(
                                    script: 'docker inspect --format="{{.State.Health.Status}}" capstone-ml-model 2> nul || echo "starting"',
                                    returnStdout: true
                                ).trim()
                                echo "ML model status: ${status}"
                                return status == 'healthy'
                            }
                        }
                        
                        // Start remaining services
                        bat 'docker-compose up -d backend frontend'
                        
                        // Final health check
                        timeout(time: 2, unit: 'MINUTES') {
                            waitUntil {
                                def backendStatus = bat(
                                    script: 'docker inspect --format="{{.State.Health.Status}}" capstone-backend 2> nul || echo "starting"',
                                    returnStdout: true
                                ).trim()
                                def frontendStatus = bat(
                                    script: 'docker inspect --format="{{.State.Health.Status}}" capstone-frontend 2> nul || echo "starting"',
                                    returnStdout: true
                                ).trim()
                                echo "Backend status: ${backendStatus}, Frontend status: ${frontendStatus}"
                                return (backendStatus == 'healthy' && frontendStatus == 'healthy')
                            }
                        }
                        
                    } catch (Exception e) {
                        // Collect diagnostics before failing
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

        // Optional: Test stage
        stage('Smoke Test') {
            when {
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                script {
                    try {
                        bat 'curl -I http://localhost:3000'
                        bat 'curl -I http://localhost:3001/health'
                        bat 'curl -I http://localhost:5000/health'
                    } catch (e) {
                        error("Smoke tests failed: ${e.message}")
                    }
                }
            }
        }
    }

    post {
        always {
            // Archive all diagnostic files
            archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
            
            // Clean up workspace but preserve logs
            cleanWs(cleanWhenAborted: true, cleanWhenFailure: true, cleanWhenNotBuilt: true, cleanWhenUnstable: true, deleteDirs: true)
            
            // Generate deployment report
            script {
                def report = """
                Deployment Report
                ================
                Build: ${currentBuild.fullDisplayName}
                Result: ${currentBuild.currentResult}
                Duration: ${currentBuild.durationString}
                
                Services Status:
                - MongoDB: ${sh(script: 'docker inspect --format="{{.State.Health.Status}}" capstone-mongo 2> nul || echo "not running"', returnStdout: true).trim()}
                - ML Model: ${sh(script: 'docker inspect --format="{{.State.Health.Status}}" capstone-ml-model 2> nul || echo "not running"', returnStdout: true).trim()}
                - Backend: ${sh(script: 'docker inspect --format="{{.State.Health.Status}}" capstone-backend 2> nul || echo "not running"', returnStdout: true).trim()}
                - Frontend: ${sh(script: 'docker inspect --format="{{.State.Health.Status}}" capstone-frontend 2> nul || echo "not running"', returnStdout: true).trim()}
                """
                writeFile file: 'deployment-report.txt', text: report
                archiveArtifacts artifacts: 'deployment-report.txt'
            }
        }

        success {
            slackSend(color: 'good', message: "✅ Pipeline SUCCESS - ${env.JOB_NAME} #${env.BUILD_NUMBER}")
            echo '🎉 Pipeline succeeded! All services are up and running.'
        }

        failure {
            slackSend(color: 'danger', message: "❌ Pipeline FAILED - ${env.JOB_NAME} #${env.BUILD_NUMBER}")
            echo '❌ Pipeline failed! Check the archived logs for details.'
            echo 'Common issues:'
            echo '- MongoDB initialization failure (check mongo.log)'
            echo '- ML model dependencies not installed (check ml-model.log)'
            echo '- Health check timeouts (adjust wait times in pipeline)'
            echo '- Resource constraints (check Docker memory/CPU allocation)'
        }
    }
}