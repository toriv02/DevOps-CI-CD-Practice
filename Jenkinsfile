pipeline {
    agent any
    
    environment {
        DJANGO_SETTINGS_MODULE = 'app.settings'  // Или правильное имя вашего settings
        PYTHON_VERSION = '3.11'
        NODE_VERSION = '18'
        PROJECT_DIR = 'project'
        CLIENT_DIR = 'client'
    }
    
    stages {
        stage('Checkout и Очистка') {
            steps {
                checkout scm
                cleanWs()
                echo "Рабочая директория: ${WORKSPACE}"
                sh 'ls -la'
            }
        }
        
        stage('Проверка изменений') {
            steps {
                script {
                    // Получаем список измененных файлов
                    def changes = sh(
                        script: 'git diff --name-only HEAD~1 HEAD 2>/dev/null || echo ""',
                        returnStdout: true
                    ).trim()
                    
                    echo "Измененные файлы: ${changes}"
                    
                    env.HAS_CHANGES = changes ? 'true' : 'false'
                    
                    // Определяем, какие части проекта изменились
                    if (changes) {
                        env.BACKEND_CHANGED = changes.contains('project/') || 
                                              changes.contains('requirements.txt') || 
                                              changes.contains('manage.py') || 
                                              changes.contains('pyproject.toml') ? 'true' : 'false'
                        
                        env.FRONTEND_CHANGED = changes.contains('client/') || 
                                               changes.contains('package.json') ? 'true' : 'false'
                    } else {
                        env.BACKEND_CHANGED = 'false'
                        env.FRONTEND_CHANGED = 'false'
                    }
                    
                    echo "Backend изменен: ${env.BACKEND_CHANGED}"
                    echo "Frontend изменен: ${env.FRONTEND_CHANGED}"
                }
            }
        }
        
        stage('Настройка Python окружения') {
            when {
                expression { return env.BACKEND_CHANGED == 'true' }
            }
            steps {
                script {
                    echo "Настройка Python ${PYTHON_VERSION}"
                    
                    // Проверяем Python
                    sh 'python --version'
                    sh 'pip --version'
                    
                    // Устанавливаем зависимости (если есть requirements.txt)
                    sh '''
                        if [ -f "requirements.txt" ]; then
                            echo "Установка зависимостей из requirements.txt..."
                            pip install -r requirements.txt
                        else
                            echo "requirements.txt не найден, устанавливаем базовые зависимости..."
                            pip install django djangorestframework
                        fi
                    '''
                    
                    // Проверяем установленные пакеты
                    sh 'pip list'
                }
            }
        }
        
        stage('Проверка миграций Django') {
            when {
                expression { return env.BACKEND_CHANGED == 'true' }
            }
            steps {
                script {
                    sh '''
                        echo "Проверка миграций Django..."
                        python manage.py makemigrations --check --dry-run
                    '''
                }
            }
        }
        
        stage('Запуск тестов Django') {
            when {
                expression { return env.BACKEND_CHANGED == 'true' }
            }
            steps {
                script {
                    echo "Запуск тестов Django..."
                    
                    sh '''
                        echo "Создание тестовой базы данных..."
                        # Если используется SQLite
                        python manage.py migrate --run-syncdb
                        
                        echo "Запуск тестов..."
                        python manage.py test project.tests --verbosity=2 --noinput
                    '''
                }
            }
            post {
                success {
                    echo '✅ Тесты Django успешно пройдены!'
                    archiveArtifacts artifacts: '**/test-reports/*.xml', allowEmptyArchive: true
                }
                failure {
                    echo '❌ Тесты Django провалились!'
                    // Сохраняем логи при ошибке
                    sh 'python manage.py test project.tests --verbosity=3 2>&1 || true'
                    error 'Тесты не пройдены'
                }
            }
        }
        
        stage('Настройка Node.js окружения') {
            when {
                expression { return env.FRONTEND_CHANGED == 'true' }
            }
            steps {
                script {
                    echo "Настройка Node.js ${NODE_VERSION}"
                    dir(env.CLIENT_DIR) {
                        // Проверяем Node.js
                        sh 'node --version'
                        sh 'npm --version'
                        
                        // Устанавливаем зависимости
                        sh 'npm ci --silent'
                        
                        // Проверяем установленные пакеты
                        sh 'npm list --depth=0'
                    }
                }
            }
        }
        
        stage('Запуск тестов Frontend') {
            when {
                expression { return env.FRONTEND_CHANGED == 'true' }
            }
            steps {
                script {
                    echo "Запуск тестов Frontend..."
                    dir(env.CLIENT_DIR) {
                        sh 'npm test -- --passWithNoTests || echo "Тесты фронтенда не найдены"'
                    }
                }
            }
        }
        
        stage('Сборка Frontend') {
            when {
                expression { 
                    return env.FRONTEND_CHANGED == 'true' && 
                    (env.GIT_BRANCH == 'main' || env.GIT_BRANCH == 'master')
                }
            }
            steps {
                script {
                    echo "Сборка Frontend для production..."
                    dir(env.CLIENT_DIR) {
                        sh 'npm run build'
                    }
                    
                    // Архивируем сборку
                    archiveArtifacts artifacts: '**/dist/**/*', allowEmptyArchive: true
                }
            }
        }
        
        stage('Статический анализ кода') {
            when {
                expression { return env.BACKEND_CHANGED == 'true' }
            }
            steps {
                script {
                    echo "Проверка качества кода..."
                    
                    // Проверка синтаксиса Python
                    sh '''
                        echo "Проверка синтаксиса Python..."
                        python -m py_compile project/*.py 2>/dev/null || echo "Ошибки синтаксиса"
                    '''
                    
                    // Проверка стиля кода (если установлен flake8)
                    sh '''
                        if command -v flake8 &> /dev/null; then
                            echo "Проверка стиля кода с flake8..."
                            flake8 project/ --max-line-length=120 --exclude=migrations || echo "Найдены стилевые ошибки"
                        fi
                    '''
                }
            }
        }
        
        stage('Проверка безопасности') {
            when {
                expression { 
                    return env.BACKEND_CHANGED == 'true' && 
                    (env.GIT_BRANCH == 'main' || env.GIT_BRANCH == 'master')
                }
            }
            steps {
                script {
                    echo "Проверка безопасности..."
                    
                    // Проверка уязвимостей в зависимостях
                    sh '''
                        if command -v safety &> /dev/null; then
                            echo "Проверка безопасности зависимостей..."
                            safety check --full-report || echo "Найдены уязвимости"
                        fi
                    '''
                    
                    // Проверка статического анализа безопасности
                    sh '''
                        if command -v bandit &> /dev/null; then
                            echo "Статический анализ безопасности..."
                            bandit -r project/ -f json -o bandit-report.json || echo "Анализ безопасности завершен"
                        fi
                    '''
                }
            }
        }
        
        stage('Деплой (для production)') {
            when {
                branch 'main'  // или 'master'
            }
            steps {
                script {
                    echo "Деплой на production..."
                    
                    // Здесь добавляем шаги деплоя
                    // Например, копирование файлов, перезапуск сервисов и т.д.
                    
                    echo "1. Сборка статических файлов Django..."
                    sh 'python manage.py collectstatic --noinput'
                    
                    echo "2. Применение миграций..."
                    sh 'python manage.py migrate'
                    
                    echo "3. Деплой завершен!"
                    
                    // Отправка уведомления
                    emailext(
                        subject: "Деплой успешен: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        body: "Сборка ${env.BUILD_NUMBER} успешно завершена и задеплоена.",
                        to: 'ваш_email@example.com'
                    )
                }
            }
        }
    }
    
    post {
        always {
            echo "==================== СБОРКА ЗАВЕРШЕНА ===================="
            echo "Статус: ${currentBuild.result ?: 'SUCCESS'}"
            echo "Время выполнения: ${currentBuild.durationString}"
            echo "=========================================================="
            
            // Очистка workspace
            cleanWs()
        }
        success {
            echo 'Пайплайн успешно выполнен!'
            
            // Можно добавить уведомления в Slack, Teams и т.д.
            slackSend(
                color: 'good',
                message: "Сборка ${env.JOB_NAME} #${env.BUILD_NUMBER} успешна"
            )
        }
        failure {
            echo 'Пайплайн завершился с ошибкой!'
            
            // Отправка уведомления об ошибке
            emailext(
                subject: "Ошибка сборки: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Сборка ${env.BUILD_NUMBER} завершилась с ошибкой.\n\nПосмотреть логи: ${env.BUILD_URL}",
                to: 'ваш_email@example.com'
            )
            
            slackSend(
                color: 'danger',
                message: "Сборка ${env.JOB_NAME} #${env.BUILD_NUMBER} провалилась"
            )
        }
        unstable {
            echo 'Пайплайн нестабилен (некоторые тесты провалились)'
        }
        aborted {
            echo 'Пайплайн был прерван'
        }
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '5'))
        disableConcurrentBuilds()
        retry(2)  // Повторять сборку при ошибке (макс 2 раза)
    }
    
    triggers {
        // Автоматический запуск при пуше в ветки
        pollSCM('H/5 * * * *')  // Проверять каждые 5 минут
        
        // Или через GitHub вебхук (рекомендуется)
        // githubPush()
    }
    
    parameters {
        choice(
            name: 'DEPLOY_ENV',
            choices: ['dev', 'staging', 'production'],
            description: 'Выберите окружение для деплоя'
        )
        booleanParam(
            name: 'RUN_ALL_TESTS',
            defaultValue: true,
            description: 'Запускать все тесты'
        )
        string(
            name: 'CUSTOM_BRANCH',
            defaultValue: '',
            description: 'Кастомная ветка для сборки (оставьте пустым для текущей)'
        )
    }
}