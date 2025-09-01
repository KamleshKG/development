import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import hashlib
import time
import json
from io import StringIO
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import importlib.util
import sys
import os

# Page configuration
st.set_page_config(
    page_title="DevOps Transformation Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -------------------------------
# Plugin Architecture Foundation
# -------------------------------

class DataSourcePlugin(ABC):
    """Abstract base class for data source plugins"""

    @abstractmethod
    def get_identifier(self) -> str:
        """Return a unique identifier for this data source"""
        pass

    @abstractmethod
    def get_display_name(self) -> str:
        """Return a user-friendly name for this data source"""
        pass

    @abstractmethod
    def load_data(self, selected_team: Optional[str] = None,
                  time_range: int = 12, **kwargs) -> Tuple[pd.DataFrame, pd.DataFrame, Dict, pd.DataFrame, Dict]:
        """
        Load data from the source

        Returns:
            Tuple containing:
            - dora_data: DataFrame with DORA metrics over time
            - team_df: DataFrame with team performance data
            - security_data: Dict with security metrics
            - cost_data: DataFrame with cost data
            - team_modifier: Dict with team-specific modifiers
        """
        pass

    @abstractmethod
    def get_available_teams(self) -> List[str]:
        """Return list of available teams in the data source"""
        pass

    @abstractmethod
    def get_data_fields_mapping(self) -> Dict[str, str]:
        """
        Return mapping of expected field names to actual field names in the data source
        This allows different data sources to have different field names
        """
        pass

    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """Test connection to the data source"""
        pass


class VisualizationPlugin(ABC):
    """Abstract base class for visualization plugins"""

    @abstractmethod
    def get_identifier(self) -> str:
        """Return a unique identifier for this visualization"""
        pass

    @abstractmethod
    def get_display_name(self) -> str:
        """Return a user-friendly name for this visualization"""
        pass

    @abstractmethod
    def render(self, data: Dict[str, Any], **kwargs) -> None:
        """Render the visualization using the provided data"""
        pass


# -------------------------------
# Plugin Manager
# -------------------------------

class PluginManager:
    """Manages data source and visualization plugins"""

    def __init__(self):
        self.data_sources: Dict[str, DataSourcePlugin] = {}
        self.visualizations: Dict[str, VisualizationPlugin] = {}
        self.load_builtin_plugins()

    def load_builtin_plugins(self):
        """Load built-in plugins"""
        # Add static demo data source
        self.register_data_source(StaticDemoDataSource())
        # Add CSV data source
        self.register_data_source(CSVDataSource())

    def register_data_source(self, data_source: DataSourcePlugin):
        """Register a data source plugin"""
        self.data_sources[data_source.get_identifier()] = data_source

    def register_visualization(self, visualization: VisualizationPlugin):
        """Register a visualization plugin"""
        self.visualizations[visualization.get_identifier()] = visualization

    def get_data_source(self, identifier: str) -> Optional[DataSourcePlugin]:
        """Get a data source by identifier"""
        return self.data_sources.get(identifier)

    def get_data_source_options(self) -> List[Dict[str, str]]:
        """Get available data sources as options for UI"""
        return [
            {"identifier": id, "name": source.get_display_name()}
            for id, source in self.data_sources.items()
        ]

    def load_plugins_from_directory(self, directory: str):
        """Load plugins from a directory (for extensibility)"""
        if not os.path.exists(directory):
            os.makedirs(directory)
            return

        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('_'):
                try:
                    module_name = filename[:-3]  # Remove .py extension
                    spec = importlib.util.spec_from_file_location(
                        module_name, os.path.join(directory, filename))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Look for classes that inherit from DataSourcePlugin or VisualizationPlugin
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and
                                issubclass(obj, (DataSourcePlugin, VisualizationPlugin)) and
                                obj not in (DataSourcePlugin, VisualizationPlugin)):

                            # Instantiate and register the plugin
                            plugin_instance = obj()
                            if isinstance(plugin_instance, DataSourcePlugin):
                                self.register_data_source(plugin_instance)
                            elif isinstance(plugin_instance, VisualizationPlugin):
                                self.register_visualization(plugin_instance)

                            st.success(f"Loaded plugin: {name}")

                except Exception as e:
                    st.error(f"Error loading plugin {filename}: {str(e)}")


# -------------------------------
# Data Field Definitions
# -------------------------------

# Define the expected data structure for the dashboard
DATA_FIELD_SPEC = {
    "dora_data": {
        "required_fields": ["date", "lead_time_minutes", "deployment_frequency",
                            "change_fail_rate", "mttr_minutes"],
        "optional_fields": [],
        "field_descriptions": {
            "date": "Date of measurement (datetime)",
            "lead_time_minutes": "Lead time for changes in minutes (numeric)",
            "deployment_frequency": "Number of deployments per week (numeric)",
            "change_fail_rate": "Percentage of changes that result in failure (numeric)",
            "mttr_minutes": "Mean time to recovery in minutes (numeric)"
        }
    },
    "team_data": {
        "required_fields": ["team", "dora_score"],
        "optional_fields": ["lead_time_minutes", "deployment_frequency", "change_fail_rate",
                            "mttr_minutes", "tech_debt_ratio", "ai_readiness_score",
                            "cloud_maturity", "automation_level"],
        "field_descriptions": {
            "team": "Team name (string)",
            "dora_score": "Overall DORA performance score 0-100 (numeric)",
            "lead_time_minutes": "Current lead time in minutes (numeric)",
            "deployment_frequency": "Current deployment frequency (numeric)",
            "change_fail_rate": "Current change failure rate percentage (numeric)",
            "mttr_minutes": "Current mean time to recovery in minutes (numeric)",
            "tech_debt_ratio": "Technical debt ratio (numeric)",
            "ai_readiness_score": "AI readiness score 0-100 (numeric)",
            "cloud_maturity": "Cloud maturity score 0-100 (numeric)",
            "automation_level": "Automation level score 0-100 (numeric)"
        }
    },
    "security_data": {
        "required_fields": ["vulnerabilities_critical", "vulnerabilities_high",
                            "vulnerabilities_medium", "vulnerabilities_low"],
        "optional_fields": ["secrets_rotation_compliance", "vault_usage_rate", "last_pen_test_score"],
        "field_descriptions": {
            "vulnerabilities_critical": "Number of critical vulnerabilities (integer)",
            "vulnerabilities_high": "Number of high severity vulnerabilities (integer)",
            "vulnerabilities_medium": "Number of medium severity vulnerabilities (integer)",
            "vulnerabilities_low": "Number of low severity vulnerabilities (integer)",
            "secrets_rotation_compliance": "Secrets rotation compliance percentage (numeric)",
            "vault_usage_rate": "Vault usage rate percentage (numeric)",
            "last_pen_test_score": "Last penetration test score 0-5 (numeric)"
        }
    },
    "cost_data": {
        "required_fields": ["month", "infrastructure_cost"],
        "optional_fields": ["storage_cost", "ci_cd_cost"],
        "field_descriptions": {
            "month": "Month identifier (string)",
            "infrastructure_cost": "Infrastructure cost in dollars (numeric)",
            "storage_cost": "Storage cost in dollars (numeric)",
            "ci_cd_cost": "CI/CD pipeline cost in dollars (numeric)"
        }
    }
}


# -------------------------------
# Built-in Data Source Plugins
# -------------------------------

class StaticDemoDataSource(DataSourcePlugin):
    """Static demo data source (existing functionality)"""

    def get_identifier(self) -> str:
        return "static_demo"

    def get_display_name(self) -> str:
        return "Static Demo Data"

    def get_available_teams(self) -> List[str]:
        return ['Team Alpha', 'Team Beta', 'Team Gamma', 'Team Delta', 'Team Epsilon']

    def get_data_fields_mapping(self) -> Dict[str, str]:
        # For static demo, field names match exactly
        return {field: field for field in
                list(DATA_FIELD_SPEC["dora_data"]["field_descriptions"].keys()) +
                list(DATA_FIELD_SPEC["team_data"]["field_descriptions"].keys()) +
                list(DATA_FIELD_SPEC["security_data"]["field_descriptions"].keys()) +
                list(DATA_FIELD_SPEC["cost_data"]["field_descriptions"].keys())}

    def load_data(self, selected_team: Optional[str] = None, time_range: int = 12, **kwargs):
        return generate_dynamic_data(selected_team, time_range)

    def test_connection(self) -> Tuple[bool, str]:
        return True, "Static demo data source is always available"


class CSVDataSource(DataSourcePlugin):
    """CSV data source plugin"""

    def __init__(self):
        self.uploaded_files = {}
        self.field_mapping = {}

    def get_identifier(self) -> str:
        return "csv_upload"

    def get_display_name(self) -> str:
        return "CSV File Upload"

    def get_available_teams(self) -> List[str]:
        # Extract teams from uploaded data if available
        if 'team_data' in self.uploaded_files and not self.uploaded_files['team_data'].empty:
            return self.uploaded_files['team_data']['team'].unique().tolist()
        return ['Team Alpha', 'Team Beta', 'Team Gamma', 'Team Delta', 'Team Epsilon']

    def get_data_fields_mapping(self) -> Dict[str, str]:
        return self.field_mapping

    def load_data(self, selected_team: Optional[str] = None, time_range: int = 12, **kwargs):
        # Check if we have uploaded files
        if not self.uploaded_files:
            st.warning("Please upload CSV files first in the Data Source Config tab")
            return generate_dynamic_data(selected_team, time_range)

        try:
            # Process DORA data
            dora_data = self.uploaded_files.get('dora_data', pd.DataFrame())
            if not dora_data.empty and selected_team:
                dora_data = dora_data[dora_data['team'] == selected_team]

            # Process team data
            team_df = self.uploaded_files.get('team_data', pd.DataFrame())

            # Process security data
            security_data = {}
            if 'security_data' in self.uploaded_files:
                security_df = self.uploaded_files['security_data']
                if not security_df.empty and selected_team:
                    security_df = security_df[security_df['team'] == selected_team]
                if not security_df.empty:
                    security_data = security_df.iloc[-1].to_dict()

            # Process cost data
            cost_data = self.uploaded_files.get('cost_data', pd.DataFrame())
            if not cost_data.empty and selected_team:
                cost_data = cost_data[cost_data['team'] == selected_team]

            # For demo purposes, return a team modifier
            team_modifier = {'perf': 1.0, 'stability': 1.0, 'speed': 1.0, 'ai_readiness': 1.0}

            return dora_data, team_df, security_data, cost_data, team_modifier

        except Exception as e:
            st.error(f"Error processing CSV data: {str(e)}")
            # Fall back to demo data
            return generate_dynamic_data(selected_team, time_range)

    def test_connection(self) -> Tuple[bool, str]:
        if self.uploaded_files:
            return True, "CSV files uploaded successfully"
        return False, "No CSV files uploaded"


# -------------------------------
# Data Validation and Transformation
# -------------------------------

class DataValidator:
    """Validates and transforms data from various sources to expected format"""

    def __init__(self, field_spec: Dict[str, Any]):
        self.field_spec = field_spec

    def validate_data(self, data: Dict[str, Any], field_mapping: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate data against the field specification

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        for data_type, spec in self.field_spec.items():
            if data_type not in data:
                errors.append(f"Missing data type: {data_type}")
                continue

            data_df = data[data_type] if data_type != "security_data" else pd.DataFrame([data[data_type]])

            # Check required fields
            for field in spec["required_fields"]:
                mapped_field = field_mapping.get(field, field)
                if mapped_field not in data_df.columns:
                    errors.append(f"Missing required field '{field}' (mapped as '{mapped_field}') in {data_type}")

            # Check data types
            for field, description in spec["field_descriptions"].items():
                mapped_field = field_mapping.get(field, field)
                if mapped_field in data_df.columns:
                    # Basic type checking based on description
                    if "numeric" in description and not pd.api.types.is_numeric_dtype(data_df[mapped_field]):
                        errors.append(f"Field '{field}' should be numeric but is {data_df[mapped_field].dtype}")
                    elif "integer" in description and not pd.api.types.is_integer_dtype(data_df[mapped_field]):
                        errors.append(f"Field '{field}' should be integer but is {data_df[mapped_field].dtype}")

        return len(errors) == 0, errors

    def transform_data(self, data: Dict[str, Any], field_mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Transform data to use expected field names
        """
        transformed = {}

        for data_type, data_value in data.items():
            if data_type not in self.field_spec:
                continue

            if isinstance(data_value, pd.DataFrame):
                # Create a copy with renamed columns
                df = data_value.copy()
                reverse_mapping = {v: k for k, v in field_mapping.items() if
                                   k in self.field_spec[data_type]["field_descriptions"]}
                df.rename(columns=reverse_mapping, inplace=True)

                # Ensure correct data types
                for field, description in self.field_spec[data_type]["field_descriptions"].items():
                    if field in df.columns:
                        if "numeric" in description:
                            df[field] = pd.to_numeric(df[field], errors='coerce')
                        elif "integer" in description:
                            df[field] = pd.to_numeric(df[field], errors='coerce').astype('Int64')

                transformed[data_type] = df
            else:
                # For dict data (like security_data), transform keys
                if isinstance(data_value, dict):
                    transformed_dict = {}
                    reverse_mapping = {v: k for k, v in field_mapping.items() if
                                       k in self.field_spec[data_type]["field_descriptions"]}
                    for key, value in data_value.items():
                        transformed_key = reverse_mapping.get(key, key)
                        transformed_dict[transformed_key] = value
                    transformed[data_type] = transformed_dict
                else:
                    transformed[data_type] = data_value

        return transformed


# -------------------------------
# Dashboard Core with Plugin Architecture
# -------------------------------

class DevOpsDashboard:
    """Main dashboard class with plugin architecture"""

    def __init__(self):
        self.plugin_manager = PluginManager()
        self.data_validator = DataValidator(DATA_FIELD_SPEC)
        self.current_data_source = None
        self.current_data = None
        self.field_mapping = {}

    def render_sidebar(self):
        """Render the dashboard sidebar"""
        st.sidebar.header("Dashboard Controls")

        # Data source selection
        data_source_options = self.plugin_manager.get_data_source_options()
        selected_data_source_id = st.sidebar.selectbox(
            "Select Data Source",
            options=[ds["identifier"] for ds in data_source_options],
            format_func=lambda x: next((ds["name"] for ds in data_source_options if ds["identifier"] == x), x)
        )

        self.current_data_source = self.plugin_manager.get_data_source(selected_data_source_id)

        if self.current_data_source:
            # Team selection based on available teams from data source
            available_teams = self.current_data_source.get_available_teams()
            selected_team = st.sidebar.selectbox("Select Team", available_teams)

            # Other controls
            time_range = st.sidebar.slider("Time Range (weeks)", 4, 26, 12)
            view_mode = st.sidebar.radio("View Mode",
                                         ["Team View", "Enterprise View", "AI Transformation", "Maturity Journey"])

            # Load data button
            if st.sidebar.button("Load Data"):
                with st.spinner("Loading data..."):
                    try:
                        # Load data from the selected source
                        dora_data, team_df, security_data, cost_data, team_modifier = self.current_data_source.load_data(
                            selected_team, time_range
                        )

                        # Store the field mapping for this data source
                        self.field_mapping = self.current_data_source.get_data_fields_mapping()

                        # Prepare data for validation
                        raw_data = {
                            "dora_data": dora_data,
                            "team_data": team_df,
                            "security_data": security_data,
                            "cost_data": cost_data
                        }

                        # Validate and transform data
                        is_valid, errors = self.data_validator.validate_data(raw_data, self.field_mapping)

                        if not is_valid:
                            st.error("Data validation failed:")
                            for error in errors:
                                st.error(f"- {error}")
                            return None, None, None, None

                        # Transform data to standard format
                        transformed_data = self.data_validator.transform_data(raw_data, self.field_mapping)

                        self.current_data = {
                            "dora_data": transformed_data["dora_data"],
                            "team_df": transformed_data["team_data"],
                            "security_data": transformed_data["security_data"],
                            "cost_data": transformed_data["cost_data"],
                            "team_modifier": team_modifier,
                            "selected_team": selected_team,
                            "time_range": time_range,
                            "view_mode": view_mode
                        }

                        st.success("Data loaded successfully!")

                    except Exception as e:
                        st.error(f"Error loading data: {str(e)}")
                        return None, None, None, None

            return selected_team, time_range, view_mode

        return None, None, None

    def render_data_health_check(self):
        """Render data health check section"""
        if self.current_data and self.current_data_source:
            st.sidebar.subheader("Data Health Check")

            # Check data freshness if we have date data
            if not self.current_data["dora_data"].empty and 'date' in self.current_data["dora_data"].columns:
                latest_date = self.current_data["dora_data"]['date'].max()
                if pd.api.types.is_datetime64_any_dtype(self.current_data["dora_data"]['date']):
                    days_old = (pd.Timestamp.now() - latest_date).days

                    if days_old <= 1:
                        st.sidebar.success("✅ Data is up to date (last 24 hours)")
                    elif days_old <= 7:
                        st.sidebar.info(f"ℹ️ Data is {days_old} days old")
                    else:
                        st.sidebar.warning(f"⚠️ Data is {days_old} days old")

            # Check data completeness
            complete = True
            for data_type, spec in DATA_FIELD_SPEC.items():
                if data_type in ["dora_data", "team_data", "cost_data"]:
                    df = self.current_data[data_type] if data_type != "team_data" else self.current_data["team_df"]
                    for field in spec["required_fields"]:
                        if field not in df.columns or df[field].isnull().all():
                            complete = False
                            break

            if complete:
                st.sidebar.success("✅ All required data fields are present")
            else:
                st.sidebar.error("❌ Some required data fields are missing")

    def render_data_source_config_tab(self):
        """Render Data Source Configuration tab"""
        st.header("🔧 Data Source Configuration")

        st.subheader("Current Data Source")
        if self.current_data_source:
            st.info(f"**{self.current_data_source.get_display_name()}** - {self.current_data_source.get_identifier()}")

            # Test connection button
            if st.button("Test Connection"):
                with st.spinner("Testing connection..."):
                    success, message = self.current_data_source.test_connection()
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

            # Show field mapping
            st.subheader("Field Mapping")
            mapping_df = pd.DataFrame([
                {"Expected Field": k, "Mapped Field": v}
                for k, v in self.field_mapping.items()
            ])
            st.dataframe(mapping_df, use_container_width=True)
        else:
            st.warning("No data source selected")

        # Data source configuration
        st.subheader("Configure Data Sources")

        # CSV data source configuration
        if isinstance(self.current_data_source, CSVDataSource):
            self.render_csv_config()

        # Plugin management
        st.subheader("Plugin Management")
        plugins_dir = st.text_input("Plugins Directory", value="./plugins")

        if st.button("Load Plugins from Directory"):
            with st.spinner("Loading plugins..."):
                self.plugin_manager.load_plugins_from_directory(plugins_dir)
                st.success("Plugins loaded successfully!")

    def render_csv_config(self):
        """Render CSV configuration UI"""
        st.write("Upload CSV files for each data type")

        # File uploaders for each data type
        dora_file = st.file_uploader("DORA Metrics Data (CSV)", type=["csv"])
        team_file = st.file_uploader("Team Performance Data (CSV)", type=["csv"])
        security_file = st.file_uploader("Security Metrics Data (CSV)", type=["csv"])
        cost_file = st.file_uploader("Cost Data (CSV)", type=["csv"])

        # Process uploaded files
        if dora_file:
            self.current_data_source.uploaded_files['dora_data'] = pd.read_csv(dora_file)
            st.success(f"Loaded DORA data: {dora_file.name}")

        if team_file:
            self.current_data_source.uploaded_files['team_data'] = pd.read_csv(team_file)
            st.success(f"Loaded team data: {team_file.name}")

        if security_file:
            self.current_data_source.uploaded_files['security_data'] = pd.read_csv(security_file)
            st.success(f"Loaded security data: {security_file.name}")

        if cost_file:
            self.current_data_source.uploaded_files['cost_data'] = pd.read_csv(cost_file)
            st.success(f"Loaded cost data: {cost_file.name}")

        # Field mapping configuration
        if any(self.current_data_source.uploaded_files.values()):
            st.subheader("Field Mapping Configuration")

            # Get all unique columns from uploaded files
            all_columns = set()
            for df in self.current_data_source.uploaded_files.values():
                if not df.empty:
                    all_columns.update(df.columns)

            # Create mapping UI
            for field_type, spec in DATA_FIELD_SPEC.items():
                for field in spec["required_fields"] + spec["optional_fields"]:
                    current_mapping = self.current_data_source.field_mapping.get(field, "")
                    available_columns = [""] + sorted(list(all_columns))

                    new_mapping = st.selectbox(
                        f"Map '{field}' to:",
                        options=available_columns,
                        index=available_columns.index(current_mapping) if current_mapping in available_columns else 0,
                        key=f"mapping_{field}"
                    )

                    if new_mapping:
                        self.current_data_source.field_mapping[field] = new_mapping

            if st.button("Save Field Mapping"):
                st.success("Field mapping saved successfully!")


# -------------------------------
# Existing Helper Functions (keep all the original functions)
# -------------------------------

# [ALL THE ORIGINAL FUNCTIONS REMAIN HERE UNCHANGED]
# get_team_seed(), get_dora_targets(), get_benchmark_data(),
# generate_dynamic_data(), generate_enterprise_maturity(),
# predict_future_metrics(), generate_team_roadmap(),
# generate_enterprise_roadmap(), generate_tooling_maturity_data(),
# generate_qa_data(), generate_quiz_data(), init_session_state()

# -------------------------------
# Modified Main Function with Plugin Architecture
# -------------------------------

def main():
    st.title("🚀 DevOps Transformation Dashboard")
    st.markdown("### Production-Ready with Plugin Architecture")

    # Initialize session state
    init_session_state()

    # Initialize the dashboard with plugin architecture
    dashboard = DevOpsDashboard()

    # Render sidebar and get settings
    selected_team, time_range, view_mode = dashboard.render_sidebar()

    # Render data health check
    dashboard.render_data_health_check()

    # Check if we have data to display
    if dashboard.current_data:
        # Extract data for use in tabs
        dora_data = dashboard.current_data["dora_data"]
        team_df = dashboard.current_data["team_df"]
        security_data = dashboard.current_data["security_data"]
        cost_data = dashboard.current_data["cost_data"]
        team_modifier = dashboard.current_data["team_modifier"]
        selected_team = dashboard.current_data["selected_team"]
        time_range = dashboard.current_data["time_range"]
        view_mode = dashboard.current_data["view_mode"]

        # Generate additional data needed for the dashboard
        enterprise_maturity = generate_enterprise_maturity()
        tooling_data, adoption_data, tooling_roadmap = generate_tooling_maturity_data(selected_team)

        # Generate appropriate roadmap based on view mode
        if view_mode == "Team View":
            roadmap_phases, roadmap_initiatives = generate_team_roadmap(selected_team, team_df)
        else:
            roadmap_phases, roadmap_initiatives = generate_enterprise_roadmap(team_df)

        # Generate Q&A and Quiz data
        qa_data = generate_qa_data()
        quiz_data = generate_quiz_data()

        # Main dashboard with tabs (now includes Data Source Config tab)
        tab_names = [
            "DORA Metrics", "Team Performance", "Security & Compliance",
            "Cost Optimization", "Transformation Roadmap", "AI Transformation",
            "Maturity Journey", "Tooling Maturity", "Q&A for Management",
            "DevOps Quiz", "Team Socialize", "Data Source Config"
        ]

        tabs = st.tabs(tab_names)

        # Render each tab (using the original tab rendering code)
        # [ALL THE ORIGINAL TAB RENDERING CODE GOES HERE]
        # with tabs[0]: render_dora_metrics_tab()
        # with tabs[1]: render_team_performance_tab()
        # ... etc.

        # Add the new Data Source Config tab
        with tabs[11]:
            dashboard.render_data_source_config_tab()

    else:
        st.info("Please select a data source and click 'Load Data' to begin")


# Run the dashboard
if __name__ == "__main__":
    main()