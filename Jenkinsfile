pipeline {
  agent any
  triggers {
    githubPush()
    pollSCM('H H * * *')
  }
  environment {
    MAIL_RECIPIENTS = 'dev+tests-reports@wazo.community'
  }
  options {
    skipStagesAfterUnstable()
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }
  stages {
    stage('Debian build and deploy') {
      steps {
        build job: 'build-package-no-arch', parameters: [
          string(name: 'PACKAGE', value: "${JOB_NAME}"),
        ]
      }
    }
    stage('Docker build confd-db') {
      steps {
        build job: 'build-docker', parameters: [
          string(name: 'GIT_URL', value: 'https://github.com/wazo-platform/xivo-manage-db.git'),
          string(name: 'IMAGE', value: 'wazoplatform/wazo-confd-db'),
          booleanParam(name: 'DOCKER_CACHE', value: false),
        ]
      }
    }
    stage('Docker build confd-db-test') {
      steps {
        build job: 'build-docker', parameters: [
          string(name: 'GIT_URL', value: 'https://github.com/wazo-platform/xivo-manage-db.git'),
          string(name: 'IMAGE', value: 'wazoplatform/wazo-confd-db-test'),
          string(name: 'DOCKERFILE', value: 'contribs/docker/wazo-confd-db-test/Dockerfile'),
        ]
      }
    }
  }
  post {
    failure {
      emailext to: "${MAIL_RECIPIENTS}", subject: '${DEFAULT_SUBJECT}', body: '${DEFAULT_CONTENT}'
    }
    fixed {
      emailext to: "${MAIL_RECIPIENTS}", subject: '${DEFAULT_SUBJECT}', body: '${DEFAULT_CONTENT}'
    }
  }
}
