pipeline{

	agent any

	environment {
		DOCKERHUB_CREDENTIALS=credentials('dockerhub')
	}

	stages {
	    
	    stage('gitclone') {

			steps {
				git 'https://github.com/Noyarodrigo/cloudwatch_nginx_phpfpm_logger.git'
			}
		}

		stage('Build') {

			steps {
				sh "docker build -t roi96/cloudwatch_nginx_phpfpm_logger:1.0.0-${BUILD_ID}  ."
			}
		}

		stage('Login') {

			steps {
				sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
			}
		}

		stage('Push') {

			steps {
				sh "docker push roi96/cloudwatch_nginx_phpfpm_logger:1.0.0-${BUILD_ID}"
			}
		}
	}

	post {
		always {
			sh 'docker logout'
		}
	}

}
