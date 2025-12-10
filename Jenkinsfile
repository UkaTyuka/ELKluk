pipeline {
    agent { label 'l1' }

    environment {
        PYTHONNOUSERSITE = "1"
        SSH_KEY_PATH     = "/home/ubuntu/id_rsa_elk_tf"   // приватный ключ, которым ты ходишь на ВМ
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Smoke test (local)') {
            steps {
                sh """
                    # на машине Jenkins: собрать и проверить, что API вообще живой
                    docker-compose down -v || true
                    docker-compose up -d --build
                    sleep 15
                    curl -f http://localhost:8000/health
                """
            }
        }

        stage('Terraform: provision infra') {
            steps {
                dir('openstack') {
                    sh """
                        terraform init -input=false
                        terraform apply -auto-approve -input=false
                    """
                }
            }
        }

        stage('Ansible: deploy to ELK VM') {
            steps {
                script {
                    // Получаем IP из Terraform output
                    def elkIp = sh(
                        script: "cd openstack && terraform output -raw elk_vm_ip",
                        returnStdout: true
                    ).trim()

                    echo "ELK VM IP from Terraform: ${elkIp}"

                    // Генерируем inventory.ini с нужным IP
                    sh """
                        cd ansible
                        cat > inventory.ini <<EOF
[elk]
${elkIp} ansible_user=ubuntu ansible_ssh_private_key_file=${SSH_KEY_PATH}
EOF

                        ansible-playbook -i inventory.ini playbook.yml
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline SUCCESS: build + infra + deploy completed."
        }
        failure {
            echo "Pipeline FAILED."
        }
    }
}
