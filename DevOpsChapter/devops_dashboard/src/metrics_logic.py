import pandas as pd
import numpy as np
import random

def generate_demo_data():
    """Generates a DataFrame with simulated DevOps metrics over 12 months for multiple teams."""
    teams = ['Enterprise', 'Team Alpha', 'Team Beta', 'Team Gamma']
    df_list = []

    for team in teams:
        dates = pd.date_range(start='2024-01-01', periods=12, freq='M')

        if team == 'Enterprise':
            deploys_per_day = np.linspace(10, 18, 12) + np.random.normal(0, 1.5, 12)
            lead_time_hours = np.linspace(50, 20, 12) + np.random.normal(0, 5, 12)
            change_failure_rate = np.linspace(0.20, 0.12, 12) + np.random.normal(0, 0.02, 12)
            time_to_restore_hours = np.linspace(10, 3, 12) + np.random.normal(0, 1, 12)
        else:
            deploys_per_day = np.linspace(9, 17, 12) + np.random.normal(0, 1, 12) + (random.uniform(-2, 2))
            lead_time_hours = np.linspace(55, 25, 12) + np.random.normal(0, 4, 12) + (random.uniform(-5, 5))
            change_failure_rate = np.linspace(0.25, 0.15, 12) + np.random.normal(0, 0.03, 12) + (random.uniform(-0.02, 0.02))
            time_to_restore_hours = np.linspace(12, 4, 12) + np.random.normal(0, 1.5, 12) + (random.uniform(-2, 2))

        data = {
            'Date': dates,
            'Team': team,
            'Deployment Frequency': np.maximum(5, deploys_per_day).round(1),
            'Lead Time (Hours)': np.maximum(15, lead_time_hours).round(1),
            'Change Failure Rate (%)': np.clip(change_failure_rate, 0.1, 0.25).round(3) * 100,
            'Time to Restore (Hours)': np.maximum(2, time_to_restore_hours).round(1)
        }
        df_list.append(pd.DataFrame(data))

    return pd.concat(df_list).set_index('Date')

def get_dora_targets():
    """Returns the DORA metrics target configuration."""
    return {
        "Deployment Frequency": {"goal": 20, "unit": "/ day", "class": "positive"},
        "Lead Time (Hours)": {"goal": 8, "unit": " hrs", "class": "negative", "initial": 50},
        "Change Failure Rate (%)": {"goal": 10, "unit": "%", "class": "negative", "initial": 20},
        "Time to Restore (Hours)": {"goal": 1, "unit": " hrs", "class": "negative", "initial": 10}
    }

def get_maturity_scores():
    """Returns the maturity scores for different teams."""
    return {
        'Enterprise': {'Current': [2.5, 2.0, 3.5, 3.0, 4.0], 'Target': [4.5, 4.0, 5.0, 5.0, 5.0]},
        'Team Alpha': {'Current': [3.5, 2.5, 4.0, 4.0, 4.5], 'Target': [5.0, 4.5, 5.0, 5.0, 5.0]},
        'Team Beta': {'Current': [2.0, 1.5, 3.0, 2.5, 3.5], 'Target': [4.0, 3.5, 4.5, 4.5, 4.5]},
        'Team Gamma': {'Current': [1.5, 1.0, 2.5, 2.0, 3.0], 'Target': [4.0, 3.0, 4.0, 3.5, 4.0]}
    }
