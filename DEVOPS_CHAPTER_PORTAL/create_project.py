import os
import json
from pathlib import Path

def create_directory(path):
    """Create directory if it doesn't exist"""
    os.makedirs(path, exist_ok=True)
    print(f"📁 Created: {path}")

def create_file(file_path, content=""):
    """Create file with content"""
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"📄 Created: {file_path}")

def create_devops_chapter_structure():
    """Create the complete DevOps Chapter structure"""
    base_dir = "copilot_unified_portal"
    
    # Core structure
    core_dirs = [
        f"{base_dir}/core",
        f"{base_dir}/core/models",
        f"{base_dir}/core/templates",
        f"{base_dir}/utils",
        f"{base_dir}/plugins"
    ]
    
    for dir_path in core_dirs:
        create_directory(dir_path)
    
    # Create core files
    create_file(f"{base_dir}/core/__init__.py", "# Core Portal Engine")
    create_file(f"{base_dir}/core/app.py", "# Main application file")
    create_file(f"{base_dir}/core/auth.py", "# Authentication logic")
    create_file(f"{base_dir}/core/plugin_loader.py", "# Plugin loader")
    create_file(f"{base_dir}/core/data_collector.py", "# Data collection utilities")
    create_file(f"{base_dir}/core/models/core_models.py", "# Core database models")
    create_file(f"{base_dir}/core/templates/value_dashboard.py", "# Dashboard templates")
    
    # Utils files
    create_file(f"{base_dir}/utils/__init__.py", "# Utilities package")
    create_file(f"{base_dir}/utils/email_utils.py", "# Email utilities")
    
    # Requirements
    create_file(f"{base_dir}/requirements.txt", """streamlit>=1.22.0
sqlite3
python-dotenv
pyyaml
""")

def create_plugins_structure():
    """Create all plugins structure"""
    base_dir = "copilot_unified_portal/plugins"
    
    # Plugin directories
    plugins = ["gamification", "innovation", "devops_chapter", "backlog_ai"]
    
    for plugin in plugins:
        plugin_dirs = [
            f"{base_dir}/{plugin}",
            f"{base_dir}/{plugin}/models",
            f"{base_dir}/{plugin}/pages",
            f"{base_dir}/{plugin}/quests" if plugin == "gamification" else None,
            f"{base_dir}/{plugin}/data" if plugin == "devops_chapter" else None,
            f"{base_dir}/{plugin}/data/usecases" if plugin == "devops_chapter" else None,
            f"{base_dir}/{plugin}/data/best_practices" if plugin == "devops_chapter" else None,
            f"{base_dir}/{plugin}/templates" if plugin == "devops_chapter" else None,
            f"{base_dir}/{plugin}/templates/deployment" if plugin == "devops_chapter" else None,
            f"{base_dir}/{plugin}/templates/monitoring" if plugin == "devops_chapter" else None,
            f"{base_dir}/{plugin}/templates/incident_response" if plugin == "devops_chapter" else None
        ]
        
        for dir_path in plugin_dirs:
            if dir_path:  # Skip None values
                create_directory(dir_path)
        
        # Create plugin __init__.py
        create_file(f"{base_dir}/{plugin}/__init__.py", f"# {plugin.title()} Plugin")
        
        # Create plugin.json
        if plugin == "devops_chapter":
            create_devops_chapter_plugin_json(f"{base_dir}/{plugin}/plugin.json")
        else:
            create_file(f"{base_dir}/{plugin}/plugin.json", "{}")
        
        # Create model files
        create_file(f"{base_dir}/{plugin}/models/__init__.py", f"# {plugin.title()} Models")
        
        # Create page files for devops_chapter
        if plugin == "devops_chapter":
            create_devops_chapter_pages(f"{base_dir}/{plugin}/pages")

def create_devops_chapter_plugin_json(file_path):
    """Create the devops_chapter plugin.json"""
    plugin_config = {
        "name": "DevOps Chapter",
        "description": "Daily productivity utilities for DevOps engineers, SREs, and developers",
        "version": "2.0.0",
        "pages": [
            {
                "name": "DevOps Dashboard",
                "module": "utilities_dashboard",
                "function": "render"
            },
            {
                "name": "Use Cases Library",
                "module": "usecases_library",
                "function": "render"
            },
            {
                "name": "Best Practices",
                "module": "bestpractices_library",
                "function": "render"
            },
            {
                "name": "Incident Resolver",
                "module": "incident_resolver",
                "function": "render"
            },
            {
                "name": "Daily Checklist",
                "module": "daily_checklist",
                "function": "render"
            },
            {
                "name": "Template Library",
                "module": "template_library",
                "function": "render"
            },
            {
                "name": "Roadmap Builder",
                "module": "roadmap_builder",
                "function": "render"
            },
            {
                "name": "Code Validator",
                "module": "code_validator",
                "function": "render"
            },
            {
                "name": "Cheatsheets",
                "module": "cheatsheets",
                "function": "render"
            }
        ]
    }
    
    with open(file_path, 'w') as f:
        json.dump(plugin_config, f, indent=2)
    print(f"📄 Created: {file_path}")

def create_devops_chapter_pages(pages_dir):
    """Create all devops_chapter page files"""
    pages = [
        "utilities_dashboard.py",
        "usecases_library.py",
        "bestpractices_library.py",
        "incident_resolver.py",
        "daily_checklist.py",
        "template_library.py",
        "roadmap_builder.py",
        "code_validator.py",
        "cheatsheets.py"
    ]
    
    for page in pages:
        create_file(f"{pages_dir}/{page}", f"# {page.replace('_', ' ').title().replace('.Py', '')}\n\ndef render(user):\n    \"\"\"Render this page\"\"\"\n    pass")

def create_sample_data_files():
    """Create sample data files for devops_chapter"""
    base_dir = "copilot_unified_portal/plugins/devops_chapter/data"
    
    # Sample use cases
    use_cases = {
        "deployment_issues.json": [
            {
                "id": "deploy-001",
                "title": "Blue-Green Deployment Failure",
                "description": "Issues during blue-green deployment switching",
                "problem": "Traffic not routing correctly to new deployment",
                "solution": [
                    "Verify load balancer health checks",
                    "Check deployment readiness probes",
                    "Execute rollback procedure if needed"
                ],
                "severity": "high",
                "frequency": "medium",
                "tags": ["deployment", "kubernetes", "loadbalancer"]
            }
        ],
        "performance_issues.json": [
            {
                "id": "perf-001",
                "title": "High CPU Usage",
                "description": "Application experiencing high CPU utilization",
                "problem": "Service responding slowly due to CPU saturation",
                "solution": [
                    "Check application profiling data",
                    "Review recent code changes",
                    "Optimize database queries",
                    "Scale horizontally if needed"
                ],
                "severity": "medium",
                "frequency": "high",
                "tags": ["performance", "cpu", "optimization"]
            }
        ]
    }
    
    for filename, data in use_cases.items():
        with open(f"{base_dir}/usecases/{filename}", 'w') as f:
            json.dump(data, f, indent=2)
        print(f"📄 Created: {base_dir}/usecases/{filename}")
    
    # Sample best practices
    best_practices = {
        "terraform_best_practices.json": [
            {
                "title": "Use Remote State Storage",
                "description": "Store Terraform state in remote backend",
                "maturity": "basic",
                "impact": "high",
                "effort": "low",
                "implementation": [
                    "Configure S3 backend for AWS",
                    "Use state locking to prevent conflicts"
                ]
            }
        ],
        "kubernetes_best_practices.json": [
            {
                "title": "Resource Limits and Requests",
                "description": "Set proper resource limits for containers",
                "maturity": "basic",
                "impact": "high",
                "effort": "medium",
                "implementation": [
                    "Set CPU and memory requests",
                    "Configure appropriate limits",
                    "Use Quality of Service classes"
                ]
            }
        ]
    }
    
    for filename, data in best_practices.items():
        with open(f"{base_dir}/best_practices/{filename}", 'w') as f:
            json.dump(data, f, indent=2)
        print(f"📄 Created: {base_dir}/best_practices/{filename}")

def create_readme():
    """Create README file"""
    readme_content = """# DevOps Chapter - Unified Portal

## 🚀 Overview

This is a comprehensive DevOps productivity hub featuring:

### Core Features
- **Use Cases Library**: Common DevOps scenarios and solutions
- **Best Practices**: Industry-standard guidelines
- **Incident Resolver**: Diagnostic tools for production issues
- **Daily Checklists**: Role-based operational checklists
- **Template Library**: Ready-to-use configuration templates
- **Code Validator**: JSON/YAML/XML validation tools
- **Cheatsheets**: Quick references for DevOps tools

### Plugins Architecture
- **Gamification**: Quest-based learning and achievements
- **Innovation Portal**: Idea submission and collaboration
- **DevOps Chapter**: Productivity utilities (this plugin)
- **Backlog AI**: AI-assisted backlog management

## 🏗️ Structure"""


