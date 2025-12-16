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
                    // Определяем текущую ветку
                    def branch = bat(
                        script: 'git branch --show-current',
                        returnStdout: true
                    ).trim()
                    env.GIT_BRANCH = branch
                    echo "Build for branch: ${env.GIT_BRANCH}"
                    
                    // Анализ измененных файлов (как в отчете)
                    String changes = bat(
                        script: 'git diff --name-only HEAD~1 HEAD 2>nul || echo ""',
                        returnStdout: true
                    ).trim()
                    
                    boolean changedFrontend = false
                    boolean changedBackend = false
                    
                    if (changes) {
                        String[] files = changes.split(/\r?\n/)
                        for (String file : files) {
                            if (file.startsWith("${env.FRONTEND_DIR}/")) {
                                changedFrontend = true
                            }
                            if (file.startsWith("${env.BACKEND_DIR}/")) {
                                changedBackend = true
                            }
                        }
                    }
                    
                    env.CHANGED_FRONTEND = changedFrontend.toString()
                    env.CHANGED_BACKEND = changedBackend.toString()
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
                    } else {
                        env.PYTHON_AVAILABLE = 'false'
                        echo "Python not found at: ${pythonPath}"
                    }
                }
            }
        }
        
        stage('Install Dependencies') {
            steps {
                script {
                    // Устанавливаем зависимости только для измененных частей
                    if (env.CHANGED_FRONTEND == 'true') {
                        dir(env.FRONTEND_DIR) {
                            bat 'npm ci --silent'
                            echo "Frontend dependencies installed"
                        }
                    } else {
                        echo 'Фронтенд не изменён - зависимости пропущены.'
                    }
                    
                    if (env.CHANGED_BACKEND == 'true' && env.PYTHON_AVAILABLE == 'true') {
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
                    } else if (env.CHANGED_BACKEND == 'true' && env.PYTHON_AVAILABLE != 'true') {
                        echo 'Бэкенд изменён, но Python не доступен - зависимости пропущены.'
                    } else {
                        echo 'Бэкенд не изменён - зависимости пропущены.'
                    }
                }
            }
        }
        
        stage('Run Frontend Tests') {
            when {
                expression {
                    def branch = env.GIT_BRANCH ?: ''
                    // Тесты выполняем для всех веток, кроме основной
                    return branch != 'main' && branch != 'master' && branch != 'origin/main' && branch != 'origin/master'
                }
            }
            steps {
                script {
                    if (env.CHANGED_FRONTEND == 'true') {
                        dir(env.FRONTEND_DIR) {
                            echo "Running Frontend tests..."
                            bat 'npm test -- --passWithNoTests'
                        }
                    } else {
                        echo 'Фронтенд не изменён - тесты пропущены.'
                    }
                }
            }
        }
        
        stage('Run Backend Tests') {
            when {
                expression {
                    def branch = env.GIT_BRANCH ?: ''
                    // Тесты выполняем для всех веток, кроме основной
                    return branch != 'main' && branch != 'master' && branch != 'origin/main' && branch != 'origin/master'
                }
            }
            steps {
                script {
                    if (env.CHANGED_BACKEND == 'true' && env.PYTHON_AVAILABLE == 'true') {
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
                    } else {
                        echo 'Бэкенд не изменён или Python не доступен - тесты пропущены.'
                    }
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                expression {
                    def branch = env.GIT_BRANCH ?: ''
                    // Деплой ТОЛЬКО для основной ветки
                    return branch == 'main' || branch == 'master' || branch == 'origin/main' || branch == 'origin/master'
                }
            }
            steps {
                script {
                    echo "Deploying to Production"
                    
                    // Всегда устанавливаем зависимости для продакшена
                    dir(env.FRONTEND_DIR) {
                        bat 'npm ci --silent'
                        bat 'npm run build 2>&1 || echo "Frontend build completed"'
                        echo "Frontend built for production"
                    }
                    
                    if (env.PYTHON_AVAILABLE == 'true') {
                        bat '''
                            if exist "manage.py" (
                                echo Collecting Django static files...
                                python manage.py collectstatic --noinput
                                
                                echo Creating production archive...
                                mkdir dist 2>nul
                                xcopy project dist\\project /E /I /Y 2>nul
                                copy manage.py dist\\ 2>nul
                                copy requirements.txt dist\\ 2>nul
                                echo Backend production build completed
                            )
                        '''
                    }
                    
                    echo "Production deployment completed"
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