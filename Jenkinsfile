pipeline {
    agent any  // Runs on any available Jenkins agent

    stages {
        // Stage 1: Fetch code from Git
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Shubham09055/Capstone_project1.git'
            }
        }

        // Stage 2: Build backend Docker image
        stage('Build Backend') {
            steps {
                dir('backend') {
                    bat 'docker build -t mern-backend .'
                }
            }
        }

        // Stage 3: Build frontend Docker image
        stage('Build Frontend') {
            steps {
                dir('frontend') {
                    bat 'docker build -t mern-frontend .'
                }
            }
        }

        // Stage 4: Deploy with Docker Compose
        stage('Deploy') {
            steps {
                bat 'docker-compose down || true'  // Stop old containers (ignore errors)
                bat 'docker-compose up -d'         // Start new containers
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline succeeded!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}