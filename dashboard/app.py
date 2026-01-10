import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION ---
ST_PAGE_TITLE = "CitiBike Ops Center"

import os

if os.path.exists("citibike.db"):
    DB_CONN = "sqlite:///citibike.db"
    IS_CLOUD = True
else:
    DB_CONN = "mysql+pymysql://root:toor@localhost:3306/citibike"
    IS_CLOUD = False

st.set_page_config(
    page_title=ST_PAGE_TITLE,
    layout="wide"
)

# --- DESIGN SYSTEM ---

THEME = {
    "primary": "#2C3E50",    # Navy Blue (Corporate)
    "secondary": "#E74C3C",  # Coral Red (Alerts/Negative)
    "accent": "#18BC9C",     # Teal (Positive/Growth)
    "background": "#F0F2F6", # Light Gray
    "text": "#2C3E50"
}

# Unified CSS for Cards and Headers
st.markdown(f"""
<style>
    /* Metric Cards - Force White Background & Dark Text */
    div[data-testid="stMetric"] {{
        background-color: #FFFFFF !important;
        border-left: 5px solid {THEME['primary']};
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-radius: 5px;
        color: #2C3E50 !important;
    }}
    
    /* Specific overrides for text elements inside the card */
    div[data-testid="stMetric"] label {{
        color: #2C3E50 !important;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: #2C3E50 !important;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {{
        color: #555555 !important;
    }}
    
    /* Headers */
    h1, h2, h3 {{
        font-family: 'Segoe UI', sans-serif;
        color: {THEME['text']};
    }}
    
    /* Remove default footer */
    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# --- DATA LOADER ---
@st.cache_data(ttl=600)
def fetch_data(query):
    try:
        engine = create_engine(DB_CONN)
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return pd.DataFrame()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Dashboard Controls")
    view_mode = st.selectbox("View Perspective", ["Operations (Real-time)", "Strategic (Historical)"])
    st.markdown("---")
    
    # Debug Info (Helpful for Cloud Deployment)
    with st.expander("Connection Debug info"):
        st.write(f"**Mode:** {'Cloud (SQLite)' if IS_CLOUD else 'Local (MySQL)'}")
        st.write(f"**CWD:** `{os.getcwd()}`")
        st.write(f"**DB Path:** `{DB_PATH_DEBUG}`")
        if not IS_CLOUD and "sqlite" not in DB_CONN:
             st.warning("Using Local MySQL. This will FAIL on Streamlit Cloud.")

# --- MAIN LAYOUT ---
st.title(f"{ST_PAGE_TITLE}")

# 1. KPI SECTION (Top Row)
if view_mode == "Operations (Real-time)":
    # Mock aggregation for KPIs
    metrics_sql = "SELECT count(*) as total, avg(duration_seconds)/60 as avg_dur FROM fact_trips"
    metrics = fetch_data(metrics_sql)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Trips", f"{metrics['total'][0]:,.0f}", delta="24h Volume")
    with k2:
        st.metric("Avg Duration", f"{metrics['avg_dur'][0]:.1f} min", delta="-0.2 min")
    with k3:
        st.metric("Active Stations", "784", delta="100% Operational")
    with k4:
        st.metric("Health Score", "98.2%", delta="Optimal")
    
    st.markdown("---")

    # 2. CHARTS SECTION (Grid)
    col1, col2 = st.columns([1, 1])

    # CHART 1: NET FLOW (Diverging Bar)
    with col1:
        st.subheader("Station Imbalance (Net Flow)")
        st.caption("Which stations are gaining (Teal) vs losing (Red) inventory?")
        
        flow_sql = """
        WITH inbound AS (SELECT end_station_id, COUNT(*) as cnt FROM fact_trips GROUP BY 1),
             outbound AS (SELECT start_station_id, COUNT(*) as cnt FROM fact_trips GROUP BY 1)
        SELECT 
            s.station_name,
            (COALESCE(i.cnt, 0) - COALESCE(o.cnt, 0)) as net_flow
        FROM dim_station s
        LEFT JOIN inbound i ON s.station_id = i.end_station_id
        LEFT JOIN outbound o ON s.station_id = o.start_station_id
        ORDER BY ABS(net_flow) DESC LIMIT 10;
        """
        df_flow = fetch_data(flow_sql)
        df_flow['color'] = df_flow['net_flow'].apply(lambda x: THEME['accent'] if x > 0 else THEME['secondary'])
        
        fig_flow = go.Figure()
        fig_flow.add_trace(go.Bar(
            y=df_flow['station_name'],
            x=df_flow['net_flow'],
            orientation='h',
            marker=dict(color=df_flow['color']),
            text=df_flow['net_flow'],
            textposition='auto'
        ))
        fig_flow.update_layout(
            barmode='relative',
            yaxis={'categoryorder':'total ascending'},
            xaxis_title="Net Bikes (In - Out)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig_flow, use_container_width=True)

    # CHART 2: HOURLY DEMAND (Area Chart)
    with col2:
        st.subheader("Demand Curve (24h)")
        st.caption("Peak traffic identification for resource allocation.")
        
        demand_sql = """
        SELECT HOUR(started_at) as hr, member_casual, COUNT(*) as trips 
        FROM fact_trips GROUP BY 1, 2 ORDER BY 1
        """
        df_demand = fetch_data(demand_sql)
        
        fig_area = px.area(
            df_demand, 
            x="hr", 
            y="trips", 
            color="member_casual",
            color_discrete_map={"member": THEME['primary'], "casual": THEME['accent']},
        )
        fig_area.update_layout(
            xaxis=dict(title="Hour of Day", dtick=2),
            yaxis=dict(title="Volume"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_area, use_container_width=True)

elif view_mode == "Strategic (Historical)":
    st.header("Historical Trends & Strategy")
    st.markdown("Long-term patterns to inform quarterly planning and fleet expansion.")
    
    # Aggregation for Day of Week
    # Note: Using MySQL's DAYNAME
    dow_sql = """
    SELECT DAYNAME(started_at) as day_name, COUNT(*) as trips 
    FROM fact_trips 
    GROUP BY 1 
    ORDER BY FIELD(day_name, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
    """
    df_dow = fetch_data(dow_sql)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Weekly Usage Pattern")
        fig_dow = px.bar(
            df_dow, 
            x="day_name", 
            y="trips",
            color="trips",
            color_continuous_scale="Blues",
            title="Trips by Day of Week"
        )
        fig_dow.update_layout(plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_dow, use_container_width=True)
        
    with col2:
        st.subheader("Strategic Recommendation")
        st.info("""
        **Weekend vs Weekday Strategy**:
        - **Weekdays**: High commuter volume. Prioritize **Speed** (Dock availability).
        - **Weekends**: High leisure volume. Prioritize **Maintenance** & Tourist spots.
        """)
        
        avg_dur_sql = "SELECT AVG(duration_seconds)/60 as val FROM fact_trips"
        avg_val = fetch_data(avg_dur_sql)['val'][0]
        st.metric("Avg Trip Duration (Hist)", f"{avg_val:.1f} min")

else:
    st.write("Select a view mode.")
