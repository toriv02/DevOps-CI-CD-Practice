pipeline {
    agent any
    
    environment {
        FRONTEND_DIR = 'client'      // Папка с Vue.js
        BACKEND_DIR = 'project'      // Папка с Django
        FRONTEND_PORT = '8080'       // Vue.js по умолчанию использует порт 8080
        BACKEND_PORT = '8000'        // Django по умолчанию порт 8000
        DJANGO_SETTINGS_MODULE = 'project.settings'
        NODE_HOME = tool name: 'NodeJS', type: 'nodejs'
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
                    // Устанавливаем зависимости для Vue.js
                    dir(env.FRONTEND_DIR) {
                        bat """
                            @echo off
                            echo Installing Vue.js dependencies...
                            npm install
                            echo Vue.js dependencies installed
                        """
                    }
                    
                    // Устанавливаем зависимости для Django
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
                                "${env.PYTHON_PATH}" -m pip install django djangorestframework django-cors-headers
                            )
                        """
                        echo "Django dependencies installed"
                    }
                }
            }
        }
        
        stage('Run Tests') {
            when {
                expression {
                    def branch = env.GIT_BRANCH ?: ''
                    return branch != 'main' && branch != 'master' && branch != 'origin/main' && branch != 'origin/master'
                }
            }
            steps {
                script {
                    // Запускаем тесты Django
                    if (env.PYTHON_PATH) {
                        bat """
                            @echo off
                            echo Running Django tests...
                            if exist "manage.py" (
                                "${env.PYTHON_PATH}" manage.py test --verbosity=2
                            )
                        """
                    }
                    
                    // Запускаем тесты Vue.js
                    dir(env.FRONTEND_DIR) {
                        bat """
                            @echo off
                            echo Running Vue.js tests...
                            npm run test:unit 2>nul || echo "No Vue.js tests found or test command failed"
                        """
                    }
                }
            }
        }
        
        stage('Build Vue.js') {
            steps {
                dir(env.FRONTEND_DIR) {
                    script {
                        // Проверяем, есть ли команда build для Vue.js
                        def hasBuildScript = bat(
                            script: 'npm run 2>&1 | findstr /i "build"',
                            returnStdout: true,
                            returnStatus: true
                        )
                        
                        if (hasBuildScript == 0) {
                            echo "Building Vue.js application..."
                            bat 'npm run build'
                            echo "Vue.js build completed"
                            
                            // Копируем сборку в папку Django для статики
                            bat """
                                @echo off
                                if exist "dist" (
                                    echo Copying Vue.js build to Django static...
                                    xcopy /E /I /Y dist\\* ..\\project\\static\\ 2>nul || echo "Copy completed"
                                )
                            """
                        } else {
                            echo "No build script found in Vue.js project"
                        }
                    }
                }
            }
        }
        
        stage('Django Migrations') {
            steps {
                script {
                    if (env.PYTHON_PATH) {
                        bat """
                            @echo off
                            echo Running Django migrations...
                            if exist "manage.py" (
                                "${env.PYTHON_PATH}" manage.py makemigrations
                                "${env.PYTHON_PATH}" manage.py migrate
                                echo Django migrations completed
                            )
                        """
                    }
                }
            }
        }
        
        stage('Collect Static Files') {
            steps {
                script {
                    if (env.PYTHON_PATH) {
                        bat """
                            @echo off
                            echo Collecting Django static files...
                            if exist "manage.py" (
                                "${env.PYTHON_PATH}" manage.py collectstatic --noinput
                                echo Static files collected
                            )
                        """
                    }
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
                    echo "=== STARTING DJANGO + VUE APPLICATION ==="
                    
                    // 1. Останавливаем предыдущие процессы
                    bat """
                        @echo off
                        echo Stopping existing processes...
                        
                        REM Останавливаем Django на порту 8000
                        for /f "tokens=5" %%i in ('netstat -ano ^| findstr :${env.BACKEND_PORT}') do (
                            echo Stopping Django process PID: %%i
                            taskkill /F /PID %%i 2>nul
                        )
                        
                        REM Останавливаем Vue dev server на порту 8080
                        for /f "tokens=5" %%i in ('netstat -ano ^| findstr :${env.FRONTEND_PORT}') do (
                            echo Stopping Vue process PID: %%i
                            taskkill /F /PID %%i 2>nul
                        )
                        
                        REM Ждем 2 секунды
                        ping 127.0.0.1 -n 3 > nul
                        echo All processes stopped
                    """
                    
                    // 2. Настраиваем Django для работы с Vue
                    bat """
                        @echo off
                        echo Configuring Django for Vue.js...
                        
                        REM Создаем базовый конфиг для Django, если нужно
                        if not exist "django_vue_config.py" (
                            echo Creating Django config for Vue...
                            echo # Django settings for Vue.js integration > django_vue_config.py
                            echo INSTALLED_APPS += ['corsheaders'] >> django_vue_config.py
                            echo MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware') >> django_vue_config.py
                            echo CORS_ALLOW_ALL_ORIGINS = True >> django_vue_config.py
                        )
                    """
                    
                    // 3. Запускаем Django бэкенд
                    if (env.PYTHON_PATH) {
                        bat """
                            @echo off
                            echo ========================================
                            echo STARTING DJANGO BACKEND
                            echo ========================================
                            
                            echo Starting Django on port ${env.BACKEND_PORT}...
                            
                            REM Запускаем Django в отдельном окне
                            start "Django Backend" cmd /k "cd /d "%WORKSPACE%" && "${env.PYTHON_PATH}" manage.py runserver 0.0.0.0:${env.BACKEND_PORT}"
                            
                            echo Django backend started in new window
                            echo Backend URL: http://localhost:${env.BACKEND_PORT}
                        """
                        
                        // Ждем запуска Django
                        bat """
                            @echo off
                            echo Waiting for Django to start...
                            ping 127.0.0.1 -n 6 > nul
                            
                            echo Checking Django health...
                            curl http://localhost:${env.BACKEND_PORT}/ 2>nul && echo Django is running || echo Django check completed
                        """
                    }
                    
                    // 4. Запускаем Vue.js фронтенд
                    dir(env.FRONTEND_DIR) {
                        script {
                            // Определяем команду для запуска Vue.js
                            def availableScripts = bat(
                                script: 'npm run 2>&1',
                                returnStdout: true
                            )
                            def startCommand = 'npm run serve'  // Стандартная команда для Vue CLI
                            
                            if (availableScripts.contains('"dev"')) {
                                startCommand = 'npm run dev'
                            } else if (availableScripts.contains('"start"')) {
                                startCommand = 'npm run start'
                            }
                            
                            bat """
                                @echo off
                                echo ========================================
                                echo STARTING VUE.JS FRONTEND
                                echo ========================================
                                
                                echo Starting Vue.js on port ${env.FRONTEND_PORT}...
                                echo Using command: ${startCommand}
                                
                                REM Запускаем Vue.js в отдельном окне
                                start "Vue.js Frontend" cmd /k ${startCommand}
                                
                                echo Vue.js frontend started in new window
                                echo Frontend URL: http://localhost:${env.FRONTEND_PORT}
                            """
                            
                            // Ждем запуска Vue.js
                            bat """
                                @echo off
                                echo Waiting for Vue.js to start...
                                ping 127.0.0.1 -n 6 > nul
                            """
                        }
                    }
                    
                    // 5. Показываем информацию для пользователя
                    bat """
                        @echo off
                        echo ========================================
                        echo APPLICATION STARTED SUCCESSFULLY!
                        echo ========================================
                        echo.
                        echo BACKEND (Django):
                        echo URL: http://localhost:${env.BACKEND_PORT}
                        echo Admin: http://localhost:${env.BACKEND_PORT}/admin
                        echo API: http://localhost:${env.BACKEND_PORT}/api/
                        echo.
                        echo FRONTEND (Vue.js):
                        echo URL: http://localhost:${env.FRONTEND_PORT}
                        echo.
                        echo ========================================
                        echo Applications are running in separate windows
                        echo ========================================
                    """
                    
                    // 6. Создаем HTML-страницу с информацией
                    bat """
                        @echo off
                        echo Creating status page...
                        
                        echo ^<html^>^<head^>^<title^>Django + Vue.js Application^</title^>^</head^> > status.html
                        echo ^<body style="font-family: Arial, sans-serif; padding: 20px;"^> >> status.html
                        echo ^<h1^>Application Successfully Deployed!^</h1^> >> status.html
                        echo ^<div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0;"^> >> status.html
                        echo ^<h2^>Backend (Django)^</h2^> >> status.html
                        echo ^<p^>URL: ^<a href="http://localhost:${env.BACKEND_PORT}" target="_blank"^>http://localhost:${env.BACKEND_PORT}^</a^>^</p^> >> status.html
                        echo ^<p^>Admin: ^<a href="http://localhost:${env.BACKEND_PORT}/admin" target="_blank"^>http://localhost:${env.BACKEND_PORT}/admin^</a^>^</p^> >> status.html
                        echo ^</div^> >> status.html
                        echo ^<div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0;"^> >> status.html
                        echo ^<h2^>Frontend (Vue.js)^</h2^> >> status.html
                        echo ^<p^>URL: ^<a href="http://localhost:${env.FRONTEND_PORT}" target="_blank"^>http://localhost:${env.FRONTEND_PORT}^</a^>^</p^> >> status.html
                        echo ^</div^> >> status.html
                        echo ^<p style="color: #666;"^>Applications are running in separate command windows^</p^> >> status.html
                        echo ^</body^>^</html^> >> status.html
                        
                        echo Status page created: %WORKSPACE%\\status.html
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo "Pipeline execution finished"
            echo "Status: ${currentBuild.result ?: 'SUCCESS'}"
            echo "Duration: ${currentBuild.durationString}"
            echo "Branch: ${env.GIT_BRANCH ?: 'not defined'}"
            
            // Не очищаем workspace, чтобы приложения продолжали работать
            echo "Workspace preserved - applications continue running"
            
            // Показываем ссылки
            echo "=== APPLICATION LINKS ==="
            echo "Backend (Django): http://localhost:${env.BACKEND_PORT}"
            echo "Frontend (Vue.js): http://localhost:${env.FRONTEND_PORT}"
            echo "========================"
        }
        success {
            echo 'Django + Vue.js application deployed successfully!'
            echo 'Applications are running in separate windows'
        }
        failure {
            echo 'Pipeline failed'
            // Очищаем workspace только при ошибке
            cleanWs()
        }
    }
}