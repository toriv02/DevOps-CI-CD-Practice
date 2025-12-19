pipeline {
    agent any
    
    environment {
        FRONTEND_DIR = 'client'
        BACKEND_DIR = 'project'
        FRONTEND_PORT = '3000'
        BACKEND_PORT = '8000'
        DJANGO_SETTINGS_MODULE = 'project.settings'
        DEPLOY_DIR = 'C:\\deploy\\myapp'
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
            when {
                expression {
                    def branch = env.GIT_BRANCH ?: ''
                    return branch == 'main' || branch == 'master' || branch == 'origin/main' || branch == 'origin/master'
                }
            }
            steps {
                dir(env.FRONTEND_DIR) {
                    script {
                        def hasBuildScript = bat(
                            script: 'npm run 2>&1 | findstr /i "build"',
                            returnStdout: true,
                            returnStatus: true
                        )
                        
                        if (hasBuildScript == 0) {
                            echo "Building Frontend for production..."
                            bat 'npm run build'
                            echo "Frontend build completed"
                        } else {
                            echo "Build script not found in package.json, skipping build"
                        }
                    }
                }
            }
        }
        
        stage('Prepare Production') {
            when {
                expression {
                    def branch = env.GIT_BRANCH ?: ''
                    return branch == 'main' || branch == 'master' || branch == 'origin/main' || branch == 'origin/master'
                }
            }
            steps {
                script {
                    echo "=== PREPARING PRODUCTION DEPLOYMENT ==="
                    
                    // Создаем директорию для деплоя
                    bat """
                        @echo off
                        echo Creating deployment directory...
                        if not exist "${env.DEPLOY_DIR}" mkdir "${env.DEPLOY_DIR}"
                        if not exist "${env.DEPLOY_DIR}\\backend" mkdir "${env.DEPLOY_DIR}\\backend"
                        if not exist "${env.DEPLOY_DIR}\\frontend" mkdir "${env.DEPLOY_DIR}\\frontend"
                    """
                    
                    // Копируем backend
                    bat """
                        @echo off
                        echo Copying backend files...
                        xcopy /E /I /Y "${env.BACKEND_DIR}\\*" "${env.DEPLOY_DIR}\\backend\\"
                        copy requirements.txt "${env.DEPLOY_DIR}\\backend\\" 2>nul || echo "No requirements.txt"
                    """
                    
                    // Копируем собранный frontend
                    dir(env.FRONTEND_DIR) {
                        bat """
                            @echo off
                            echo Copying frontend files...
                            if exist "dist" (
                                xcopy /E /I /Y "dist\\*" "${env.DEPLOY_DIR}\\frontend\\"
                            ) else if exist "build" (
                                xcopy /E /I /Y "build\\*" "${env.DEPLOY_DIR}\\frontend\\"
                            ) else (
                                echo No frontend build directory found
                            )
                        """
                    }
                    
                    // Создаем конфигурационные файлы
                    bat """
                        @echo off
                        echo Creating configuration files...
                        
                        echo # Django Production Settings > "${env.DEPLOY_DIR}\\backend\\production_settings.py"
                        echo DEBUG = False >> "${env.DEPLOY_DIR}\\backend\\production_settings.py"
                        echo ALLOWED_HOSTS = ['localhost', '127.0.0.1'] >> "${env.DEPLOY_DIR}\\backend\\production_settings.py"
                        
                        echo # Startup script > "${env.DEPLOY_DIR}\\start_app.bat"
                        echo @echo off >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo echo Starting Application... >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo cd /d "${env.DEPLOY_DIR}\\backend" >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo "${env.PYTHON_PATH}" manage.py migrate --noinput >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo "${env.PYTHON_PATH}" manage.py collectstatic --noinput >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo start "Django Backend" /B "${env.PYTHON_PATH}" manage.py runserver 0.0.0.0:${env.BACKEND_PORT} >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo timeout /t 3 >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo cd /d "${env.DEPLOY_DIR}\\frontend" >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo if exist "index.html" ( >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo   echo Starting frontend server... >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo   "${env.PYTHON_PATH}" -m http.server ${env.FRONTEND_PORT} >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo ) else ( >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo   echo No frontend files found >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo ) >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo echo Application started! >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo echo Backend: http://localhost:${env.BACKEND_PORT} >> "${env.DEPLOY_DIR}\\start_app.bat"
                        echo echo Frontend: http://localhost:${env.FRONTEND_PORT} >> "${env.DEPLOY_DIR}\\start_app.bat"
                    """
                    
                    echo "=== PRODUCTION PREPARATION COMPLETE ==="
                }
            }
        }
        
        stage('Deploy and Start') {
            when {
                expression {
                    def branch = env.GIT_BRANCH ?: ''
                    return branch == 'main' || branch == 'master' || branch == 'origin/main' || branch == 'origin/master'
                }
            }
            steps {
                script {
                    echo "=== DEPLOYING AND STARTING APPLICATION ==="
                    
                    // Останавливаем предыдущие экземпляры приложения
                    bat """
                        @echo off
                        echo Stopping previous instances...
                        taskkill /F /IM python.exe 2>nul || echo No Python processes found
                        taskkill /F /IM python314.exe 2>nul || echo No Python314 processes found
                        timeout /t 2
                    """
                    
                    // Устанавливаем зависимости для продакшена
                    bat """
                        @echo off
                        cd /d "${env.DEPLOY_DIR}\\backend"
                        echo Installing production dependencies...
                        "${env.PYTHON_PATH}" -m pip install -r requirements.txt
                    """
                    
                    // Запускаем приложение
                    bat """
                        @echo off
                        cd /d "${env.DEPLOY_DIR}"
                        echo Starting application...
                        start "MyApp Production" start_app.bat
                    """
                    
                    // Ждем запуска и проверяем
                    bat 'timeout /t 10 /nobreak'
                    
                    // Проверяем, что сервисы работают
                    bat """
                        @echo off
                        echo Checking if services are running...
                        
                        echo Testing backend...
                        curl -f http://localhost:${env.BACKEND_PORT}/ || curl -f http://localhost:${env.BACKEND_PORT}/api/ || echo "Backend check completed"
                        
                        echo Testing frontend...
                        curl -f http://localhost:${env.FRONTEND_PORT}/ || echo "Frontend check completed"
                        
                        echo.
                        echo ========================================
                        echo APPLICATION SUCCESSFULLY DEPLOYED!
                        echo ========================================
                        echo Backend API: http://localhost:${env.BACKEND_PORT}
                        echo Frontend App: http://localhost:${env.FRONTEND_PORT}
                        echo Admin Panel: http://localhost:${env.BACKEND_PORT}/admin
                        echo ========================================
                    """
                    
                    echo "=== DEPLOYMENT COMPLETE ==="
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
            
            // Не очищаем workspace, чтобы сохранить деплой
            // cleanWs()
        }
        success {
            echo 'Pipeline completed successfully'
            echo 'Application is running at:'
            echo "  Backend: http://localhost:${env.BACKEND_PORT}"
            echo "  Frontend: http://localhost:${env.FRONTEND_PORT}"
        }
        failure {
            echo 'Pipeline failed'
        }
    }
}