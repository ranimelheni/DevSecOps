// =============================================================================
// Pipeline DevSecOps - Secure Notes API
// =============================================================================

pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 10, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '10'))
    }

    stages {

        // ---------------------------------------------------------------------
        // 1. Checkout du code source
        // ---------------------------------------------------------------------
        stage('Checkout') {
            steps {
                checkout scm

                echo 'Repository checked out successfully.'

                sh '''
                    set -eu

                    echo "Current directory:"
                    pwd

                    echo "Checking project structure..."

                    test -f Jenkinsfile
                    test -f Dockerfile
                    test -f requirements.txt
                    test -d app

                    echo "Project structure verified."
                '''
            }
        }

    }

    post {
        success {
            echo 'SUCCESS: Checkout and project verification passed.'
        }

        failure {
            echo 'FAILED: Check the Jenkins console output.'
        }
    }
}