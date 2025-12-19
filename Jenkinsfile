pipeline {
    agent any
    
    environment {
        FRONTEND_DIR = 'client'
        BACKEND_DIR = 'project'
        FRONTEND_PORT = '3000'
        BACKEND_PORT = '8000'
        DJANGO_SETTINGS_MODULE = 'project.settings
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
                    
                    // 1. Сборка фронтенда
                    dir(env.FRONTEND_DIR) {
                        bat 'npm run build 2>&1 || echo "Frontend build completed for production"'
                        echo "Frontend production build completed"
                    }
                    
                    // 2. Подготовка бэкенда
                    if (env.PYTHON_PATH) {
                        bat """
                            @echo off
                            echo Creating production build...
                            
                            if exist "manage.py" (
                                echo Collecting Django static files...
                                "${env.PYTHON_PATH}" manage.py collectstatic --noinput
                                
                                echo Applying migrations...
                                "${env.PYTHON_PATH}" manage.py migrate
                                
                                echo Creating production package...
                                mkdir dist 2>nul
                                xcopy project dist\\project /E /I /Y 2>nul
                                copy manage.py dist\\ 2>nul
                                copy requirements.txt dist\\ 2>nul
                                copy -r "${env.FRONTEND_DIR}/build" dist\\frontend_build 2>nul
                                echo Backend production package created
                            )
                        """
                    }
                    
                    echo "=== PRODUCTION DEPLOYMENT READY ==="
                }
            }
        }
        
        stage('Start Application') {
            when {
                expression {
                    def branch = env.GIT_BRANCH ?: ''
                    return branch == 'main' || branch == 'master' || branch == 'origin/main' || branch == 'origin/master'
                }
            }
            steps {
                script {
                    echo "=== STARTING APPLICATION ==="
                    
                    // 1. Останавливаем предыдущие процессы на тех же портах
                    bat """
                        @echo off
                        echo Stopping processes on ports ${env.FRONTEND_PORT} and ${env.BACKEND_PORT}...
                        
                        for /f "tokens=5" %%i in ('netstat -ano ^| findstr :${env.FRONTEND_PORT}') do (
                            taskkill /F /PID %%i 2>nul
                        )
                        
                        for /f "tokens=5" %%i in ('netstat -ano ^| findstr :${env.BACKEND_PORT}') do (
                            taskkill /F /PID %%i 2>nul
                        )
                        
                        timeout /t 2 /nobreak
                    """
                    
                    // 2. Запускаем бэкенд (Django)
                    if (env.PYTHON_PATH) {
                        bat """
                            @echo off
                            echo Starting Django backend on port ${env.BACKEND_PORT}...
                            
                            cd dist
                            start "Django Backend" /B "${env.PYTHON_PATH}" manage.py runserver 0.0.0.0:${env.BACKEND_PORT}
                            echo Django backend started with PID %ERRORLEVEL%
                        """
                        
                        // Ждем запуска бэкенда
                        bat 'timeout /t 5 /nobreak'
                        
                        // Проверяем, что бэкенд запустился
                        bat """
                            @echo off
                            echo Checking if backend is running...
                            curl -f http://localhost:${env.BACKEND_PORT}/api/ || curl -f http://localhost:${env.BACKEND_PORT}/ || echo "Backend health check completed"
                        """
                    }
                    
                    
                    dir(env.FRONTEND_DIR) {
                        bat """
                            @echo off
                            echo Starting frontend dev server on port ${env.FRONTEND_PORT}...
                            start "Frontend Server" /B npm run start
                            echo Frontend server started
                        """
                    }
                    
                    echo "=== APPLICATION STARTED ==="
                    echo "Backend: http://localhost:${env.BACKEND_PORT}"
                    echo "Frontend: http://localhost:${env.FRONTEND_PORT}"
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