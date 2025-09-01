import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data_loader import DevOpsDataLoader
from metrics_logic import get_dora_targets, get_maturity_scores

# --- Page Configuration ---
st.set_page_config(
    page_title="DevOps Strategic Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading (using the provisioned data_loader) ---
loader = DevOpsDataLoader()
df_metrics_raw = loader.load_data()

# --- Main Title and Sidebar ---
st.title("DevOps Chapter: Strategic Goals & Transformation")
st.sidebar.header("Dashboard Controls")
selected_team = st.sidebar.selectbox("Select a Team:", ['Enterprise', 'Team Alpha', 'Team Beta', 'Team Gamma'])

df_filtered = df_metrics_raw[df_metrics_raw['Team'] == selected_team]

# --- Main Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard & Metrics", "Maturity & Benchmarks", "Business Value & ROI", "AI/ML & The Future"])

# --- Tab 1: Dashboard & Metrics ---
with tab1:
    st.header("Strategic Overview")
    st.markdown("This dashboard translates your **current performance into a tangible journey** towards your strategic goals.")

    st.subheader(f"DORA Metrics for **{selected_team}**")
    cols = st.columns(4)
    dora_targets = get_dora_targets()
    for i, (metric, data) in enumerate(dora_targets.items()):
        current_val = df_filtered[metric].iloc[-1]
        goal = data["goal"]
        unit = data["unit"]

        with cols[i]:
            st.metric(label=f"Current {metric}", value=f"{current_val}{unit}", delta=f"{goal}{unit} Target")

            if data["class"] == "positive":
                progress_val = np.clip(current_val / goal, 0, 1.0)
            else:
                initial_val = data["initial"]
                progress_val = np.clip((initial_val - current_val) / (initial_val - goal), 0, 1.0)

            st.progress(float(progress_val))

    st.markdown("---")
    st.subheader("Performance Trends Over Time")

    metric_choice = st.radio(
        "Select a metric to visualize:",
        ("Deployment Frequency", "Lead Time (Hours)", "Change Failure Rate (%)", "Time to Restore (Hours)"),
        horizontal=True
    )

    fig = px.line(df_filtered, x=df_filtered.index, y=metric_choice, markers=True,
                  title=f"{metric_choice} Trend for {selected_team}",
                  labels={'y': metric_choice, 'x': 'Date'})

    target_value = dora_targets[metric_choice]['goal']
    fig.add_hline(y=target_value, line_dash="dash", line_color="red", annotation_text="Target", annotation_position="bottom right")

    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Maturity & Benchmarks ---
with tab2:
    st.header("Maturity Assessment & Benchmarks")
    st.markdown("We're moving from a legacy pipeline to a fully-matured, modern DevOps Chapter. Our progress is measured against industry benchmarks.")

    st.subheader("Maturity Index")
    maturity_scores = get_maturity_scores()
    maturity_data = maturity_scores[selected_team]
    maturity_pillars = list(maturity_scores['Enterprise']['Current'])

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=maturity_data['Current'],
        theta=maturity_pillars,
        fill='toself',
        name='Current Maturity'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=maturity_data['Target'],
        theta=maturity_pillars,
        fill='toself',
        name='Target Maturity'
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        showlegend=True,
        title=f'Maturity Index for {selected_team}'
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.info("The maturity index is a score from 1 (Initial) to 5 (Optimizing) across key pillars.")

    st.markdown("---")
    st.subheader("DORA Metric Benchmarks")

    benchmark_data = {
        'Category': ['Elite', 'High', 'Medium', 'Low'],
        'Deployment Frequency': [24, 7, 1, 0.25],
        'Lead Time (Hours)': [1, 24, 168, 720],
        'Change Failure Rate (%)': [15, 15, 30, 60],
        'Time to Restore (Hours)': [1, 24, 168, 720]
    }
    benchmark_df = pd.DataFrame(benchmark_data).set_index('Category')

    selected_metric_benchmark = st.radio(
        "Compare a metric to industry benchmarks:",
        ("Deployment Frequency", "Lead Time (Hours)", "Change Failure Rate (%)", "Time to Restore (Hours)"),
        horizontal=True
    )

    current_val_for_benchmark = df_filtered[selected_metric_benchmark].iloc[-1]

    fig_bench = go.Figure()
    fig_bench.add_trace(go.Bar(
        x=benchmark_df.index,
        y=benchmark_df[selected_metric_benchmark],
        name='Industry Benchmark'
    ))
    fig_bench.add_trace(go.Bar(
        x=[f'Our Current\n({selected_team})'],
        y=[current_val_for_benchmark],
        name='Our Performance'
    ))

    fig_bench.update_layout(
        title=f"Our {selected_metric_benchmark} vs. Industry",
        yaxis_title=f"Value ({selected_metric_benchmark})",
        xaxis_title="Benchmark Level"
    )
    st.plotly_chart(fig_bench, use_container_width=True)

# --- Tab 3: Business Value & ROI ---
with tab3:
    st.header("From Traditional to Business Value")
    st.markdown("The most impactful part of our transformation is not just the numbers, but the **return on investment** for the business.")

    col_before, col_after = st.columns(2)
    with col_before:
        st.subheader("Before: The Traditional Model")
        st.info("Our manual, siloed process led to slow releases, high risk, and a reactive culture.")
        st.metric("Avg Lead Time", "48 hours")
        st.metric("Avg Change Failure Rate", "18%")

    with col_after:
        st.subheader("After: The Modern DevOps Chapter")
        st.success("By leveraging our tools, we've achieved a streamlined, collaborative pipeline.")
        st.metric("New Avg Lead Time", "20 hours", "-58% decrease")
        st.metric("New Avg Change Failure Rate", "12%", "-33% decrease")

    st.markdown("---")
    st.subheader("Simulate Your ROI")
    st.markdown("Use the slider to see how a reduction in incidents directly translates to cost savings.")

    incidents_per_year = st.slider("Number of Production Incidents per year", 10, 200, 150)
    cost_per_incident = st.slider("Avg. Cost per Incident (person-hours)", 10, 50, 25)

    current_cost = incidents_per_year * cost_per_incident * 1.0
    projected_cost = (incidents_per_year * (1 - 0.33)) * cost_per_incident

    savings = current_cost - projected_cost

    st.metric("Projected Annual Savings", f"${savings*20:.2f}k", f"based on a 33% reduction in incident rate")
    st.caption("Assumes an average hourly rate of $20 per person.")

# --- Tab 4: AI/ML & The Future ---
with tab4:
    st.header("The Future: AI/ML in DevSecOps")
    st.markdown("Our next strategic differentiator is integrating intelligence into the pipeline to automate decisions and proactively reduce risk.")

    st.subheader("Predictive Build Failure")
    st.info("Simulate an AI model that predicts if a build will fail based on historical data.")
    if st.button("Run Prediction"):
        with st.spinner("Analyzing historical patterns..."):
            st.warning("Prediction: High risk of failure (85% confidence). Suggested action: Reroute to a parallel test suite to confirm.")

    st.subheader("Intelligent Test Selection")
    st.info("Simulate how a smarter test runner could save time by only running relevant tests for a given code change.")
    if st.button("Simulate Smart Testing"):
        with st.spinner("Analyzing code change context..."):
            st.success("Test savings: Skipped 75% of tests. Total tests run: 25%. Pipeline time saved: 15 minutes.")

    st.subheader("Automated SonarQube Remediation")
    st.info("Simulate how AI can provide instant, actionable advice on a security vulnerability.")
    if st.button("Get Remediation Advice"):
        with st.spinner("Consulting knowledge base..."):
            st.write("Vulnerability: Log4j CVE-2021-44228")
            st.markdown("---")
            st.success("AI-powered Remediation:")
            st.markdown("Summary: The vulnerability is found in `commons-collections.jar`.")
            st.markdown("Action: Update the `commons-collections` dependency to `3.2.2` or higher in your `pom.xml` or `build.gradle` file.")
            st.markdown("Context: Our pipeline should be configured to flag this version using a SonarQube quality gate and prevent the build from proceeding.")
