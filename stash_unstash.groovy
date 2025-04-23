pipeline {
    agent none
    stages {
        // --- STAGE 1: Stash .hpi file from Jenkins master (Linux) ---
        stage('Stash .hpi from Master') {
            agent { label 'master' }  // Force execution on the master node
            steps {
                script {
                    // Verify the .hpi file exists
                    sh """
                        echo "Master JENKINS_HOME: ${env.JENKINS_HOME}"
                        ls -la "${env.JENKINS_HOME}/plugins/your-plugin.hpi"
                    """
                    // Stash the file for transfer
                    stash(
                        name: 'plugin-hpi',
                        includes: "${env.JENKINS_HOME}/plugins/your-plugin.hpi",
                        allowEmpty: false  // Fail if file is missing
                    )
                }
            }
        }

        // --- STAGE 2: Copy to Windows agent ---
        stage('Copy to Windows Agent') {
            agent { label 'windows' }  // Runs on Windows agent
            steps {
                script {
                    // Unstash the file (saved to workspace root)
                    unstash('plugin-hpi')
                    // Verify and copy to a target directory
                    bat """
                        echo "Workspace contents:"
                        dir
                        mkdir "C:\\Jenkins\\Plugins\\" 2>nul || echo "Directory exists"
                        copy "your-plugin.hpi" "C:\\Jenkins\\Plugins\\"
                        echo "Copied to C:\\Jenkins\\Plugins\\"
                        dir "C:\\Jenkins\\Plugins\\"
                    """
                }
            }
        }
    }
}