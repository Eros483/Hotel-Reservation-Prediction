pipeline{
    agent any

    stages{
        stage('Cloning Github repo to jenkins'){
            steps{
                script{
                    echo 'cloning github repo to jenkins...'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Eros483/Hotel-Reservation-Prediction']])
                }
            }
        }
    }
}