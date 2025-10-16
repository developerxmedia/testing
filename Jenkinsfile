pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/developerxmedia/testing.git'
        BRANCH_NAME = "${env.BRANCH_NAME ?: 'master'}"
        PYTHON_VERSION = '3.9'
        NODE_VERSION = '16'
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
                    url: "${REPO_URL}", 
                    credentialsId: 'github-credentials'
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    sh 'python3 -m venv venv'
                    sh '. venv/bin/activate'
                    sh 'pip install -r requirements.txt || true'
                    
                    nodejs(nodeJSInstallationName: 'Node 16') {
                        sh 'npm install'
                    }
                }
            }
        }

        stage('Lint') {
            parallel {
                stage('Python Lint') {
                    steps {
                        sh 'python3 -m pylint **/*.py || true'
                    }
                }
                stage('JavaScript Lint') {
                    steps {
                        sh 'npx eslint . || true'
                    }
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    sh 'python3 -m pytest tests/ || true'
                    sh 'npm test || true'
                }
            }
            post {
                always {
                    junit 'test-results/*.xml'
                    cobertura coberturaReportFile: 'coverage.xml'
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    sh 'python3 setup.py sdist bdist_wheel'
                    sh 'npm run build'
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'master'
                expression { params.DEPLOYMENT_TARGET == 'production' }
            }
            steps {
                script {
                    if (params.DEPLOYMENT_TARGET == 'production') {
                        sh 'pip install twine'
                        sh 'twine upload dist/*'
                        sh 'npm publish'
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
            slackSend color: 'good', 
                      message: "Build ${env.JOB_NAME} ${env.BUILD_NUMBER} succeeded!"
        }
        failure {
            echo 'Pipeline failed!'
            slackSend color: 'danger', 
                      message: "Build ${env.JOB_NAME} ${env.BUILD_NUMBER} failed!"
        }
        cleanup {
            sh 'rm -rf venv'
            sh 'npm cache clean --force'
            deleteDir()
        }
    }
}