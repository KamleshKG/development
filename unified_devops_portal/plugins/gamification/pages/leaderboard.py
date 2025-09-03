import importlib.util
import os
import json
import streamlit as st
from pathlib import Path

def load_plugins(plugins_dir="plugins"):
    """Discover and load all plugins from the plugins directory"""
    plugins = []
    
    for plugin_name in os.listdir(plugins_dir):
        plugin_path = Path(plugins_dir) / plugin_name
        plugin_json_path = plugin_path / "plugin.json"
        
        if plugin_path.is_dir() and plugin_json_path.exists():
            try:
                with open(plugin_json_path, 'r') as f:
                    plugin_info = json.load(f)
                    plugin_info['path'] = str(plugin_path)
                    plugins.append(plugin_info)
                    st.sidebar.success(f"✅ Loaded: {plugin_info['name']}")
            except Exception as e:
                st.sidebar.error(f"❌ Failed to load {plugin_name}: {str(e)}")
    
    return plugins

def get_plugin_page(plugin_slug, page_module):
    """Dynamically import a plugin page module"""
    try:
        module_path = f"plugins.{plugin_slug}.{page_module.replace('/', '.')}"
        spec = importlib.util.find_spec(module_path)
        
        if spec is None:
            raise ImportError(f"Module {module_path} not found")
        
        module = importlib.import_module(module_path)
        return module
        
    except Exception as e:
        st.error(f"Error loading plugin page: {str(e)}")
        return None