// Nightly Doc2Test pipeline as deployed in Wideverse's CI/CD (paper §5).
// Single Jenkins stage wrapping the Docker image; auto-generated suites
// are version-controlled and editable by QA engineers if desired.
pipeline {
    agent any

    environment {
        DOC2TEST_IMAGE      = "doc2test:1.0"
        UAT_DIR             = "uats/"
        STAGING_URL         = credentials('client-staging-url')
        OPENAI_API_KEY      = credentials('openai-api-key')
        GEMINI_API_KEY      = credentials('gemini-api-key')
        ARTIFACTS           = "target/junit"
    }

    options {
        timeout(time: 90, unit: 'MINUTES')
        ansiColor('xterm')
    }

    stages {
        stage('Doc2Test - Generate & Execute') {
            steps {
                sh '''
                    mkdir -p ${ARTIFACTS}
                    docker run --rm \
                        -e OPENAI_API_KEY -e GEMINI_API_KEY \
                        -v "$WORKSPACE/${UAT_DIR}":/app/uats:ro \
                        -v "$WORKSPACE/${ARTIFACTS}":/app/target/junit \
                        ${DOC2TEST_IMAGE} batch \
                        --uat-dir /app/uats \
                        --url ${STAGING_URL} \
                        --junit /app/target/junit \
                        --max-retries 3
                '''
            }
        }

        stage('Publish JUnit') {
            steps {
                junit "${ARTIFACTS}/*.xml"
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: "${ARTIFACTS}/**/*.xml,traces/**/*.json", allowEmptyArchive: true
        }
    }
}
