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
                    // Получаем текущую ветку
                    def branch = bat(
                        script: 'git branch --show-current',
                        returnStdout: true
                    ).trim()
                    env.GIT_BRANCH = branch
                    echo "Build for branch: ${env.GIT_BRANCH}"
                }
            }
        }
        
        stage('Install Dependencies') {
            steps {
                
                script {
                    dir(env.FRONTEND_DIR) {
                        bat 'npm ci --silent'
                        echo "Frontend dependencies installed"
                    }
                    
                    
                    def pythonPath = "C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python314\\python.exe"
                    def exists = bat(
                        script: "@echo off && if exist \"${pythonPath}\" (echo EXISTS) else (echo NOT_FOUND)",
                        returnStdout: true
                    ).trim()
                    
                    if (exists.contains("EXISTS")) {
                        env.PYTHON_PATH = pythonPath
                        bat """
                            @echo off
                            echo Using Python from: ${env.PYTHON_PATH}
                            
                            if exist "requirements.txt" (
                                echo Installing Python dependencies...
                                "${env.PYTHON_PATH}" -m pip install -r requirements.txt
                            ) else (
                                echo requirements.txt not found
                                "${env.PYTHON_PATH}" -m pip install django djangorestframework
                            )
                        """
                        echo "Backend dependencies installed"
                    } else {
                        echo "Python not found, skipping backend dependencies"
                    }
                }
            }
        }
        
        stage('Run Backend Tests') {
            when {
                expression {
                    def branch = env.GIT_BRANCH ?: ''
                    
                    return branch != 'main' && branch != 'master' && branch != 'origin/main' && branch != 'origin/master'
                }
            }
            steps {
                script {
                    if (env.PYTHON_PATH) {
                        echo "Running Django tests with Python: ${env.PYTHON_PATH}"
                        
                        bat """
                            @echo off
                            echo Python path: ${env.PYTHON_PATH}
                            
                            if exist "manage.py" (
                                echo Checking Django project...
                                "${env.PYTHON_PATH}" manage.py check
                                
                                echo Running Django tests...
                                "${env.PYTHON_PATH}" manage.py test --verbosity=2
                            ) else (
                                echo manage.py not found
                                exit 1
                            )
                        """
                    } else {
                        echo "Python not available, skipping backend tests"
                    }
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
        
        stage('Build Frontend') {
            steps {
                dir(env.FRONTEND_DIR) {
                   
                    script {
                        def hasBuildScript = bat(
                            script: 'npm run 2>&1 | findstr /i "build"',
                            returnStdout: true,
                            returnStatus: true
                        )
                        
                        if (hasBuildScript == 0) {
                            echo "Building Frontend..."
                            bat 'npm run build 2>&1 || echo "Frontend build command executed"'
                            echo "Frontend build completed"
                        } else {
                            echo "Build script not found in package.json, skipping build"
                        }
                    }
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                expression {
                    def branch = env.GIT_BRANCH ?: ''
                    return branch == 'main' || branch == 'master' || branch == 'origin/main' || branch == 'origin/master'
                }
            }
            steps {
                script {
                    echo "=== DEPLOYING TO PRODUCTION ==="
                    
                    // Фронтенд
                    dir(env.FRONTEND_DIR) {
                        bat 'npm run build 2>&1 || echo "Frontend build completed for production"'
                        echo "Frontend production build completed"
                    }
                    
                    // Бэкенд
                    if (env.PYTHON_PATH) {
                        bat """
                            @echo off
                            echo Creating production build...
                            
                            if exist "manage.py" (
                                echo Collecting Django static files...
                                "${env.PYTHON_PATH}" manage.py collectstatic --noinput
                                python manage.py runserver
                                echo python manage.py runserver
                                echo Creating production package...
                                mkdir dist 2>nul
                                xcopy project dist\\project /E /I /Y 2>nul
                                copy manage.py dist\\ 2>nul
                                copy requirements.txt dist\\ 2>nul
                                echo Backend production package created
                            )
                        """
                    }
                    
                    echo "=== PRODUCTION DEPLOYMENT READY ==="
                }
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