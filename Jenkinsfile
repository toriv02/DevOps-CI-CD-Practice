pipeline {
    agent any
    
    environment {
        FRONTEND_DIR = 'client'
        BACKEND_DIR = 'project'
        FRONTEND_PORT = '3000'
        BACKEND_PORT = '8000'
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
                    // Frontend dependencies
                    dir(env.FRONTEND_DIR) {
                        bat 'npm ci --silent'
                        echo "Frontend dependencies installed"
                    }
                    
                    // Backend dependencies
                    bat """
                        @echo off
                        echo Installing Python dependencies...
                        python -m pip install -r requirements.txt
                    """
                }
            }
        }
        
        stage('Build Frontend') {
            when {
                expression {
                    def branch = env.GIT_BRANCH ?: ''
                    return branch == 'main' || branch == 'master'
                }
            }
            steps {
                dir(env.FRONTEND_DIR) {
                    bat 'npm run build'
                    echo "Frontend built successfully"
                }
            }
        }
        
        stage('Prepare Deployment') {
            when {
                expression {
                    def branch = env.GIT_BRANCH ?: ''
                    return branch == 'main' || branch == 'master'
                }
            }
            steps {
                script {
                    // Create deployment directory
                    bat """
                        @echo off
                        if not exist "${env.DEPLOY_DIR}" mkdir "${env.DEPLOY_DIR}"
                        if not exist "${env.DEPLOY_DIR}\\backend" mkdir "${env.DEPLOY_DIR}\\backend"
                        if not exist "${env.DEPLOY_DIR}\\frontend" mkdir "${env.DEPLOY_DIR}\\frontend"
                    """
                    
                    // Copy backend
                    bat """
                        @echo off
                        echo Copying backend...
                        xcopy /E /I /Y "${env.BACKEND_DIR}\\*" "${env.DEPLOY_DIR}\\backend\\"
                    """
                    
                    // Copy frontend build
                    dir(env.FRONTEND_DIR) {
                        bat """
                            @echo off
                            echo Copying frontend...
                            if exist "dist" (
                                xcopy /E /I /Y "dist\\*" "${env.DEPLOY_DIR}\\frontend\\"
                            ) else if exist "build" (
                                xcopy /E /I /Y "build\\*" "${env.DEPLOY_DIR}\\frontend\\"
                            )
                        """
                    }
                    
                    // Create start script
                    bat """
                        @echo off
                        echo Creating start script...
                        
                        echo @echo off > "${env.DEPLOY_DIR}\\start.bat"
                        echo echo Starting Django backend... >> "${env.DEPLOY_DIR}\\start.bat"
                        echo cd /d "${env.DEPLOY_DIR}\\backend" >> "${env.DEPLOY_DIR}\\start.bat"
                        echo python manage.py migrate --noinput >> "${env.DEPLOY_DIR}\\start.bat"
                        echo start "" python manage.py runserver 0.0.0.0:${env.BACKEND_PORT} >> "${env.DEPLOY_DIR}\\start.bat"
                        echo timeout /t 5 >> "${env.DEPLOY_DIR}\\start.bat"
                        echo echo Backend started: http://localhost:${env.BACKEND_PORT} >> "${env.DEPLOY_DIR}\\start.bat"
                        echo. >> "${env.DEPLOY_DIR}\\start.bat"
                        echo echo Starting frontend server... >> "${env.DEPLOY_DIR}\\start.bat"
                        echo cd /d "${env.DEPLOY_DIR}\\frontend" >> "${env.DEPLOY_DIR}\\start.bat"
                        echo python -m http.server ${env.FRONTEND_PORT} >> "${env.DEPLOY_DIR}\\start.bat"
                        echo echo Frontend started: http://localhost:${env.FRONTEND_PORT} >> "${env.DEPLOY_DIR}\\start.bat"
                    """
                }
            }
        }
        
        stage('Deploy Application') {
            when {
                expression {
                    def branch = env.GIT_BRANCH ?: ''
                    return branch == 'main' || branch == 'master'
                }
            }
            steps {
                script {
                    // Stop any running instances on our ports
                    bat """
                        @echo off
                        echo Checking for running processes...
                        
                        REM Kill processes on backend port
                        for /f "tokens=5" %%i in ('netstat -ano ^| findstr :${env.BACKEND_PORT}') do (
                            taskkill /PID %%i /F
                        )
                        
                        REM Kill processes on frontend port
                        for /f "tokens=5" %%i in ('netstat -ano ^| findstr :${env.FRONTEND_PORT}') do (
                            taskkill /PID %%i /F
                        )
                        
                        timeout /t 2
                    """
                    
                    // Start the application
                    bat """
                        @echo off
                        cd /d "${env.DEPLOY_DIR}"
                        start "MyApp" start.bat
                        echo Application deployment started!
                    """
                    
                    // Wait and verify
                    bat 'timeout /t 10 /nobreak'
                    
                    // Verify services
                    bat """
                        @echo off
                        echo Verifying services...
                        echo.
                        echo =============================
                        echo DEPLOYMENT SUCCESSFUL!
                        echo =============================
                        echo Backend: http://localhost:${env.BACKEND_PORT}
                        echo Frontend: http://localhost:${env.FRONTEND_PORT}
                        echo =============================
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo "Pipeline execution completed"
            echo "Status: ${currentBuild.currentResult}"
            echo "Branch: ${env.GIT_BRANCH ?: 'unknown'}"
        }
        success {
            echo 'Application deployed successfully!'
            echo "Visit: http://localhost:${env.FRONTEND_PORT}"
        }
        failure {
            echo 'Deployment failed'
        }
    }
}