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

# Page configuration
st.set_page_config(
    page_title="DevOps Transformation Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Helper function to generate consistent seed from team name
def get_team_seed(team_name):
    """Generate a consistent numeric seed from team name string"""
    if team_name is None:
        return 42
    # Use hash of team name to create a consistent seed between 0 and 2**32-1
    hash_obj = hashlib.md5(team_name.encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    return hash_int % (2 ** 32 - 1)


# Enhanced data loader class (inspired by the provided project)
class DevOpsDataLoader:
    """
    A class to handle all data provisioning for the DevOps dashboard.
    This class is designed for extensibility to various data sources.
    """

    def __init__(self):
        # Configuration for data source
        self.source_type = "static_demo"  # Options: "static_demo", "csv", "database"

    def _load_from_static_data(self, selected_team=None, time_range=12):
        """Loads data from our existing generate_dynamic_data function"""
        return generate_dynamic_data(selected_team, time_range)

    def _load_from_csv(self, file_path):
        """Loads data from a CSV file."""
        st.info(f"Loading data from CSV: {file_path}")
        # Placeholder for future implementation
        return self._load_from_static_data()

    def _load_from_database(self, query):
        """Loads data from a database."""
        st.info(f"Connecting to database with query: {query}")
        # Placeholder for future implementation
        return self._load_from_static_data()

    def load_data(self, selected_team=None, time_range=12):
        """
        Main method to load data based on the configured source type.
        This is the single entry point for all data provisioning.
        """
        if self.source_type == "static_demo":
            return self._load_from_static_data(selected_team, time_range)
        elif self.source_type == "csv":
            return self._load_from_csv("dummy_path.csv")
        elif self.source_type == "database":
            return self._load_from_database("SELECT * FROM your_table")
        else:
            st.error("Invalid data source type configured.")
            return pd.DataFrame()


# Enhanced metrics functions (inspired by the provided project)
def get_dora_targets():
    """Returns the DORA metrics target configuration."""
    return {
        "lead_time_minutes": {"goal": 60, "unit": " min", "class": "negative", "initial": 240,
                              "display_name": "Lead Time"},
        "deployment_frequency": {"goal": 20, "unit": "/ week", "class": "positive",
                                 "display_name": "Deployment Frequency"},
        "change_fail_rate": {"goal": 5, "unit": "%", "class": "negative", "initial": 15,
                             "display_name": "Change Failure Rate"},
        "mttr_minutes": {"goal": 30, "unit": " min", "class": "negative", "initial": 120, "display_name": "MTTR"}
    }


def get_benchmark_data():
    """Returns industry benchmark data for comparison."""
    return {
        'Category': ['Elite', 'High', 'Medium', 'Low'],
        'deployment_frequency': [45, 20, 10, 5],
        'lead_time_minutes': [60, 120, 240, 480],
        'change_fail_rate': [5, 10, 15, 20],
        'mttr_minutes': [30, 60, 120, 240]
    }


# Generate dynamic demo data based on team and time range
def generate_dynamic_data(selected_team=None, time_range=12):
    # Set seed for reproducibility but with team-based variation
    team_seed = get_team_seed(selected_team)
    np.random.seed(team_seed)
    random.seed(team_seed)

    dates = pd.date_range(start='2024-01-01', end='2024-06-15', freq='W')
    n_dates = len(dates)

    # Team-specific performance modifiers
    team_modifiers = {
        'Team Alpha': {'perf': 1.2, 'stability': 0.9, 'speed': 1.1, 'ai_readiness': 1.4},
        'Team Beta': {'perf': 0.8, 'stability': 1.1, 'speed': 0.9, 'ai_readiness': 0.6},
        'Team Gamma': {'perf': 1.0, 'stability': 1.0, 'speed': 1.0, 'ai_readiness': 1.0},
        'Team Delta': {'perf': 1.1, 'stability': 0.8, 'speed': 1.2, 'ai_readiness': 0.9},
        'Team Epsilon': {'perf': 0.9, 'stability': 1.2, 'speed': 0.8, 'ai_readiness': 1.1}
    }

    modifier = team_modifiers.get(selected_team, {'perf': 1.0, 'stability': 1.0, 'speed': 1.0, 'ai_readiness': 1.0})

    # Add realistic noise and trends
    base_trend = np.linspace(1, 0.5, n_dates)

    dora_data = pd.DataFrame({
        'date': dates,
        'lead_time_minutes': np.maximum(1800 * base_trend * modifier['speed'] + np.random.normal(0, 30, n_dates), 240),
        'deployment_frequency': np.minimum(
            5 + np.arange(n_dates) * 0.8 * modifier['speed'] + np.random.normal(0, 2, n_dates), 45),
        'change_fail_rate': np.maximum(15 * base_trend * modifier['stability'] + np.random.normal(0, 1.5, n_dates),
                                       2.5),
        'mttr_minutes': np.maximum(240 * base_trend * modifier['stability'] + np.random.normal(0, 15, n_dates), 25)
    })

    # Add some realistic spikes and anomalies
    spike_indices = random.sample(range(n_dates), 3)
    for idx in spike_indices:
        dora_data.loc[idx, 'change_fail_rate'] *= 2.5  # Bad deployment
        dora_data.loc[idx, 'mttr_minutes'] *= 1.8  # Took longer to recover

    # Team performance data with variations
    teams = ['Team Alpha', 'Team Beta', 'Team Gamma', 'Team Delta', 'Team Epsilon']
    team_performance = []

    for team in teams:
        team_mod = team_modifiers[team]
        team_performance.append({
            'team': team,
            'dora_score': int(np.random.randint(65, 95) * team_mod['perf']),
            'lead_time_minutes': int(np.random.randint(120, 480) / team_mod['speed']),
            'deployment_frequency': int(np.random.randint(10, 50) * team_mod['speed']),
            'change_fail_rate': np.random.uniform(2.0, 12.0) / team_mod['stability'],
            'mttr_minutes': int(np.random.randint(30, 180) / team_mod['stability']),
            'tech_debt_ratio': np.random.uniform(5.0, 20.0) * (1.3 if team_mod['perf'] < 1 else 0.8),
            'ai_readiness_score': int(60 * team_mod['ai_readiness']),
            'cloud_maturity': int(70 * team_mod['perf']),
            'automation_level': int(65 * team_mod['speed'])
        })

    team_df = pd.DataFrame(team_performance)

    # Security metrics with team variations
    security_data = {
        'vulnerabilities_critical': max(5, int(12 * (1.5 if modifier['perf'] < 1 else 0.7))),
        'vulnerabilities_high': max(20, int(45 * (1.3 if modifier['perf'] < 1 else 0.8))),
        'vulnerabilities_medium': max(80, int(128 * (1.2 if modifier['perf'] < 1 else 0.9))),
        'vulnerabilities_low': max(150, int(256 * (1.1 if modifier['perf'] < 1 else 0.95))),
        'secrets_rotation_compliance': max(70, 87.5 * modifier['perf']),
        'vault_usage_rate': max(85, 92.3 * modifier['perf']),
        'last_pen_test_score': max(3.5, 4.2 * modifier['perf'])
    }

    # Cost optimization data with team variations
    cost_modifier = 0.9 if modifier['perf'] > 1 else 1.1
    cost_data = pd.DataFrame({
        'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'infrastructure_cost': [int(125000 * cost_modifier),
                                int(118000 * cost_modifier),
                                int(110000 * cost_modifier),
                                int(105000 * cost_modifier),
                                int(98000 * cost_modifier),
                                int(92000 * cost_modifier)],
        'storage_cost': [int(45000 * cost_modifier),
                         int(42000 * cost_modifier),
                         int(38000 * cost_modifier),
                         int(35000 * cost_modifier),
                         int(32000 * cost_modifier),
                         int(28500 * cost_modifier)],
        'ci_cd_cost': [int(28000 * cost_modifier),
                       int(27500 * cost_modifier),
                       int(27000 * cost_modifier),
                       int(26500 * cost_modifier),
                       int(26000 * cost_modifier),
                       int(25500 * cost_modifier)]
    })

    return dora_data, team_df, security_data, cost_data, modifier


# Generate enterprise maturity data
def generate_enterprise_maturity():
    """Generate enterprise-wide maturity assessment"""
    # Current state (based on weighted average of teams)
    current_devops = 68  # Weighted average
    current_devsecops = 62

    # Target state for next year
    target_devops = 85
    target_devsecops = 80

    # Maturity breakdown by category
    maturity_categories = [
        'Culture & Process', 'Automation', 'Measurement', 'Sharing', 'Security'
    ]

    current_scores = [65, 70, 60, 75, 62]
    target_scores = [85, 90, 80, 85, 80]

    return {
        'current_devops': current_devops,
        'current_devsecops': current_devsecops,
        'target_devops': target_devops,
        'target_devsecops': target_devsecops,
        'maturity_categories': maturity_categories,
        'current_scores': current_scores,
        'target_scores': target_scores
    }


# ML Prediction function with realistic noise
def predict_future_metrics(current_metrics, selected_team=None):
    future_dates = pd.date_range(start='2024-07-01', end='2024-12-31', freq='M')
    predictions = []

    # Team-specific prediction modifiers
    team_modifiers = {
        'Team Alpha': {'improvement': 1.2, 'volatility': 0.8},
        'Team Beta': {'improvement': 0.8, 'volatility': 1.2},
        'Team Gamma': {'improvement': 1.0, 'volatility': 1.0},
        'Team Delta': {'improvement': 1.1, 'volatility': 0.9},
        'Team Epsilon': {'improvement': 0.9, 'volatility': 1.1}
    }

    modifier = team_modifiers.get(selected_team, {'improvement': 1.0, 'volatility': 1.0})

    for i, date in enumerate(future_dates):
        improvement_factor = 0.85 * modifier['improvement']
        volatility = 0.05 * modifier['volatility']

        predictions.append({
            'date': date,
            'predicted_lead_time': max(180, current_metrics['lead_time_minutes'].iloc[-1] *
                                       (improvement_factor ** (i + 1)) *
                                       (1 + np.random.normal(0, volatility))),
            'predicted_fail_rate': max(1.8, current_metrics['change_fail_rate'].iloc[-1] *
                                       (0.9 * modifier['improvement'] ** (i + 1)) *
                                       (1 + np.random.normal(0, volatility))),
            'predicted_mttr': max(20, current_metrics['mttr_minutes'].iloc[-1] *
                                  (0.88 * modifier['improvement'] ** (i + 1)) *
                                  (1 + np.random.normal(0, volatility)))
        })

    return pd.DataFrame(predictions)


# Generate team-specific transformation roadmap
def generate_team_roadmap(selected_team, team_df):
    """Generate a transformation roadmap specific to the selected team"""
    team_info = team_df[team_df['team'] == selected_team].iloc[0]

    # Define roadmap based on team characteristics
    if selected_team == 'Team Alpha':
        phases = [
            {'phase': 'AI Integration', 'start': '2024-07-01', 'end': '2024-09-30', 'progress': 30,
             'status': 'In Progress', 'priority': 'High', 'dependencies': 'None'},
            {'phase': 'Advanced Monitoring', 'start': '2024-08-01', 'end': '2024-10-31', 'progress': 15,
             'status': 'Not Started', 'priority': 'High', 'dependencies': 'AI Integration'},
            {'phase': 'Predictive Scaling', 'start': '2024-10-01', 'end': '2024-12-31', 'progress': 0,
             'status': 'Not Started', 'priority': 'Medium', 'dependencies': 'Advanced Monitoring'},
        ]
    elif selected_team == 'Team Beta':
        phases = [
            {'phase': 'Foundation Setup', 'start': '2024-07-01', 'end': '2024-10-31', 'progress': 20,
             'status': 'In Progress', 'priority': 'High', 'dependencies': 'None'},
            {'phase': 'Basic Automation', 'start': '2024-09-01', 'end': '2024-12-31', 'progress': 5,
             'status': 'Not Started', 'priority': 'High', 'dependencies': 'Foundation Setup'},
            {'phase': 'CI/CD Pipeline', 'start': '2025-01-01', 'end': '2025-03-31', 'progress': 0,
             'status': 'Not Started', 'priority': 'Medium', 'dependencies': 'Basic Automation'},
        ]
    else:
        phases = [
            {'phase': 'Process Optimization', 'start': '2024-07-01', 'end': '2024-08-31', 'progress': 45,
             'status': 'In Progress', 'priority': 'High', 'dependencies': 'None'},
            {'phase': 'Tool Standardization', 'start': '2024-08-15', 'end': '2024-10-31', 'progress': 20,
             'status': 'In Progress', 'priority': 'High', 'dependencies': 'Process Optimization'},
            {'phase': 'Quality Gates', 'start': '2024-10-01', 'end': '2024-12-31', 'progress': 0,
             'status': 'Not Started', 'priority': 'Medium', 'dependencies': 'Tool Standardization'},
        ]

    # Add team-specific key initiatives
    initiatives = []
    if team_info['ai_readiness_score'] > 75:
        initiatives.extend([
            {'initiative': 'AI-Powered Testing', 'status': 'Planned', 'impact': 'High', 'team': selected_team},
            {'initiative': 'Predictive Deployment', 'status': 'Backlog', 'impact': 'Medium', 'team': selected_team},
        ])
    elif team_info['ai_readiness_score'] < 50:
        initiatives.extend([
            {'initiative': 'Basic Automation', 'status': 'In Progress', 'impact': 'High', 'team': selected_team},
            {'initiative': 'CI/CD Foundation', 'status': 'Planned', 'impact': 'High', 'team': selected_team},
        ])
    else:
        initiatives.extend([
            {'initiative': 'Test Automation', 'status': 'In Progress', 'impact': 'High', 'team': selected_team},
            {'initiative': 'Monitoring Setup', 'status': 'Planned', 'impact': 'Medium', 'team': selected_team},
        ])

    return phases, initiatives


# Generate enterprise transformation roadmap
def generate_enterprise_roadmap(team_df):
    """Generate an enterprise-wide transformation roadmap"""
    # Core enterprise initiatives
    phases = [
        {'phase': 'Platform Standardization', 'start': '2024-07-01', 'end': '2024-09-30', 'progress': 40,
         'status': 'In Progress', 'priority': 'High', 'dependencies': 'None'},
        {'phase': 'Security Baseline', 'start': '2024-08-01', 'end': '2024-10-31', 'progress': 25,
         'status': 'In Progress', 'priority': 'High', 'dependencies': 'Platform Standardization'},
        {'phase': 'AI Enablement', 'start': '2024-10-01', 'end': '2024-12-31', 'progress': 10,
         'status': 'Not Started', 'priority': 'Medium', 'dependencies': 'Security Baseline'},
    ]

    # Team-specific initiatives based on their maturity
    initiatives = []
    for _, team in team_df.iterrows():
        if team['ai_readiness_score'] > 75:
            initiatives.append({'initiative': f'AI Pilot - {team["team"]}', 'status': 'Planned',
                                'impact': 'High', 'team': team['team']})
        elif team['dora_score'] < 70:
            initiatives.append({'initiative': f'Foundation Upgrade - {team["team"]}', 'status': 'In Progress',
                                'impact': 'High', 'team': team['team']})
        else:
            initiatives.append({'initiative': f'Process Optimization - {team["team"]}', 'status': 'Planned',
                                'impact': 'Medium', 'team': team['team']})

    return phases, initiatives


# Generate tooling maturity data based on team
def generate_tooling_maturity_data(selected_team=None):
    # Set seed for reproducibility but with team-based variation
    team_seed = get_team_seed(selected_team)
    np.random.seed(team_seed)
    random.seed(team_seed)

    # Team-specific tooling maturity modifiers
    team_modifiers = {
        'Team Alpha': {'ci_cd': 1.3, 'release': 0.7, 'database': 0.6, 'testing': 1.2, 'monitoring': 1.1},
        'Team Beta': {'ci_cd': 0.7, 'release': 0.4, 'database': 0.5, 'testing': 0.6, 'monitoring': 0.8},
        'Team Gamma': {'ci_cd': 1.0, 'release': 1.0, 'database': 1.0, 'testing': 1.0, 'monitoring': 1.0},
        'Team Delta': {'ci_cd': 1.1, 'release': 0.8, 'database': 0.9, 'testing': 1.1, 'monitoring': 1.2},
        'Team Epsilon': {'ci_cd': 0.9, 'release': 0.6, 'database': 0.7, 'testing': 0.9, 'monitoring': 0.9}
    }

    modifier = team_modifiers.get(selected_team,
                                  {'ci_cd': 1.0, 'release': 1.0, 'database': 1.0, 'testing': 1.0, 'monitoring': 1.0})

    # Generate tooling maturity data
    tooling_data = {
        'ci_cd_maturity': int(65 * modifier['ci_cd']),
        'release_maturity': int(25 * modifier['release']),  # Low due to XLR not onboarded
        'database_maturity': int(30 * modifier['database']),  # Low due to manual Ansible templates
        'testing_maturity': int(25 * modifier['testing']),  # Low due to no automation framework
        'monitoring_maturity': int(60 * modifier['monitoring']),
        'automation_level': int(45 * modifier['ci_cd']),  # Overall automation level
        'tooling_integration': int(40 * min(modifier.values())),  # Weakest link determines integration
    }

    # Tool adoption status
    adoption_data = [
        {'tool': 'CI/CD (Jenkins/GitLab)', 'status': 'Partial', 'automation': 70, 'team': selected_team},
        {'tool': 'Release Management (XLR)', 'status': 'Not Onboarded', 'automation': 10, 'team': selected_team},
        {'tool': 'Database Deployment', 'status': 'Manual Ansible', 'automation': 25, 'team': selected_team},
        {'tool': 'Testing Framework', 'status': 'Not Implemented', 'automation': 20, 'team': selected_team},
        {'tool': 'Monitoring', 'status': 'Basic', 'automation': 65, 'team': selected_team},
    ]

    # Tooling roadmap
    tooling_roadmap = [
        {'initiative': 'XLR Implementation', 'priority': 'High', 'timeline': 'Q3 2024', 'team': selected_team},
        {'initiative': 'Database Automation with Datical', 'priority': 'High', 'timeline': 'Q4 2024',
         'team': selected_team},
        {'initiative': 'Test Automation Framework', 'priority': 'Medium', 'timeline': 'Q1 2025', 'team': selected_team},
        {'initiative': 'CI/CD Optimization', 'priority': 'Medium', 'timeline': 'Q2 2025', 'team': selected_team},
    ]

    return tooling_data, adoption_data, tooling_roadmap


# NEW: Generate Q&A data for management explanations
def generate_qa_data():
    """Generate Q&A data for management explanations"""
    return {
        "DORA Metrics": {
            "description": "Track the four key metrics that measure DevOps performance: Lead Time, Deployment Frequency, Change Failure Rate, and Mean Time to Recovery.",
            "questions": [
                {
                    "question": "What do these metrics tell us about our performance?",
                    "answer": "These metrics provide insights into our delivery speed, stability, and reliability. Elite performers typically have lead times under an hour, deploy multiple times per day, have change failure rates under 5%, and recover from incidents in under an hour."
                },
                {
                    "question": "How do we compare to industry benchmarks?",
                    "answer": "The benchmark comparison shows where we stand against industry standards (Elite, High, Medium, Low performers). Our goal is to reach Elite status across all metrics."
                }
            ]
        },
        "Team Performance": {
            "description": "Compare team performance across various DevOps capabilities and identify areas for improvement.",
            "questions": [
                {
                    "question": "Why are there differences between teams?",
                    "answer": "Team performance varies based on factors like application complexity, technical debt, team experience, and tooling maturity. The radar chart helps visualize strengths and weaknesses across different dimensions."
                },
                {
                    "question": "How can we improve team performance?",
                    "answer": "Focus on targeted improvements based on each team's specific gaps. High-performing teams can share best practices, and we can provide additional resources or training where needed."
                }
            ]
        },
        # Add similar sections for other tabs
    }


# NEW: Generate quiz questions
def generate_quiz_data():
    """Generate quiz questions about DevOps practices"""
    return [
        {
            "question": "What does DORA stand for?",
            "options": [
                "DevOps Research and Assessment",
                "Digital Operations and Reliability Analytics",
                "Development Operations Reporting Association",
                "Deployment Optimization and Recovery Assessment"
            ],
            "correct_answer": 0,
            "explanation": "DORA stands for DevOps Research and Assessment, which is a research program that identifies key capabilities that drive DevOps success."
        },
        {
            "question": "Which of these is NOT one of the four key DORA metrics?",
            "options": [
                "Lead Time for Changes",
                "Deployment Frequency",
                "Code Coverage Percentage",
                "Change Failure Rate"
            ],
            "correct_answer": 2,
            "explanation": "Code Coverage Percentage is a quality metric but not one of the four key DORA metrics. The four DORA metrics are: Lead Time for Changes, Deployment Frequency, Change Failure Rate, and Mean Time to Recovery."
        },
        {
            "question": "What is considered an 'Elite' performance level for Deployment Frequency?",
            "options": [
                "Multiple deploys per day",
                "Once per day",
                "Once per week",
                "Once per month"
            ],
            "correct_answer": 0,
            "explanation": "Elite performers deploy multiple times per day, enabling them to respond quickly to market changes and customer needs."
        },
        {
            "question": "Which practice is most associated with reducing Mean Time to Recovery (MTTR)?",
            "options": [
                "Comprehensive monitoring and alerting",
                "Increasing test coverage",
                "Reducing deployment size",
                "Automating infrastructure provisioning"
            ],
            "correct_answer": 0,
            "explanation": "Comprehensive monitoring and alerting helps quickly identify issues, which is crucial for reducing MTTR. While the other practices contribute to reliability, monitoring directly impacts recovery time."
        }
    ]


# NEW: Initialize session state for social features
def init_session_state():
    """Initialize session state for social features"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = {}
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0


# Create the dashboard
def main():
    st.title("🚀 DevOps Transformation Dashboard")
    st.markdown("### Holistic View of CI/CD Performance, Quality, and Security")

    # Initialize session state
    init_session_state()

    # Sidebar with controls
    st.sidebar.header("Dashboard Controls")
    selected_team = st.sidebar.selectbox("Select Team",
                                         ['Team Alpha', 'Team Beta', 'Team Gamma', 'Team Delta', 'Team Epsilon'])
    time_range = st.sidebar.slider("Time Range (weeks)", 4, 26, 12)
    view_mode = st.sidebar.radio("View Mode", ["Team View", "Enterprise View", "AI Transformation", "Maturity Journey"])

    # Initialize data loader
    loader = DevOpsDataLoader()

    # Generate dynamic data based on selection
    dora_data, team_df, security_data, cost_data, team_modifier = loader.load_data(selected_team, time_range)
    enterprise_maturity = generate_enterprise_maturity()

    # Generate tooling maturity data
    tooling_data, adoption_data, tooling_roadmap = generate_tooling_maturity_data(selected_team)

    # Generate Q&A and Quiz data
    qa_data = generate_qa_data()
    quiz_data = generate_quiz_data()

    # Generate appropriate roadmap based on view mode
    if view_mode == "Team View":
        roadmap_phases, roadmap_initiatives = generate_team_roadmap(selected_team, team_df)
    else:
        roadmap_phases, roadmap_initiatives = generate_enterprise_roadmap(team_df)

    # Main dashboard with 11 tabs (added 3 new tabs)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "DORA Metrics", "Team Performance", "Security & Compliance",
        "Cost Optimization", "Transformation Roadmap", "AI Transformation",
        "Maturity Journey", "Tooling Maturity", "Q&A for Management",
        "DevOps Quiz", "Team Socialize"
    ])

    # Existing tabs 1-8 (unchanged)
    with tab1:
        if view_mode == "Team View":
            st.header(f"📊 DORA Metrics for {selected_team}")
        else:
            st.header("📊 Enterprise DORA Metrics")

        # Enhanced progress visualization with targets (from provided project)
        st.subheader("Strategic Goals & Progress")
        dora_targets = get_dora_targets()
        cols = st.columns(4)

        for i, (metric, data) in enumerate(dora_targets.items()):
            current_val = dora_data[metric].iloc[-1]
            goal = data["goal"]
            unit = data["unit"]
            display_name = data["display_name"]

            with cols[i]:
                st.metric(label=f"Current {display_name}", value=f"{current_val:.1f}{unit}",
                          delta=f"{goal}{unit} Target")

                if data["class"] == "positive":
                    progress_val = np.clip(current_val / goal, 0, 1.0)
                else:
                    initial_val = data["initial"]
                    progress_val = np.clip((initial_val - current_val) / (initial_val - goal), 0, 1.0)

                st.progress(float(progress_val))

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            # Lead Time chart
            fig_lead = px.line(dora_data.tail(time_range), x='date', y='lead_time_minutes',
                               title='Lead Time for Changes (minutes)',
                               labels={'lead_time_minutes': 'Minutes', 'date': 'Date'})
            fig_lead.add_hrect(y0=0, y1=60, line_width=0, fillcolor="green", opacity=0.1)
            fig_lead.add_hrect(y0=60, y1=120, line_width=0, fillcolor="yellow", opacity=0.1)
            fig_lead.add_hrect(y0=120, y1=1000, line_width=0, fillcolor="red", opacity=0.1)
            st.plotly_chart(fig_lead, use_container_width=True)

            # Deployment Frequency chart
            fig_freq = px.line(dora_data.tail(time_range), x='date', y='deployment_frequency',
                               title='Deployment Frequency (per week)',
                               labels={'deployment_frequency': 'Deployments', 'date': 'Date'})
            st.plotly_chart(fig_freq, use_container_width=True)

        with col2:
            # Change Fail Rate chart
            fig_fail = px.line(dora_data.tail(time_range), x='date', y='change_fail_rate',
                               title='Change Failure Rate (%)',
                               labels={'change_fail_rate': 'Failure Rate %', 'date': 'Date'})
            fig_fail.add_hrect(y0=0, y1=5, line_width=0, fillcolor="green", opacity=0.1)
            fig_fail.add_hrect(y0=5, y1=10, line_width=0, fillcolor="yellow", opacity=0.1)
            fig_fail.add_hrect(y0=10, y1=100, line_width=0, fillcolor="red", opacity=0.1)
            st.plotly_chart(fig_fail, use_container_width=True)

            # MTTR chart
            fig_mttr = px.line(dora_data.tail(time_range), x='date', y='mttr_minutes',
                               title='Mean Time to Recovery (minutes)',
                               labels={'mttr_minutes': 'Minutes', 'date': 'Date'})
            st.plotly_chart(fig_mttr, use_container_width=True)

        # Industry benchmark comparison (from provided project)
        st.markdown("---")
        st.subheader("Industry Benchmark Comparison")

        benchmark_data = get_benchmark_data()
        benchmark_df = pd.DataFrame(benchmark_data).set_index('Category')

        selected_metric_benchmark = st.selectbox(
            "Select metric for benchmark comparison:",
            ["deployment_frequency", "lead_time_minutes", "change_fail_rate", "mttr_minutes"],
            format_func=lambda x: dora_targets[x]["display_name"]
        )

        current_val = dora_data[selected_metric_benchmark].iloc[-1]
        display_name = dora_targets[selected_metric_benchmark]["display_name"]

        fig_bench = go.Figure()
        fig_bench.add_trace(go.Bar(
            x=benchmark_df.index,
            y=benchmark_df[selected_metric_benchmark],
            name='Industry Benchmark',
            marker_color='lightblue'
        ))
        fig_bench.add_trace(go.Bar(
            x=['Current Performance'],
            y=[current_val],
            name='Our Performance',
            marker_color='orange'
        ))

        fig_bench.update_layout(
            title=f"{display_name} vs. Industry Benchmarks",
            yaxis_title=display_name,
            xaxis_title="Performance Level"
        )
        st.plotly_chart(fig_bench, use_container_width=True)

        # ML Predictions section
        st.markdown("---")
        st.subheader("📈 Predictive Analytics")
        predictions = predict_future_metrics(dora_data, selected_team)

        col_pred1, col_pred2, col_pred3 = st.columns(3)
        with col_pred1:
            current_lt = dora_data['lead_time_minutes'].iloc[-1]
            predicted_lt = predictions['predicted_lead_time'].iloc[-1]
            improvement = ((current_lt - predicted_lt) / current_lt) * 100
            st.metric("Predicted Lead Time", f"{predicted_lt:.0f} min",
                      f"{improvement:.1f}% improvement", delta_color="inverse")

        with col_pred2:
            current_cfr = dora_data['change_fail_rate'].iloc[-1]
            predicted_cfr = predictions['predicted_fail_rate'].iloc[-1]
            improvement = ((current_cfr - predicted_cfr) / current_cfr) * 100
            st.metric("Predicted Failure Rate", f"{predicted_cfr:.1f}%",
                      f"{improvement:.1f}% improvement", delta_color="inverse")

        with col_pred3:
            current_mttr = dora_data['mttr_minutes'].iloc[-1]
            predicted_mttr = predictions['predicted_mttr'].iloc[-1]
            improvement = ((current_mttr - predicted_mttr) / current_mttr) * 100
            st.metric("Predicted MTTR", f"{predicted_mttr:.0f} min",
                      f"{improvement:.1f}% improvement", delta_color="inverse")

    with tab2:
        if view_mode == "Team View":
            st.subheader(f"Team Performance Comparison")
        else:
            st.subheader("Enterprise Team Performance Overview")

        col1, col2 = st.columns(2)

        with col1:
            # Team radar chart
            categories = ['Lead Time', 'Deployment Freq', 'Failure Rate', 'MTTR', 'Tech Debt']

            fig_radar = go.Figure()

            for _, team in team_df.iterrows():
                fig_radar.add_trace(go.Scatterpolar(
                    r=[team['lead_time_minutes'] / 10,
                       team['deployment_frequency'] / 2,
                       (20 - team['change_fail_rate']) * 5,
                       (60 - team['mttr_minutes'] / 5),
                       (25 - team['tech_debt_ratio']) * 4],
                    theta=categories,
                    fill='toself',
                    name=team['team']
                ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=True,
                title="Team Performance Radar Chart"
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col2:
            # Team scores
            fig_scores = px.bar(team_df, x='team', y='dora_score',
                                title='Team DORA Performance Scores',
                                color='dora_score',
                                color_continuous_scale='Viridis')
            st.plotly_chart(fig_scores, use_container_width=True)

            if view_mode == "Team View":
                # Selected team details
                team_info = team_df[team_df['team'] == selected_team].iloc[0]
                st.subheader(f"Team Details: {selected_team}")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("DORA Score", f"{team_info['dora_score']}/100")
                col2.metric("Lead Time", f"{team_info['lead_time_minutes']} min")
                col3.metric("Deploy Frequency", f"{team_info['deployment_frequency']}/week")
                col4.metric("Failure Rate", f"{team_info['change_fail_rate']:.1f}%")
                st.metric("MTTR", f"{team_info['mttr_minutes']} min")
            else:
                # Enterprise summary
                st.subheader("Enterprise Summary")
                avg_lead_time = team_df['lead_time_minutes'].mean()
                avg_failure_rate = team_df['change_fail_rate'].mean()
                avg_deployment_freq = team_df['deployment_frequency'].mean()

                col1, col2, col3 = st.columns(3)
                col1.metric("Avg Lead Time", f"{avg_lead_time:.0f} min")
                col2.metric("Avg Failure Rate", f"{avg_failure_rate:.1f}%")
                col3.metric("Avg Deployment Freq", f"{avg_deployment_freq:.0f}/week")

    with tab3:
        if view_mode == "Team View":
            st.header(f"🔒 Security & Compliance - {selected_team}")
        else:
            st.header("🔒 Enterprise Security & Compliance")

        col1, col2 = st.columns(2)

        with col1:
            # Vulnerabilities chart
            vuln_data = pd.DataFrame({
                'severity': ['Critical', 'High', 'Medium', 'Low'],
                'count': [security_data['vulnerabilities_critical'],
                          security_data['vulnerabilities_high'],
                          security_data['vulnerabilities_medium'],
                          security_data['vulnerabilities_low']]
            })

            fig_vuln = px.bar(vuln_data, x='severity', y='count',
                              title='Open Vulnerabilities by Severity',
                              color='severity',
                              color_discrete_sequence=['red', 'orange', 'yellow', 'green'])
            st.plotly_chart(fig_vuln, use_container_width=True)

            # Security scores
            st.metric("Secrets Rotation Compliance", f"{security_data['secrets_rotation_compliance']}%")
            st.metric("Vault Usage Rate", f"{security_data['vault_usage_rate']}%")
            st.metric("Pen Test Score", f"{security_data['last_pen_test_score']}/5.0")

        with col2:
            # Compliance status
            st.subheader("Compliance Status")

            compliance_data = pd.DataFrame({
                'standard': ['SOC2', 'ISO27001', 'GDPR', 'HIPAA', 'PCI-DSS'],
                'status': ['Compliant', 'Compliant', 'Compliant', 'In Progress', 'Not Started'],
                'progress': [100, 100, 100, 65, 0]
            })

            for _, row in compliance_data.iterrows():
                st.progress(row['progress'] / 100, text=f"{row['standard']}: {row['status']} ({row['progress']}%)")

            # Security trend
            st.subheader("Security Posture Trend")
            security_trend = pd.DataFrame({
                'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'security_score': [72, 75, 78, 82, 85, 88]
            })

            fig_security = px.line(security_trend, x='month', y='security_score',
                                   title='Security Posture Score Improvement',
                                   markers=True)
            st.plotly_chart(fig_security, use_container_width=True)

    with tab4:
        st.subheader("Cost Optimization & Efficiency")

        col1, col2 = st.columns(2)

        with col1:
            # Cost breakdown
            fig_cost = px.area(cost_data, x='month', y=['infrastructure_cost', 'storage_cost', 'ci_cd_cost'],
                               title='Monthly Cost Breakdown ($)',
                               labels={'value': 'Cost ($)', 'variable': 'Cost Type'})
            st.plotly_chart(fig_cost, use_container_width=True)

            # Efficiency metrics
            st.subheader("Efficiency Gains")
            efficiency_data = pd.DataFrame({
                'metric': ['Build Time', 'Test Execution', 'Deployment Duration', 'Resource Utilization'],
                'before': [45, 28, 22, 45],
                'after': [12, 8, 7, 78],
                'improvement': [73.3, 71.4, 68.2, 73.3]
            })

            for _, row in efficiency_data.iterrows():
                st.metric(f"{row['metric']} Improvement",
                          f"{row['after']} min" if row['metric'] != 'Resource Utilization' else f"{row['after']}%",
                          f"{row['improvement']}% better")

        with col2:
            # ROI calculation
            st.subheader("ROI Calculation")

            savings_data = pd.DataFrame({
                'area': ['Infrastructure', 'Storage', 'Developer Time', 'Incident Reduction'],
                'monthly_savings': [12500, 8500, 45000, 22000],
                'investment': [20000, 5000, 35000, 15000]
            })

            savings_data['roi'] = (savings_data['monthly_savings'] * 12) / savings_data['investment']

            fig_roi = px.bar(savings_data, x='area', y='roi',
                             title='Return on Investment (Annualized)',
                             labels={'roi': 'ROI Multiple', 'area': 'Investment Area'})
            st.plotly_chart(fig_roi, use_container_width=True)

            total_savings = savings_data['monthly_savings'].sum()
            total_investment = savings_data['investment'].sum()
            overall_roi = (total_savings * 12) / total_investment

            st.metric("Total Estimated Monthly Savings", f"${total_savings:,.0f}")
            st.metric("Total Investment", f"${total_investment:,.0f}")
            st.metric("Annualized ROI", f"{overall_roi:.1f}x")

            # Enhanced ROI simulation (from provided project)
            st.markdown("---")
            st.subheader("ROI Simulation")
            st.markdown("Use the sliders to see how improvements translate to cost savings.")

            incidents_per_month = st.slider("Number of Production Incidents per month", 5, 50, 20)
            cost_per_incident = st.slider("Avg. Cost per Incident (person-hours)", 4, 40, 16)
            improvement_percentage = st.slider("Expected Improvement (%)", 10, 60, 33)

            current_cost = incidents_per_month * cost_per_incident * 150  # $150/hour fully loaded cost
            projected_cost = (incidents_per_month * (1 - improvement_percentage / 100)) * cost_per_incident * 150
            savings = current_cost - projected_cost

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Monthly Cost", f"${current_cost:,.0f}")
            with col2:
                st.metric("Projected Monthly Cost", f"${projected_cost:,.0f}")
            with col3:
                st.metric("Projected Monthly Savings", f"${savings:,.0f}",
                          f"{improvement_percentage}% improvement")

            st.caption("Assumes a fully loaded cost of $150 per person-hour.")

    with tab5:
        st.subheader("Transformation Roadmap & Progress")

        # Show appropriate roadmap based on view mode
        if view_mode == "Team View":
            st.markdown(f"### Team-Specific Roadmap for {selected_team}")
        else:
            st.markdown("### Enterprise Transformation Roadmap")

        # Transformation phases
        for phase in roadmap_phases:
            status_icon = "✅" if phase['status'] == 'Completed' else "🟡" if phase['status'] == 'In Progress' else "⚪"
            priority_icon = "🔴" if phase['priority'] == 'High' else "🟡" if phase['priority'] == 'Medium' else "🟢"
            st.write(f"{status_icon} {priority_icon} **{phase['phase']}** ({phase['status']})")
            st.progress(phase['progress'] / 100,
                        text=f"{phase['start']} to {phase['end']} - {phase['progress']}% complete")
            st.caption(f"Dependencies: {phase['dependencies']}")

        # Key initiatives status
        st.subheader("Key Initiatives Status")

        for initiative in roadmap_initiatives:
            status_icon = {'Completed': '✅', 'In Progress': '🟡', 'Planned': '📅', 'Backlog': '📋'}[initiative['status']]
            impact_icon = {'High': '🔥', 'Medium': '⚠️', 'Low': '🔹'}[initiative['impact']]
            team_label = f"({initiative['team']})" if 'team' in initiative else ""
            st.write(f"{status_icon} {impact_icon} {initiative['initiative']} {team_label}")

    with tab6:
        st.header("🤖 AI Transformation Roadmap")
        st.markdown("### From Traditional DevOps to AI-Driven Excellence")

        # Make AI tab context-aware based on team selection
        if view_mode == "Team View" and selected_team:
            ai_readiness_score = team_df[team_df['team'] == selected_team]['ai_readiness_score'].iloc[0]
            cloud_maturity = team_df[team_df['team'] == selected_team]['cloud_maturity'].iloc[0]
            automation_level = team_df[team_df['team'] == selected_team]['automation_level'].iloc[0]

            if selected_team == 'Team Alpha':
                st.success("🚀 AI Leader: This team is ready for advanced AI implementation")
                ai_readiness = "High"
                recommended_ai_phases = ["Q3 2024", "Q4 2024", "Q1 2025", "Q2 2025"]
                progress_levels = [100, 65, 20, 0]
                ai_use_cases = [
                    {'name': 'Predictive Test Selection', 'priority': 'High', 'status': 'In Progress',
                     'impact': 'Reduces test time by 70%', 'timeline': 'Q3 2024'},
                    {'name': 'Anomaly Detection', 'priority': 'High', 'status': 'Completed',
                     'impact': 'Early warning for incidents', 'timeline': 'Q2 2024'},
                    {'name': 'Intelligent Root Cause', 'priority': 'Medium', 'status': 'Planned',
                     'impact': 'Reduces MTTR by 50%', 'timeline': 'Q4 2024'},
                    {'name': 'Risk-Based Deployment', 'priority': 'Medium', 'status': 'Planned',
                     'impact': 'Auto-approves safe changes', 'timeline': 'Q1 2025'},
                    {'name': 'Cost Optimization AI', 'priority': 'Low', 'status': 'Backlog',
                     'impact': 'Saves 25% on cloud spend', 'timeline': 'Q2 2025'}
                ]
            elif selected_team == 'Team Beta':
                st.warning("⚠️ AI Novice: This team needs foundational work first")
                ai_readiness = "Low"
                recommended_ai_phases = ["Q1 2025", 'Q2 2025', 'Q3 2025', 'Q4 2025']
                progress_levels = [30, 0, 0, 0]
                ai_use_cases = [
                    {'name': 'Basic Test Automation', 'priority': 'High', 'status': 'In Progress',
                     'impact': 'Reduces manual testing', 'timeline': 'Q4 2024'},
                    {'name': 'Log Analysis', 'priority': 'Medium', 'status': 'Planned',
                     'impact': 'Faster issue identification', 'timeline': 'Q1 2025'},
                    {'name': 'Deployment Automation', 'priority': 'High', 'status': 'Not Started',
                     'impact': 'Reduces deployment errors', 'timeline': 'Q2 2025'}
                ]
            else:
                st.info("📊 AI Intermediate: This team can begin with basic AI features")
                ai_readiness = "Medium"
                recommended_ai_phases = ["Q4 2024", 'Q1 2025', 'Q2 2025', 'Q3 2025']
                progress_levels = [75, 15, 0, 0]
                ai_use_cases = [
                    {'name': 'Test Optimization', 'priority': 'High', 'status': 'In Progress',
                     'impact': 'Reduces test time by 50%', 'timeline': 'Q3 2024'},
                    {'name': 'Basic Anomaly Detection', 'priority': 'Medium', 'status': 'Planned',
                     'impact': 'Early warning system', 'timeline': 'Q4 2024'},
                    {'name': 'Performance Prediction', 'priority': 'Medium', 'status': 'Backlog',
                     'impact': 'Forecasts system behavior', 'timeline': 'Q1 2025'}
                ]

            st.metric("AI Readiness Score", f"{ai_readiness_score}/100", ai_readiness)
            st.metric("Cloud Maturity", f"{cloud_maturity}/100")
            st.metric("Automation Level", f"{automation_level}/100")
        else:
            st.info("🏢 Enterprise AI Transformation Overview")
            ai_readiness = "Variable"
            recommended_ai_phases = ["Q4 2024", 'Q1 2025', 'Q2 2025', 'Q3 2025']
            progress_levels = [60, 25, 5, 0]

            # Calculate enterprise averages
            avg_ai_readiness = team_df['ai_readiness_score'].mean()
            avg_cloud_maturity = team_df['cloud_maturity'].mean()
            avg_automation = team_df['automation_level'].mean()

            st.metric("Avg AI Readiness Score", f"{avg_ai_readiness:.0f}/100")
            st.metric("Avg Cloud Maturity", f"{avg_cloud_maturity:.0f}/100")
            st.metric("Avg Automation Level", f"{avg_automation:.0f}/100")

            ai_use_cases = [
                {'name': 'Enterprise AI Platform', 'priority': 'High', 'status': 'In Progress',
                 'impact': 'Standardized AI tools', 'timeline': 'Q4 2024'},
                {'name': 'Cross-Team Knowledge Sharing', 'priority': 'High', 'status': 'Planned',
                 'impact': 'Accelerates AI adoption', 'timeline': 'Q1 2025'},
                {'name': 'AI Governance Framework', 'priority': 'Medium', 'status': 'Planned',
                 'impact': 'Ensures responsible AI use', 'timeline': 'Q2 2025'}
            ]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔄 Traditional vs AI-Driven DevOps")

            comparison_data = pd.DataFrame({
                'Capability': ['Incident Response', 'Testing', 'Deployment', 'Capacity Planning', 'Cost Optimization'],
                'Traditional': [30, 40, 50, 45, 35],
                'AI_Enhanced': [85, 90, 95, 88, 92]
            })

            fig_comparison = go.Figure()
            fig_comparison.add_trace(go.Bar(
                name='Traditional',
                y=comparison_data['Capability'],
                x=comparison_data['Traditional'],
                orientation='h',
                marker_color='#636EFA'
            ))
            fig_comparison.add_trace(go.Bar(
                name='AI-Enhanced',
                y=comparison_data['Capability'],
                x=comparison_data['AI_Enhanced'],
                orientation='h',
                marker_color='#00CC96'
            ))
            fig_comparison.update_layout(barmode='group', title='Capability Maturity: Traditional vs AI-Enhanced')
            st.plotly_chart(fig_comparison, use_container_width=True)

            # AI Adoption Timeline
            st.subheader("📅 AI Adoption Timeline")
            ai_timeline = pd.DataFrame({
                'Phase': ['Foundation', 'Augmented Intelligence', 'Predictive Operations', 'Autonomous Operations'],
                'Start': recommended_ai_phases,
                'End': [f"Q{int(p.split(' ')[0][1]) + 1} {p.split(' ')[1]}" for p in recommended_ai_phases],
                'Progress': progress_levels
            })

            for _, row in ai_timeline.iterrows():
                st.write(f"**{row['Phase']}** ({row['Start']} - {row['End']})")
                st.progress(row['Progress'] / 100)

        with col2:
            st.subheader("📈 Expected AI Impact")

            impact_metrics = pd.DataFrame({
                'Metric': ['Lead Time Reduction', 'Incident Reduction', 'Test Time Savings', 'Cost Optimization',
                           'Team Productivity'],
                'Expected_Improvement': [35, 60, 75, 40, 30],
                'Timeframe': ['6 months', '12 months', '9 months', '12 months', '18 months']
            })

            fig_impact = px.bar(impact_metrics, y='Metric', x='Expected_Improvement',
                                orientation='h', title='Expected AI Impact (%)',
                                color='Expected_Improvement', color_continuous_scale='Viridis')
            st.plotly_chart(fig_impact, use_container_width=True)

            # AI Use Cases
            st.subheader("🎯 Priority AI Use Cases")

            for case in ai_use_cases:
                priority_color = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}[case['priority']]
                status_icon = {'Completed': '✅', 'In Progress': '🟡', 'Planned': '📅',
                               'Backlog': '📋', 'Not Started': '⚪'}[case['status']]
                st.write(f"{priority_color} {status_icon} **{case['name']}** - {case['impact']} ({case['timeline']})")

            # AI Simulation Features (from provided project)
            st.markdown("---")
            st.subheader("AI Impact Simulation")

            if st.button("Simulate AI-Powered Test Optimization"):
                with st.spinner("Analyzing test patterns and coverage..."):
                    time.sleep(1.5)
                    st.success("**Results:** AI would reduce test execution time by 65%")
                    st.info("""
                    - Identified 42% of tests as redundant or low-value
                    - Recommended parallelization strategy for remaining tests
                    - Estimated time savings: 45 minutes per pipeline run
                    """)

            if st.button("Simulate Predictive Failure Analysis"):
                with st.spinner("Analyzing historical failure patterns..."):
                    time.sleep(1.5)
                    st.warning("**Prediction:** High risk of deployment failure (78% confidence)")
                    st.info("""
                    - Pattern detected: Similar code changes caused failures 3 times in past 2 months
                    - Recommended: Additional testing on database migration components
                    - Suggested: Run targeted integration tests before full deployment
                    """)

    with tab7:
        st.header("📊 DevOps & DevSecOps Maturity Journey")
        st.markdown("### Current State vs Target State Transformation")

        # Make maturity context-aware
        if view_mode == "Team View" and selected_team:
            team_info = team_df[team_df['team'] == selected_team].iloc[0]
            current_devops = team_info['dora_score']
            current_devsecops = int(team_info['dora_score'] * 0.85)
            target_devops = min(100, current_devops + 20)
            target_devsecops = min(100, current_devsecops + 18)

            st.subheader(f"Maturity Assessment for {selected_team}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current DevOps", f"{current_devops}/100")
            with col2:
                st.metric("Target DevOps", f"{target_devops}/100")
            with col3:
                st.metric("Current DevSecOps", f"{current_devsecops}/100")
            with col4:
                st.metric("Target DevSecOps", f"{target_devsecops}/100")
        else:
            # Use enterprise view
            current_devops = enterprise_maturity['current_devops']
            current_devsecops = enterprise_maturity['current_devsecops']
            target_devops = enterprise_maturity['target_devops']
            target_devsecops = enterprise_maturity['target_devsecops']

            st.subheader("Enterprise Maturity Assessment")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current DevOps", f"{current_devops}/100")
            with col2:
                st.metric("Target DevOps", f"{target_devops}/100")
            with col3:
                st.metric("Current DevSecOps", f"{current_devsecops}/100")
            with col4:
                st.metric("Target DevSecOps", f"{target_devsecops}/100")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏢 Maturity Assessment by Category")

            categories = ['Culture & Process', 'Automation', 'Measurement', 'Sharing', 'Security Integration']

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=[65, 70, 60, 75, 62],
                theta=categories,
                fill='toself',
                name='Current State'
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=[85, 90, 80, 85, 80],
                theta=categories,
                fill='toself',
                name='Target State'
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            # Maturity Timeline
            st.subheader("🕒 Maturity Evolution Timeline")

            maturity_evolution = pd.DataFrame({
                'Year': ['2022', '2023', '2024', '2025', '2026'],
                'DevOps_Maturity': [45, 58, current_devops, 78, target_devops],
                'DevSecOps_Maturity': [35, 48, current_devsecops, 72, target_devsecops]
            })

            fig_evolution = px.line(maturity_evolution, x='Year', y=['DevOps_Maturity', 'DevSecOps_Maturity'],
                                    title='Maturity Evolution Over Time', markers=True,
                                    labels={'value': 'Maturity Score', 'variable': 'Maturity Type'})
            st.plotly_chart(fig_evolution, use_container_width=True)

        with col2:
            st.subheader("🎯 Maturity Gap Analysis")

            gap_data = pd.DataFrame({
                'Dimension': ['Process & Culture', 'Tooling & Automation', 'Measurement & Metrics',
                              'Collaboration & Sharing', 'Security & Compliance'],
                'Current_Score': [65, 70, 60, 75, 62],
                'Target_Score': [85, 90, 80, 85, 80],
                'Gap': [20, 20, 20, 10, 18]
            })

            gap_data['Improvement_Needed'] = gap_data['Gap'] / gap_data['Target_Score'] * 100

            fig_gap = px.bar(gap_data, x='Gap', y='Dimension', orientation='h',
                             title='Maturity Gap by Dimension', color='Gap',
                             color_continuous_scale='Reds')
            st.plotly_chart(fig_gap, use_container_width=True)

            # Team Maturity Distribution
            st.subheader("👥 Team Maturity Distribution")

            fig_team = px.scatter(team_df, x='dora_score', y='ai_readiness_score',
                                  color='team', size='dora_score',
                                  title='Team Maturity vs AI Readiness', hover_data=['team'])
            st.plotly_chart(fig_team, use_container_width=True)

            # Recommendations
            st.subheader("💡 Recommended Focus Areas")
            recommendations = [
                {"area": "Test Optimization", "effort": "High", "impact": "High", "timeline": "Q3 2024"},
                {"area": "Security Automation", "effort": "Medium", "impact": "High", "timeline": "Q4 2024"},
                {"area": "AI-Powered Monitoring", "effort": "High", "impact": "Medium", 'timeline': 'Q1 2025'},
                {"area": "Cost Governance", "effort": "Medium", "impact": "Medium", 'timeline': 'Q2 2025'}
            ]

            for rec in recommendations:
                effort_icon = "🔴" if rec["effort"] == "High" else "🟡" if rec["effort"] == "Medium" else "🟢"
                impact_icon = "🔥" if rec["impact"] == "High" else "⚠️" if rec["impact"] == "Medium" else "🔹"
                st.write(f"{effort_icon}{impact_icon} **{rec['area']}** - {rec['timeline']}")

    with tab8:
        st.header("🛠️ Tooling Maturity Assessment")
        st.markdown("### Current Tooling State vs Target Automation")

        if view_mode == "Team View":
            st.subheader(f"Tooling Maturity for {selected_team}")
        else:
            st.subheader("Enterprise Tooling Maturity Overview")

        col1, col2 = st.columns(2)

        with col1:
            # Tooling maturity radar chart
            categories = ['CI/CD', 'Release Mgmt', 'Database', 'Testing', 'Monitoring']

            fig_tooling = go.Figure()

            if view_mode == "Team View":
                # Single team view
                fig_tooling.add_trace(go.Scatterpolar(
                    r=[tooling_data['ci_cd_maturity'],
                       tooling_data['release_maturity'],
                       tooling_data['database_maturity'],
                       tooling_data['testing_maturity'],
                       tooling_data['monitoring_maturity']],
                    theta=categories,
                    fill='toself',
                    name=selected_team
                ))
            else:
                # Enterprise view - show all teams
                teams = ['Team Alpha', 'Team Beta', 'Team Gamma', 'Team Delta', 'Team Epsilon']
                for team in teams:
                    team_tooling, _, _ = generate_tooling_maturity_data(team)
                    fig_tooling.add_trace(go.Scatterpolar(
                        r=[team_tooling['ci_cd_maturity'],
                           team_tooling['release_maturity'],
                           team_tooling['database_maturity'],
                           team_tooling['testing_maturity'],
                           team_tooling['monitoring_maturity']],
                        theta=categories,
                        fill='toself',
                        name=team
                    ))

            fig_tooling.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title="Tooling Maturity by Category"
            )
            st.plotly_chart(fig_tooling, use_container_width=True)

            # Tool adoption status
            st.subheader("🔄 Tool Adoption Status")
            adoption_df = pd.DataFrame(adoption_data)

            # Create a color map for status
            status_colors = {
                'Partial': 'orange',
                'Not Onboarded': 'red',
                'Manual Ansible': 'red',
                'Not Implemented': 'red',
                'Basic': 'orange',
                'Advanced': 'green',
                'Fully Automated': 'green'
            }

            fig_adoption = px.bar(adoption_df, x='tool', y='automation', color='status',
                                  color_discrete_map=status_colors,
                                  title='Tool Automation Level (%)',
                                  labels={'automation': 'Automation Level %', 'tool': 'Tool'})
            st.plotly_chart(fig_adoption, use_container_width=True)

        with col2:
            # Tooling metrics
            st.subheader("📊 Tooling Metrics")

            if view_mode == "Team View":
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("CI/CD Maturity", f"{tooling_data['ci_cd_maturity']}/100")
                    st.metric("Release Maturity", f"{tooling_data['release_maturity']}/100")
                    st.metric("Database Maturity", f"{tooling_data['database_maturity']}/100")
                with col2:
                    st.metric("Testing Maturity", f"{tooling_data['testing_maturity']}/100")
                    st.metric("Monitoring Maturity", f"{tooling_data['monitoring_maturity']}/100")
                    st.metric("Overall Automation", f"{tooling_data['automation_level']}/100")
            else:
                # Calculate enterprise averages
                teams = ['Team Alpha', 'Team Beta', 'Team Gamma', 'Team Delta', 'Team Epsilon']
                tooling_scores = {
                    'ci_cd': [], 'release': [], 'database': [], 'testing': [], 'monitoring': [], 'automation': []
                }

                for team in teams:
                    team_tooling, _, _ = generate_tooling_maturity_data(team)
                    tooling_scores['ci_cd'].append(team_tooling['ci_cd_maturity'])
                    tooling_scores['release'].append(team_tooling['release_maturity'])
                    tooling_scores['database'].append(team_tooling['database_maturity'])
                    tooling_scores['testing'].append(team_tooling['testing_maturity'])
                    tooling_scores['monitoring'].append(team_tooling['monitoring_maturity'])
                    tooling_scores['automation'].append(team_tooling['automation_level'])

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Avg CI/CD Maturity", f"{np.mean(tooling_scores['ci_cd']):.0f}/100")
                    st.metric("Avg Release Maturity", f"{np.mean(tooling_scores['release']):.0f}/100")
                    st.metric("Avg Database Maturity", f"{np.mean(tooling_scores['database']):.0f}/100")
                with col2:
                    st.metric("Avg Testing Maturity", f"{np.mean(tooling_scores['testing']):.0f}/100")
                    st.metric("Avg Monitoring Maturity", f"{np.mean(tooling_scores['monitoring']):.0f}/100")
                    st.metric("Avg Automation Level", f"{np.mean(tooling_scores['automation']):.0f}/100")

            # Tooling roadmap
            st.subheader("🛣️ Tooling Improvement Roadmap")

            for initiative in tooling_roadmap:
                priority_icon = "🔴" if initiative['priority'] == 'High' else "🟡" if initiative[
                                                                                        'priority'] == 'Medium' else "🟢"
                st.write(f"{priority_icon} **{initiative['initiative']}** - {initiative['timeline']}")

            # Key gaps and recommendations
            st.subheader("💡 Key Gaps & Recommendations")

            gaps = [
                {"gap": "XLR Not Onboarded", "impact": "High", "recommendation": "Plan XLR implementation in Q3 2024"},
                {"gap": "Manual Database Deployments", "impact": "High",
                 "recommendation": "Evaluate Datical for database automation"},
                {"gap": "No Test Automation Framework", "impact": "Medium",
                 "recommendation": "Select and implement test automation framework"},
                {"gap": "Partial CI/CD Automation", "impact": "Medium",
                 "recommendation": "Complete pipeline-as-code implementation"}
            ]

            for gap in gaps:
                impact_icon = "🔥" if gap["impact"] == "High" else "⚠️" if gap["impact"] == "Medium" else "🔹"
                st.write(f"{impact_icon} **{gap['gap']}**: {gap['recommendation']}")

    # NEW: Q&A for Management Tab
    with tab9:
        st.header("❓ Q&A for Management")
        st.markdown("### Explaining Dashboard Metrics to Leadership")

        # Tab selection for different dashboard sections
        qa_tab = st.selectbox(
            "Select Dashboard Section to Explain:",
            list(qa_data.keys())
        )

        st.subheader(qa_tab)
        st.info(qa_data[qa_tab]["description"])

        # Display questions and answers
        for i, qa in enumerate(qa_data[qa_tab]["questions"]):
            with st.expander(f"Q: {qa['question']}"):
                st.write(f"**A:** {qa['answer']}")

        # Additional management insights
        st.subheader("📋 Executive Summary")

        if view_mode == "Team View":
            team_info = team_df[team_df['team'] == selected_team].iloc[0]

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Team Performance Score", f"{team_info['dora_score']}/100",
                          "Elite" if team_info['dora_score'] > 80 else
                          "High" if team_info['dora_score'] > 65 else
                          "Medium" if team_info['dora_score'] > 50 else "Low")

                st.metric("AI Readiness", f"{team_info['ai_readiness_score']}/100",
                          "Ready" if team_info['ai_readiness_score'] > 70 else
                          "Getting There" if team_info['ai_readiness_score'] > 50 else "Needs Work")

            with col2:
                st.metric("Automation Level", f"{team_info['automation_level']}/100")
                st.metric("Cloud Maturity", f"{team_info['cloud_maturity']}/100")

            # Performance summary
            st.subheader("🎯 Performance Insights")
            if team_info['dora_score'] > 80:
                st.success(
                    "This team is performing at an elite level. Focus on maintaining excellence and sharing best practices with other teams.")
            elif team_info['dora_score'] > 65:
                st.info("This team is performing well. Identify specific areas for improvement to reach elite status.")
            else:
                st.warning(
                    "This team needs focused improvement. Consider additional resources, training, or process changes.")

        else:
            # Enterprise view
            avg_dora = team_df['dora_score'].mean()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Enterprise Performance", f"{avg_dora:.0f}/100",
                          "Elite" if avg_dora > 80 else
                          "High" if avg_dora > 65 else
                          "Medium" if avg_dora > 50 else "Low")

                avg_ai = team_df['ai_readiness_score'].mean()
                st.metric("Avg AI Readiness", f"{avg_ai:.0f}/100")

            with col2:
                avg_auto = team_df['automation_level'].mean()
                st.metric("Avg Automation", f"{avg_auto:.0f}/100")

                avg_cloud = team_df['cloud_maturity'].mean()
                st.metric("Avg Cloud Maturity", f"{avg_cloud:.0f}/100")

            # Performance distribution
            st.subheader("📊 Performance Distribution")
            perf_bins = [0, 50, 65, 80, 100]
            perf_labels = ["Low", "Medium", "High", "Elite"]
            team_df['perf_category'] = pd.cut(team_df['dora_score'], bins=perf_bins, labels=perf_labels)
            perf_dist = team_df['perf_category'].value_counts().reindex(perf_labels, fill_value=0)

            fig_perf = px.bar(x=perf_dist.index, y=perf_dist.values,
                              title="Team Performance Distribution",
                              labels={'x': 'Performance Level', 'y': 'Number of Teams'})
            st.plotly_chart(fig_perf, use_container_width=True)

            # Recommendations
            st.subheader("💡 Leadership Recommendations")
            if avg_dora > 80:
                st.success(
                    "The organization is performing at an elite level. Focus on innovation and maintaining competitive advantage.")
            elif avg_dora > 65:
                st.info(
                    "The organization is performing well. Identify and address gaps in lower-performing teams to raise overall performance.")
            else:
                st.warning(
                    "The organization needs improvement. Prioritize foundational DevOps practices and consider organizational changes.")

    # NEW: DevOps Quiz Tab
    with tab10:
        st.header("🧠 DevOps Knowledge Quiz")
        st.markdown("### Test Your DevOps Knowledge")

        # Initialize quiz state
        if 'quiz_submitted' not in st.session_state:
            st.session_state.quiz_submitted = False

        # Display quiz questions
        score = 0
        total_questions = len(quiz_data)

        for i, question_data in enumerate(quiz_data):
            st.subheader(f"Question {i + 1}")
            st.write(question_data["question"])

            # Display options
            options = question_data["options"]
            selected_option = st.radio(
                "Select your answer:",
                options,
                key=f"q_{i}",
                index=None
            )

            # Show explanation if quiz is submitted
            if st.session_state.quiz_submitted:
                correct_answer = options[question_data["correct_answer"]]
                if selected_option == correct_answer:
                    st.success(f"✅ Correct! {question_data['explanation']}")
                    score += 1
                else:
                    st.error(f"❌ Incorrect. The correct answer is: {correct_answer}")
                    st.info(f"Explanation: {question_data['explanation']}")

            st.divider()

        # Submit button
        if not st.session_state.quiz_submitted:
            if st.button("Submit Quiz"):
                st.session_state.quiz_submitted = True
                st.session_state.quiz_score = score
                st.rerun()
        else:
            # Display score
            st.subheader("Quiz Results")
            st.metric("Your Score", f"{score}/{total_questions}",
                      f"{score / total_questions * 100:.1f}%")

            # Performance assessment
            if score == total_questions:
                st.success("🎉 Perfect score! You're a DevOps expert!")
            elif score >= total_questions * 0.7:
                st.info("👍 Good job! You have solid DevOps knowledge.")
            else:
                st.warning("📚 Keep learning! Review the explanations and try again.")

            # Try again button
            if st.button("Try Again"):
                st.session_state.quiz_submitted = False
                st.rerun()

    # NEW: Team Socialize Tab
    with tab11:
        st.header("💬 Team Collaboration Space")
        st.markdown("### Share Ideas, Best Practices, and Feedback")

        # Team selection for messaging
        teams = ['Team Alpha', 'Team Beta', 'Team Gamma', 'Team Delta', 'Team Epsilon', 'All Teams']
        selected_channel = st.selectbox("Select channel:", teams)

        # Message input
        message = st.text_input("Your message:")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Send Message"):
                if message:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.session_state.messages.append({
                        "team": selected_team,
                        "channel": selected_channel,
                        "message": message,
                        "timestamp": timestamp
                    })
                    st.success("Message sent!")

        with col2:
            if st.button("Clear Chat"):
                st.session_state.messages = []
                st.info("Chat cleared!")

        # Display messages
        st.subheader("💭 Messages")

        if not st.session_state.messages:
            st.info("No messages yet. Start the conversation!")
        else:
            # Filter messages by selected channel
            filtered_messages = [
                msg for msg in st.session_state.messages
                if
                msg["channel"] == selected_channel or msg["channel"] == "All Teams" or selected_channel == "All Teams"
            ]

            for msg in filtered_messages:
                with st.chat_message("user"):
                    st.write(f"**{msg['team']}** ({msg['timestamp']}):")
                    st.write(msg["message"])

        # Best practices sharing
        st.subheader("🌟 Share Best Practices")

        practice_type = st.selectbox("Practice type:",
                                     ["CI/CD", "Testing", "Security", "Monitoring", "Automation", "Other"])

        practice_title = st.text_input("Title:")
        practice_description = st.text_area("Description:")

        if st.button("Share Practice"):
            if practice_title and practice_description:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.messages.append({
                    "team": selected_team,
                    "channel": "Best Practices",
                    "message": f"**{practice_type}**: {practice_title} - {practice_description}",
                    "timestamp": timestamp
                })
                st.success("Best practice shared!")

        # Feedback section
        st.subheader("📝 Provide Feedback")

        feedback_type = st.selectbox("Feedback type:",
                                     ["Bug Report", "Feature Request", "General Feedback", "Kudos"])

        feedback = st.text_area("Your feedback:")

        if st.button("Submit Feedback"):
            if feedback:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.messages.append({
                    "team": selected_team,
                    "channel": "Feedback",
                    "message": f"**{feedback_type}**: {feedback}",
                    "timestamp": timestamp
                })
                st.success("Feedback submitted! Thank you.")


# Run the dashboard
if __name__ == "__main__":
    main()