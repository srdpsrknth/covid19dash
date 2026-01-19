import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from pathlib import Path
import numpy as np

# Set page config
st.set_page_config(page_title="COVID-19 Dashboard Netherlands", layout="wide")

# Set paths
CLEANPATH = Path.cwd() / 'clean-data'
EXTERNALPATH = Path.cwd() / 'external'

# Load data
try:
    df_ndaily = pd.read_csv(CLEANPATH /'national_daily_clean.csv',index_col=0)
    df_ncumu = pd.read_csv(CLEANPATH /'national_cumulative_clean.csv',index_col=0)
    df_pdaily = pd.read_csv(CLEANPATH / 'province_daily_clean.csv', index_col=0)
    df_pcumu = pd.read_csv(CLEANPATH / 'province_cumulative_clean.csv', index_col=0)
    df_r = pd.read_csv(CLEANPATH /'reproduction_clean.csv',index_col=0)
    df_contagious = pd.read_csv(CLEANPATH /'contagious_clean.csv',index_col=0)
    df_desc = pd.read_csv(CLEANPATH /'descriptive_clean.csv',index_col=0)
except FileNotFoundError as e:
    st.error(f"Data file not found: {e}. Make sure the 'clean-data' directory is in the correct location.")
    st.stop()

# Convert date columns to datetime
for df in [df_ndaily, df_ncumu, df_pdaily, df_pcumu, df_r, df_contagious]:
    df['date'] = pd.to_datetime(df['date'])

# Load GeoJSON
try:
    with open(EXTERNALPATH / 'the-netherlands.json') as f:
        nl_geojson = json.load(f)
except FileNotFoundError:
    st.error("GeoJSON file not found. Make sure 'the-netherlands.json' is in the 'external' directory.")
    st.stop()


select = {'cumu':'Cumulative', 'daily':'Daily','total':'Confirmed', 'admitted':'Hospitalised', 'deaths':'Deaths'}


# ============================================================================
# PLOTTING FUNCTIONS
# ============================================================================

def nat_line_plot(dtype='cumu', param='total'):
    """Create national line plot with bar overlay"""
    if dtype == 'cumu':
        df = df_ncumu
    elif dtype == 'daily':
        df = df_ndaily
    else:
        st.error("Incorrect input type. Choose dtype = 'cumu' or 'daily'")
        return None

    fig = go.Figure()

    # Add bar trace
    fig.add_trace(go.Bar(
        x=df['date'], 
        y=df[param],
        name=f'{select.get(param, param)}',
        marker_color='rgba(31, 119, 180, 0.7)',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>%{y:,.0f}<extra></extra>'
    ))

    # Add line trace
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df[param],
        name=f'{select.get(param, param)} Trend',
        line=dict(color='#FF6B6B', width=3),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>%{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        autosize=True,
        margin=dict(t=40, b=20, l=60, r=20),
        template="plotly_white",
        title_font_size=18,
        hovermode='x unified',
        xaxis_title="Date",
        yaxis_title=f'{select.get(param, param)}',
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)')
    )
    
    return fig


def province_line_plot(dtype='cumu', param='total'):
    """Create provincial line plot showing trend across provinces"""
    if dtype == 'cumu':
        df = df_pcumu
    elif dtype == 'daily':
        df = df_pdaily
    else:
        st.error("Incorrect input type. Choose dtype = 'cumu' or 'daily'")
        return None

    province_list = sorted(df['province'].unique())
    
    fig = go.Figure()

    for prov in province_list:
        prov_data = df.query(f"province=='{prov}'")
        fig.add_trace(
            go.Scatter(
                x=prov_data['date'],
                y=prov_data[param],
                name=prov,
                mode='lines',
                hovertemplate='<b>%{fullData.name}</b><br>%{x|%Y-%m-%d}<br>%{y:,.0f}<extra></extra>'
            )
        )
    
    fig.update_layout(
        autosize=True,
        template="plotly_white",
        title=f"{select.get(dtype, dtype)} {select.get(param, param)} by Province",
        title_font_size=18,
        hovermode='x unified',
        xaxis_title="Date",
        yaxis_title=f'{select.get(param, param)}',
        margin=dict(t=60, b=20, l=60, r=20),
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)')
    )

    return fig


def nl_choropleth_latest(dtype='cumu', param='total'):
    """Create choropleth map of latest data by province"""
    if dtype == 'cumu':
        df = df_pcumu
    elif dtype == 'daily':
        df = df_pdaily
    else:
        st.error("Incorrect input type. Choose dtype = 'cumu' or 'daily'")
        return None
    
    date_latest = df['date'].max()
    
    df_latest = df[df['date'] == date_latest].copy()
    r_min = df_latest[param].min()
    r_max = df_latest[param].max()
    
    fig = px.choropleth_mapbox(
        df_latest, 
        geojson=nl_geojson,
        locations='province', 
        color=param,
        featureidkey="properties.name",
        color_continuous_scale="YlOrRd",
        range_color=(r_min, r_max),
        mapbox_style="light",
        zoom=6,
        center={"lat": 52.1326, "lon": 5.2913},
        opacity=0.8,
        hover_name='province',
        hover_data={param: ':.0f'},
        title=f"{select.get(dtype, dtype)} {select.get(param, param)} - {date_latest.strftime('%Y-%m-%d')}"
    )

    fig.update_layout(
        autosize=True,
        margin=dict(t=50, b=20, l=20, r=20),
        title_font_size=16
    )

    # Add Mapbox token for styling
    fig.update_layout(mapbox_accesstoken="pk.eyJ1IjoiendlaWxvdXMiLCJhIjoiY2tpaXdmZ3F4MTJ4djJwbXF5dnozeHk0eiJ9.HrPRH33LUQagKn4e_fd3oQ") 
    
    return fig


def repro_plt(df):
    """Plot reproduction number with confidence bands"""
    df_sorted = df.sort_values('date')
    
    fig = go.Figure()

    # Add upper bound
    fig.add_trace(go.Scatter(
        x=df_sorted['date'],
        y=df_sorted['R_high'],
        fill=None,
        mode='lines',
        line_color='rgba(0,0,0,0)',
        showlegend=False,
        hoverinfo='skip'
    ))

    # Add shaded area (confidence band)
    fig.add_trace(go.Scatter(
        x=df_sorted['date'],
        y=df_sorted['R_min'],
        fill='tonexty',
        fillcolor='rgba(0,100,255,0.2)',
        mode='lines',
        line_color='rgba(0,0,0,0)',
        name='Confidence Band',
        hoverinfo='skip'
    ))

    # Add average line
    fig.add_trace(go.Scatter(
        x=df_sorted['date'],
        y=df_sorted['R_avg'],
        line_color='#EF553B',
        name='R Average',
        mode='lines+markers',
        line=dict(width=3),
        marker=dict(size=5),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>R: %{y:.2f}<extra></extra>'
    ))

    # Add reference line at R=1
    fig.add_hline(
        y=1.0,
        line_dash="dash",
        line_color="gray",
        annotation_text="R=1 (Epidemic threshold)",
        annotation_position="right"
    )
    
    fig.update_layout(
        autosize=True,
        template="plotly_white",
        title="Reproduction Number (R) Over Time",
        title_font_size=18,
        xaxis_title="Date",
        yaxis_title="Reproduction Number",
        hovermode='x unified',
        margin=dict(t=60, b=20, l=60, r=100),
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)')
    )
    
    return fig


def contagious_plt(df):
    """Plot contagious prevalence with confidence bands"""
    df_sorted = df.sort_values('date')
    
    fig = go.Figure()

    # Add upper bound
    fig.add_trace(go.Scatter(
        x=df_sorted['date'],
        y=df_sorted['Rt_up'],
        fill=None,
        mode='lines',
        line_color='rgba(0,0,0,0)',
        showlegend=False,
        hoverinfo='skip'
    ))

    # Add shaded area (confidence band)
    fig.add_trace(go.Scatter(
        x=df_sorted['date'],
        y=df_sorted['Rt_low'],
        fill='tonexty',
        fillcolor='rgba(255,165,0,0.2)',
        mode='lines',
        line_color='rgba(0,0,0,0)',
        name='Confidence Band',
        hoverinfo='skip'
    ))

    # Add average line
    fig.add_trace(go.Scatter(
        x=df_sorted['date'],
        y=df_sorted['Rt_avg'],
        line_color='#AB63FA',
        name='Prevalence Average',
        mode='lines+markers',
        line=dict(width=3),
        marker=dict(size=5),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Prevalence: %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        autosize=True,
        template="plotly_white",
        title="Contagious Prevalence Over Time",
        title_font_size=18,
        xaxis_title="Date",
        yaxis_title="Prevalence",
        hovermode='x unified',
        margin=dict(t=60, b=20, l=60, r=20),
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)')
    )
    
    return fig


def deaths_by_age_sex():
    """Histogram of deaths by age group and sex"""
    df_deaths = df_desc[df_desc['Death'] == 'Yes'].copy()
    
    fig = px.histogram(
        df_deaths,
        x="agegroup",
        color='sex',
        title="COVID-19 Deaths by Age Group and Sex",
        labels={'agegroup': 'Age Group', 'sex': 'Sex', 'count': 'Number of Deaths'},
        barmode='group',
        color_discrete_map={'M': '#1f77b4', 'F': '#ff7f0e', 'U': '#d62728'}
    )
    
    fig.update_layout(
        autosize=True,
        template="plotly_white",
        title_font_size=18,
        xaxis_title="Age Group",
        yaxis_title="Number of Deaths",
        margin=dict(t=60, b=50, l=60, r=20),
        legend_title="Sex"
    )
    fig.update_xaxes(categoryorder='array', categoryarray=sorted(df_deaths['agegroup'].unique()))
    
    return fig


def confirmed_by_age_sex():
    """Histogram of confirmed cases by age group and sex"""
    df_confirmed = df_desc.copy()
    
    fig = px.histogram(
        df_confirmed,
        x="agegroup",
        color='sex',
        title="COVID-19 Confirmed Cases by Age Group and Sex",
        labels={'agegroup': 'Age Group', 'sex': 'Sex', 'count': 'Number of Cases'},
        barmode='group',
        color_discrete_map={'M': '#1f77b4', 'F': '#ff7f0e', 'U': '#d62728'}
    )
    
    fig.update_layout(
        autosize=True,
        template="plotly_white",
        title_font_size=18,
        xaxis_title="Age Group",
        yaxis_title="Number of Cases",
        margin=dict(t=60, b=50, l=60, r=20),
        legend_title="Sex"
    )
    fig.update_xaxes(categoryorder='array', categoryarray=sorted(df_confirmed['agegroup'].unique()))
    
    return fig


def deaths_by_province():
    """Bar chart of cumulative deaths by province - latest date"""
    date_latest = df_pcumu['date'].max()
    df_latest = df_pcumu[df_pcumu['date'] == date_latest].copy()
    df_latest = df_latest.sort_values('deaths', ascending=True)
    
    fig = px.bar(
        df_latest,
        x='deaths',
        y='province',
        title=f"Cumulative Deaths by Province - {date_latest.strftime('%Y-%m-%d')}",
        labels={'deaths': 'Number of Deaths', 'province': 'Province'},
        orientation='h',
        color='deaths',
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        autosize=True,
        template="plotly_white",
        title_font_size=16,
        xaxis_title="Number of Deaths",
        yaxis_title="Province",
        margin=dict(t=50, b=20, l=100, r=20),
        showlegend=False
    )
    
    return fig


# ============================================================================
# DASHBOARD UI
# ============================================================================

st.title('COVID-19 Dashboard - The Netherlands')
st.markdown("---")

st.warning(
    "Daily deaths from the RIVM daily feed are currently unavailable because the source data is unreliable. "
    "Daily death charts are hidden; cumulative deaths remain available."
)

# Add metadata about data
col1, col2, col3 = st.columns(3)
with col1:
    latest_date = df_ncumu['date'].max()
    st.metric("Latest Data Date", latest_date.strftime('%Y-%m-%d'))
with col2:
    total_confirmed = df_ncumu[df_ncumu['date'] == latest_date]['total'].values[0]
    st.metric("Total Confirmed Cases", f"{int(total_confirmed):,.0f}")
with col3:
    total_deaths = df_ncumu[df_ncumu['date'] == latest_date]['deaths'].values[0]
    st.metric("Total Deaths", f"{int(total_deaths):,.0f}")

st.markdown("---")

# Sidebar
st.sidebar.title('View Options')
view = st.sidebar.radio("Select view", ('Overview', 'National', 'Provincial', 'Reproduction & Prevalence', 'Descriptive Analysis'))

dtype_map = {'Cumulative': 'cumu', 'Daily': 'daily'}
param_map = {'Confirmed': 'total', 'Hospitalised': 'admitted', 'Deaths': 'deaths'}

# ============================================================================
# OVERVIEW TAB
# ============================================================================
if view == 'Overview':
    st.header('Overview - Key Indicators')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('National Daily Cases')
        fig = nat_line_plot(dtype='daily', param='total')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader('National Daily Deaths')
        st.info("Hidden: daily deaths suppressed due to unreliable source data.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('Reproduction Number (R)')
        fig = repro_plt(df_r)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader('Contagious Prevalence')
        fig = contagious_plt(df_contagious)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# NATIONAL TAB
# ============================================================================
elif view == 'National':
    st.header('National Data Analysis')
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        data_type = st.sidebar.radio("Data type", ('Cumulative', 'Daily'))
    with col2:
        if data_type == 'Daily':
            parameter = st.sidebar.radio("Parameter", ('Confirmed', 'Hospitalised'))
        else:
            parameter = st.sidebar.radio("Parameter", ('Confirmed', 'Hospitalised', 'Deaths'))
    
    selected_dtype = dtype_map[data_type]
    selected_param = param_map[parameter]

    st.subheader(f'National {data_type} {parameter}')
    fig = nat_line_plot(dtype=selected_dtype, param=selected_param)
    st.plotly_chart(fig, use_container_width=True)
    
    # Show summary statistics
    with st.expander("📊 Summary Statistics"):
        if selected_dtype == 'cumu':
            df = df_ncumu
        else:
            df = df_ndaily
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Latest Value", f"{int(df[selected_param].iloc[-1]):,.0f}")
        with col2:
            st.metric("Maximum", f"{int(df[selected_param].max()):,.0f}")
        with col3:
            st.metric("Average", f"{int(df[selected_param].mean()):,.0f}")
        with col4:
            st.metric("Minimum", f"{int(df[selected_param].min()):,.0f}")

# ============================================================================
# PROVINCIAL TAB
# ============================================================================
elif view == 'Provincial':
    st.header('Provincial Data Analysis')
    
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        plot_type = st.sidebar.radio("Plot type", ('Line Plot', 'Choropleth', 'Bar Chart'))
    with col2:
        data_type = st.sidebar.radio("Data type", ('Cumulative', 'Daily'))
    with col3:
        if data_type == 'Daily':
            parameter = st.sidebar.radio("Parameter", ('Confirmed',))
        else:
            parameter = st.sidebar.radio("Parameter", ('Confirmed', 'Deaths'))
    
    selected_dtype = dtype_map[data_type]
    selected_param = param_map[parameter]

    if plot_type == 'Line Plot':
        st.subheader(f'Provincial {data_type} {parameter} - Line Plot')
        fig = province_line_plot(dtype=selected_dtype, param=selected_param)
        st.plotly_chart(fig, use_container_width=True)
    
    elif plot_type == 'Choropleth':
        st.subheader(f'Provincial {data_type} {parameter} - Map View (Latest Data)')
        fig = nl_choropleth_latest(dtype=selected_dtype, param=selected_param)
        st.plotly_chart(fig, use_container_width=True)
    
    elif plot_type == 'Bar Chart':
        st.subheader(f'Cumulative Deaths by Province - Latest Data')
        fig = deaths_by_province()
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# REPRODUCTION & PREVALENCE TAB
# ============================================================================
elif view == 'Reproduction & Prevalence':
    st.header('Epidemiological Indicators')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('Reproduction Number (R)')
        st.markdown("""
        **R** represents the average number of people infected by each positive case.
        - R > 1: Epidemic is growing
        - R < 1: Epidemic is declining
        - R ≈ 1: Epidemic is stable
        """)
        fig = repro_plt(df_r)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader('Contagious Prevalence')
        st.markdown("""
        **Prevalence** shows the proportion of the population that is contagious.
        This indicator helps track the active infection rate in the population.
        """)
        fig = contagious_plt(df_contagious)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# DESCRIPTIVE ANALYSIS TAB
# ============================================================================
elif view == 'Descriptive Analysis':
    st.header('Demographic Analysis')
    
    analysis_type = st.sidebar.radio("Select analysis", ('Deaths by Age & Sex', 'Cases by Age & Sex', 'Deaths by Province'))
    
    if analysis_type == 'Deaths by Age & Sex':
        st.subheader('COVID-19 Deaths by Age Group and Sex')
        fig = deaths_by_age_sex()
        st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == 'Cases by Age & Sex':
        st.subheader('COVID-19 Confirmed Cases by Age Group and Sex')
        fig = confirmed_by_age_sex()
        st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == 'Deaths by Province':
        st.subheader('Geographic Distribution')
        fig = deaths_by_province()
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
**Data Source:** RIVM (Rijksinstituut voor Volksgezondheid en Milieu)  
**Last Updated:** COVID-19 data is updated daily from RIVM sources.  
**Dashboard Version:** 1.0
""")
