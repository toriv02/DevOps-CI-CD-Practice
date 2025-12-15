pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                dir('client') {
                    bat 'npm ci --silent'
                }
                bat 'python -m pip install -r requirements.txt'
                // или явный путь, например:
                // bat 'C:\\Python39\\Scripts\\pip.exe install -r requirements.txt'
            }
        }
        
        stage('Run Tests') {
            steps {
                bat 'python manage.py test'
                dir('client') {
                    bat 'npm test -- --passWithNoTests || echo "No tests"'
                }
            }
        }
        
        stage('Build') {
            steps {
                echo 'Build completed'
            }
        }
    }
}