// Main application
function initializeApp() {
    console.log('Initializing application with vis version:', vis.version);

    let network = null;
    const container = document.getElementById('network');
    const analyzeBtn = document.getElementById('analyzeBtn');

    // Initialize container
    container.style.width = '100%';
    container.style.height = '600px';
    container.style.backgroundColor = 'white';
    container.style.border = '1px solid #ddd';

    // Test visualization
    const testData = {
        nodes: [
            {id: 1, label: 'Test Class', color: '#E3F2FD', title: 'Sample test node'}
        ],
        edges: []
    };
    createVisualization(testData);

    // Set up analyze button
    analyzeBtn.addEventListener('click', analyzeCode);

    async function analyzeCode() {
        const folderPath = document.getElementById('folderPath').value.trim();
        if (!folderPath) {
            showError('Please enter a folder path');
            return;
        }

        try {
            showLoading('Analyzing code...');

            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ folder_path: folderPath })
            });

            const data = await response.json();
            createVisualization(data);

        } catch (error) {
            showError('Analysis failed: ' + error.message);
        }
    }

    function createVisualization(data) {
        // Clear previous
        if (network) {
            network.destroy();
        }

        // Create new visualization
        const nodes = new vis.DataSet(data.nodes || []);
        const edges = new vis.DataSet(data.links || []);

        network = new vis.Network(container, { nodes, edges }, {
            layout: {
                hierarchical: {
                    direction: 'UD',
                    nodeSpacing: 150
                }
            },
            physics: {
                hierarchicalRepulsion: {
                    nodeDistance: 200
                }
            }
        });
    }

    // Helper functions
    function showLoading(message) {
        container.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">${message}</p>
            </div>
        `;
    }

    function showError(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger';
        alert.textContent = message;
        container.appendChild(alert);
    }
}

// Make initializeApp available globally
window.initializeApp = initializeApp;