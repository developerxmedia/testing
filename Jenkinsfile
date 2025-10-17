pipeline {
    agent any

    environment {
        GITHUB_REPO = 'https://github.com/developerxmedia/testing.git'
        BRANCH_NAME = "${env.BRANCH_NAME ?: 'master'}"
        PYTHON_VERSION = '3.9'
        CREDENTIALS_ID = 'github-credentials'
    }

    parameters {
        choice(name: 'DEPLOYMENT_TARGET', choices: ['staging', 'production'], description: 'Deployment environment')
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: "${BRANCH_NAME}", 
                    credentialsId: "${CREDENTIALS_ID}", 
                    url: "${GITHUB_REPO}"
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt || true
                    '''
                }
            }
        }

        stage('Lint') {
            steps {
                script {
                    sh '''
                        . venv/bin/activate
                        pylint **/*.py || true
                        flake8 . || true
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    sh '''
                        . venv/bin/activate
                        python3 -m pytest tests/ || true
                    '''
                }
            }
            post {
                always {
                    junit 'test-reports/*.xml'
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    sh '''
                        . venv/bin/activate
                        python3 setup.py sdist bdist_wheel || true
                    '''
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'master'
            }
            steps {
                script {
                    if (params.DEPLOYMENT_TARGET == 'production') {
                        sh '''
                            echo "Deploying to production"
                            # Add production deployment commands
                        '''
                    } else {
                        sh '''
                            echo "Deploying to staging"
                            # Add staging deployment commands
                        '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
            emailext(
                subject: "Jenkins Build ${currentBuild.currentResult}: Job ${env.JOB_NAME}",
                body: "Build succeeded. Check console output at ${env.BUILD_URL}",
                to: 'team@company.com'
            )
        }
        failure {
            echo 'Pipeline failed!'
            emailext(
                subject: "Jenkins Build ${currentBuild.currentResult}: Job ${env.JOB_NAME}",
                body: "Build failed. Check console output at ${env.BUILD_URL}",
                to: 'team@company.com'
            )
        }
        always {
            cleanWs()
        }
    }
}