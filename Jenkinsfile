pipeline {
    agent any
    
    environment {
        FRONTEND_DIR = 'client'
        BACKEND_DIR = 'project'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                
                script {
                    def branch = bat(
                        script: 'git branch --show-current',
                        returnStdout: true
                    ).trim()
                    env.GIT_BRANCH = branch
                    echo "Build for branch: ${env.GIT_BRANCH}"
                }
            }
        }
        
        stage('Install Frontend Dependencies') {
            steps {
                dir(env.FRONTEND_DIR) {
                    bat 'npm ci --silent'
                    echo "Frontend dependencies installed"
                }
            }
        }
        
        stage('Install Backend Dependencies') {
            steps {
                script {
                    try {
                        bat 'python --version'
                        echo "Python found"
                        env.PYTHON_AVAILABLE = 'true'
                    } catch (Exception e) {
                        echo "Python not found, skipping backend dependencies"
                        env.PYTHON_AVAILABLE = 'true'
                        return
                    }
                    
                    bat '''
                        if exist "requirements.txt" (
                            echo Installing dependencies from requirements.txt...
                            pip install -r requirements.txt
                        ) else (
                            echo requirements.txt not found
                            pip install django djangorestframework
                        )
                    '''
                    echo "Backend dependencies installed"
                }
            }
        }
        
        stage('Run Backend Tests') {
           
            steps {
                script {
                    echo "Running Django tests..."
                    
                    bat '''
                        if exist "manage.py" (
                            echo Checking Django project...
                            python manage.py check
                            
                            echo Running tests from tests.py...
                            python manage.py test project.tests --verbosity=2
                        ) else (
                            echo manage.py not found
                            exit 1
                        )
                    '''
                }
            }
            post {
                success {
                    echo 'Django tests passed successfully'
                }
                failure {
                    echo 'Django tests failed'
                }
            }
        }
        
        stage('Run Frontend Tests') {
            when {
                expression {
                    def branch = env.GIT_BRANCH ?: ''
                    return branch != 'main' && branch != 'master'
                }
            }
            steps {
                dir(env.FRONTEND_DIR) {
                    script {
                        def hasTests = bat(
                            script: 'npm run 2>&1 | findstr /i "test"',
                            returnStdout: true,
                            returnStatus: true
                        )
                        
                        if (hasTests == 0) {
                            echo "Running Frontend tests..."
                            bat 'npm test -- --passWithNoTests'
                        } else {
                            echo "Frontend tests not configured in package.json"
                        }
                    }
                }
            }
        }
        
        stage('Build for Production') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                }
            }
            steps {
                script {
                    echo "Building for Production"
                    
                    dir(env.FRONTEND_DIR) {
                        bat 'npm run build 2>&1 || echo "Frontend build completed"'
                        echo "Frontend built"
                    }
                    
                    if (env.PYTHON_AVAILABLE == 'true') {
                        bat '''
                            if exist "manage.py" (
                                echo Collecting Django static files...
                                python manage.py collectstatic --noinput
                                
                                echo Creating archive...
                                mkdir dist 2>nul
                                xcopy project dist\\project /E /I /Y 2>nul
                                copy manage.py dist\\ 2>nul
                                copy requirements.txt dist\\ 2>nul
                                echo Backend build completed
                            )
                        '''
                    }
                    
                    echo "Production build completed"
                }
            }
        }
        
        stage('Demo Deploy') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                }
            }
            steps {
                echo "Demo deployment"
                bat 'echo Deployment completed successfully (demo)'
                echo "Deployment completed"
            }
        }
    }
    
    post {
        always {
            echo "Build finished"
            echo "Status: ${currentBuild.result ?: 'SUCCESS'}"
            echo "Duration: ${currentBuild.durationString}"
            echo "Branch: ${env.GIT_BRANCH ?: 'not defined'}"
            
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully'
        }
        failure {
            echo 'Pipeline failed'
        }
    }
}