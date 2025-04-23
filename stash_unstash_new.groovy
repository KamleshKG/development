// --- Scripted Pipeline (Pure Groovy) ---

// Get all nodes and their labels (including master)
def nodes = Jenkins.instance.nodes
def masterNode = Jenkins.instance  // Master is not in 'nodes', but accessible directly

// Find the master's label (defaults to 'master' if none set)
def masterLabel = masterNode.labelString ?: 'master'
echo "Master node label: ${masterLabel}"

// --- Pipeline Stages ---
node('windows') {  // Target Windows agent
    stage('Fetch File from Master') {
        // Run on master to stash the file (using dynamically detected label)
        node(masterLabel) {
            echo "Fetching file from master (${env.JENKINS_HOME}/plugins/)"
            stash(
                name: 'plugin-hpi',
                includes: "${env.JENKINS_HOME}/plugins/your-plugin.hpi",
                allowEmpty: false
            )
        }
    }

    stage('Deploy on Windows') {
        unstash('plugin-hpi')
        bat """
            mkdir "C:\\Jenkins\\Plugins\\" 2>nul || echo "Directory exists"
            copy "your-plugin.hpi" "C:\\Jenkins\\Plugins\\"
            echo "File copied to C:\\Jenkins\\Plugins\\"
        """
    }
}