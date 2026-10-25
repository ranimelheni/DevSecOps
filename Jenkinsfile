
// =============================================================================
// Pipeline DevSecOps - Secure Notes API
// Plugins requis : Pipeline, Docker Pipeline, JUnit
// Prerequis : agent Linux avec Docker utilisable par Jenkins
// =============================================================================

// Contrôle du comportement des security gates :
// ENFORCE_GATES = true  -> un échec bloque le build
// ENFORCE_GATES = false -> un échec marque le build UNSTABLE et continue
def gate(String name, Closure body) {
    if (params.ENFORCE_GATES == null || params.ENFORCE_GATES) {
        body()
    } else {
        catchError(
            buildResult: 'UNSTABLE',
            stageResult: 'UNSTABLE',
            message: "${name} : constats non bloquants (ENFORCE_GATES=false)"
        ) {
            body()
        }
    }
}

pipeline {
    agent any

    parameters {
        booleanParam(
            name: 'ENFORCE_GATES',
            defaultValue: true,
            description: 'true = les contrôles bloquent le build ; false = rapport seulement (UNSTABLE)'
        )
    }

    options {
        timestamps()
        timeout(time: 10, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(
            logRotator(
                numToKeepStr: '20',
                artifactNumToKeepStr: '10'
            )
        )
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

                    test -f requirements.txt
                    test -d app

                    echo "Project structure verified."
                '''
            }
        }

        // ---------------------------------------------------------------------
        // 2. Tests automatisés avec pytest et vérification de couverture
        // ---------------------------------------------------------------------
        stage('Tests - pytest') {
            agent {
                docker {
                    image 'python:3.12-slim'
                    reuseNode true
                }
            }

            steps {
                script {
                    gate('Tests') {
                        sh '''#!/bin/bash
                            set -euo pipefail

                            export HOME=/tmp
                            export PATH="$PATH:/tmp/.local/bin"
                            export PIP_DISABLE_PIP_VERSION_CHECK=1

                            echo "Installing test dependencies..."
                            pip install --user -q -r requirements-dev.txt coverage

                            echo "Running tests..."
                            coverage run -m pytest -q --junitxml=junit.xml

                            echo "Generating coverage report..."
                            coverage xml -o coverage.xml

                            echo "Checking test coverage..."
                            coverage report --fail-under=80
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            junit(
                allowEmptyResults: true,
                testResults: 'junit.xml'
            )

            archiveArtifacts(
                artifacts: 'junit.xml, coverage.xml',
                allowEmptyArchive: true,
                fingerprint: true
            )
        }

        success {
            echo 'SUCCESS: Checkout and pytest completed.'
        }

        unstable {
            echo 'UNSTABLE: A check failed, but ENFORCE_GATES=false.'
        }

        failure {
            echo 'FAILED: Check the Jenkins Console Output.'
        }
    }
}
