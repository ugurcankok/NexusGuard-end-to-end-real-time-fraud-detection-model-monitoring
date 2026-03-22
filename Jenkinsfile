pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = "nexusguard"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'The code is being pulled from the GitHub repository...'
                checkout scm
            }
        }

        stage('Clean & Build') {
            steps {
                echo 'The old system is being cleaned up and images are being built...'
                sh 'docker compose down -v --remove-orphans'
                sh 'docker compose build'
            }
        }

        stage('Deploy') {
            steps {
                echo 'The system is being brought back online...'
                sh 'docker compose up -d'
            }
        }

        stage('Health Check') {
            steps {
                echo 'The services are expected to be ready...'
                sh 'sleep 20'
                sh 'curl -f http://nexus_serving:8000/metrics || exit 1'
            }
        }
    }
}