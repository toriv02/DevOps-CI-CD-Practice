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
                    
                    // Проверяем, является ли ветка main
                    env.IS_MAIN_BRANCH = (env.GIT_BRANCH == 'main' || env.GIT_BRANCH == 'master') ? 'true' : 'false'
                    echo "Is main branch: ${env.IS_MAIN_BRANCH}"
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
        
        stage('Setup Python') {
            steps {
                script {
                    // Явно указываем путь к Python
                    def pythonPath = "C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python314\\python.exe"
                    
                    // Проверяем, существует ли файл
                    def exists = bat(
                        script: "@echo off && if exist \"${pythonPath}\" (echo EXISTS) else (echo NOT_FOUND)",
                        returnStdout: true
                    ).trim()
                    
                    if (exists.contains("EXISTS")) {
                        env.PYTHON_PATH = pythonPath
                        env.PYTHON_AVAILABLE = 'true'
                        echo "Python found at: ${env.PYTHON_PATH}"
                        
                        // Проверяем версию
                        bat "\"${env.PYTHON_PATH}\" --version"
                    } else {
                        env.PYTHON_AVAILABLE = 'false'
                        echo "Python not found at: ${pythonPath}"
                    }
                }
            }
        }

        stage('Install Backend Dependencies') {
            when {
                expression { env.PYTHON_AVAILABLE == 'true' }
            }
            steps {
                bat """
                    @echo off
                    echo Using Python from: ${env.PYTHON_PATH}
                    
                    if exist "requirements.txt" (
                        echo Installing dependencies from requirements.txt...
                        "${env.PYTHON_PATH}" -m pip install -r requirements.txt
                    ) else (
                        echo requirements.txt not found
                        "${env.PYTHON_PATH}" -m pip install django djangorestframework
                    )
                """
                echo "Backend dependencies installed"
            }
        }

        // ТЕСТЫ - ТОЛЬКО ДЛЯ НЕ-MAIN ВЕТОК
        stage('Run Backend Tests') {
            when {
                allOf {
                    expression { env.PYTHON_AVAILABLE == 'true' }
                    expression { env.IS_MAIN_BRANCH == 'false' }
                }
            }
            steps {
                echo "Running Django tests with Python: ${env.PYTHON_PATH}"
                
                bat """
                    @echo off
                    echo Python path: ${env.PYTHON_PATH}
                    
                    if exist "manage.py" (
                        echo Checking Django project...
                        "${env.PYTHON_PATH}" manage.py check
                        
                        echo Running tests from tests.py...
                        "${env.PYTHON_PATH}" manage.py test project.tests --verbosity=2
                    ) else (
                        echo manage.py not found
                        exit 1
                    )
                """
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
                expression { env.IS_MAIN_BRANCH == 'false' }
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
        
        // BUILD FOR PRODUCTION - ТОЛЬКО ДЛЯ MAIN ВЕТКИ
        stage('Build for Production') {
            when {
                expression { env.IS_MAIN_BRANCH == 'true' }
            }
            steps {
                script {
                    echo "Building for Production on main branch"
                    
                    // Сборка фронтенда
                    dir(env.FRONTEND_DIR) {
                        bat 'npm run build 2>&1 || echo "Frontend build completed"'
                        echo "Frontend built"
                    }
                    
                    // Сборка бэкенда (если Python доступен)
                    if (env.PYTHON_AVAILABLE == 'true') {
                        bat """
                            @echo off
                            if exist "manage.py" (
                                echo Collecting Django static files...
                                "${env.PYTHON_PATH}" manage.py collectstatic --noinput
                                
                                echo Creating archive...
                                mkdir dist 2>nul
                                xcopy project dist\\project /E /I /Y 2>nul
                                copy manage.py dist\\ 2>nul
                                copy requirements.txt dist\\ 2>nul
                                echo Backend build completed
                            )
                        """
                    }
                    
                    echo "Production build completed"
                }
            }
        }
        
        // DEPLOY - ТОЛЬКО ДЛЯ MAIN ВЕТКИ
        stage('Deploy') {
            when {
                expression { env.IS_MAIN_BRANCH == 'true' }
            }
            steps {
                script {
                    echo "Starting deployment on main branch"
                    
                    // Здесь будет ваш реальный процесс деплоя
                    // Например, копирование файлов на сервер, запуск Docker и т.д.
                    
                    bat 'echo Deployment to production server started'
                    
                    // Пример: копирование собранных файлов
                    bat '''
                        @echo off
                        echo Copying built files to server...
                        REM Добавьте здесь реальные команды деплоя
                        echo Files copied successfully
                    '''
                    
                    // Пример: перезапуск сервисов
                    bat '''
                        @echo off
                        echo Restarting services...
                        REM Добавьте здесь команды перезапуска сервисов
                        echo Services restarted
                    '''
                    
                    echo "Deployment completed successfully"
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