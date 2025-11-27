import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, LineString
from shapely.ops import split, linemerge, unary_union
from datetime import timedelta
import folium
from folium.plugins import TimestampedGeoJson
import networkx as nx
#from sklearn.neighbors import BallTree
from shapely.strtree import STRtree
import streamlit as st
from streamlit_folium import st_folium
import base64
from components_international import continent_card
import streamlit.components.v1 as components
import plotly.express as px
from folium.plugins import HeatMap,MarkerCluster, Fullscreen

access_token = 'sgKt0HmG4TTVt9lXUCAjaLsSPLMoVN7CnA8LegyngahiKtMimaUg83TvgfROeUCe' #Access token jawg.io (MAP)

#[Set up the page title]
st.markdown(f"""
        <style>
        .block-container {{
            padding-top: 1rem;
        }} </style>
        <h1 style='display: flex; align-items: center;gap: 12px; margin-top: 10px;'> <img src='https://www.thiings.co/_next/image?url=https%3A%2F%2Flftz25oez4aqbxpq.public.blob.vercel-storage.com%2Fimage-X7dat6FnLoK14tvhi0ecr3pgW3GHAe.png&w=1000&q=75' width='85' style='margin-bottom: 4px;'/>
            International Trade with Puerto Rico 
            <span style='color:#c8c9d0; font-weight:normal;'> <h1> Maritime cargo </h1></span> </h1> """, unsafe_allow_html=True)


international_trade ="U.S International Trade - Imports and Exports.xlsx" #File Path
# [Load and prepare database]
@st.cache_data(show_spinner="Loading data...")
def load_and_prepare_data(file_path: str) -> pd.DataFrame:
    try:
        data = pd.read_excel(file_path, header=0)
    except FileNotFoundError:
        st.error(f"File was not found: {file_path}")
        st.stop()
    data['Latitude_country'] = pd.to_numeric(data['Latitude_country'], errors='coerce')
    data['Longitude_country'] = pd.to_numeric(data['Longitude_country'], errors='coerce')

    for col in ['Latitude_country', 'Longitude_country']:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
        else:
            st.warning(f"⚠️ La columna '{col}' no fue encontrada en los datos.")
        
    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    #st.dataframe(data.head(20), use_container_width=True)
    return data

def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def filter_sidebar(data: pd.DataFrame) -> tuple[pd.DataFrame, dict]: #set up the sidebar
    dfi = data.copy()
    logo_base64 = get_base64_image("assets/Images/Logos/CETL.png")
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center; margin-top:-15px; margin-bottom: 30px;'>
            <img src="data:image/png;base64,{logo_base64}" style="width:700px; border-radius:10px; box-shadow: 0 0px 0px rgba(0,0,0,0.1);">
        </div>
        """, unsafe_allow_html=True)
        
        st.header("Filters") #Title for the sidebar

        #take the unique values for the select boxes
        country_options = ['All'] + sorted(dfi['Country'].unique().tolist())
        dfi['International Organization'] = dfi['International Organization'].fillna('Not Applicable')  # Fill NaN with empty string
        organization_options = (dfi['International Organization'].dropna().astype(str).unique().tolist())
        organization_options = ['All'] + sorted(organization_options)
        port_options = ['All'] + sorted(dfi['Port'].dropna().unique().tolist())
        year_options = ['All'] + sorted(dfi['Year'].dropna().unique().tolist())
        

        #Select box for country selection
        select_year = st.selectbox("Select Year", options=year_options, index=0)
        select_flowtype = st.selectbox("Select Flow Type", options=dfi['Indicator'].unique().tolist(), index=0)
        select_port = st.selectbox("Select Port", options=port_options, index=0)   
        #select_country = st.selectbox("Select Country", options=country_options, index=0, disabled=True)
        #select_international_organization = st.selectbox("Select International Organization", options=organization_options, index=0, disabled=True) 
    
    #Logic to filter the data
    filtered_data = dfi.copy()
    if select_flowtype is not None:
        filtered_data = filtered_data[filtered_data['Indicator'] == select_flowtype]
    
    if select_port != 'All':
        filtered_data = filtered_data[filtered_data['Port'] == select_port] if select_port != 'All' else filtered_data
    
    if select_year != 'All':
        filtered_data = filtered_data[filtered_data['Year'] == select_year] if select_year != 'All' else filtered_data

    
    filters = {
        "Year": select_year,
        #"Country": select_country,
        "Port": select_port,
        "Flow Type": select_flowtype
    }
    #st.write(filtered_data.head(10))

    return dfi, filtered_data, filters

@st.cache_data(show_spinner="Loading data...")
def load_and_prepare_data(file_path: str) -> pd.DataFrame:
    try:
        data = pd.read_excel(file_path, header=0)
    except FileNotFoundError:
        st.error(f"File was not found: {file_path}")
        st.stop()
    data['Latitude_country'] = pd.to_numeric(data['Latitude_country'], errors='coerce')
    data['Longitude_country'] = pd.to_numeric(data['Longitude_country'], errors='coerce')

    for col in ['Latitude_country', 'Longitude_country']:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
        else:
            st.warning(f"⚠️ La columna '{col}' no fue encontrada en los datos.")
        
    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    #st.dataframe(data.head(20), use_container_width=True)
    return data

def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def filter_sidebar(data: pd.DataFrame) -> tuple[pd.DataFrame, dict]: #set up the sidebar
    dfi = data.copy()
    logo_base64 = get_base64_image("assets/Images/Logos/CETL.png")
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center; margin-top:-15px; margin-bottom: 30px;'>
            <img src="data:image/png;base64,{logo_base64}" style="width:700px; border-radius:10px; box-shadow: 0 0px 0px rgba(0,0,0,0.1);">
        </div>
        """, unsafe_allow_html=True)
        
        st.header("Filters") #Title for the sidebar

        #take the unique values for the select boxes
        country_options = ['All'] + sorted(dfi['Country'].unique().tolist())
        dfi['International Organization'] = dfi['International Organization'].fillna('Not Applicable')  # Fill NaN with empty string
        organization_options = (dfi['International Organization'].dropna().astype(str).unique().tolist())
        organization_options = ['All'] + sorted(organization_options)
        port_options = ['All'] + sorted(dfi['Port'].dropna().unique().tolist())
        year_options = ['All'] + sorted(dfi['Year'].dropna().unique().tolist())
        

        #Select box for country selection
        select_year = st.selectbox("Select Year", options=year_options, index=0)
        select_flowtype = st.selectbox("Select Flow Type", options=dfi['Indicator'].unique().tolist(), index=0)
        select_port = st.selectbox("Select Port", options=port_options, index=0)   
        #select_country = st.selectbox("Select Country", options=country_options, index=0, disabled=True)
        #select_international_organization = st.selectbox("Select International Organization", options=organization_options, index=0, disabled=True) 
    
    #Logic to filter the data
    filtered_data = dfi.copy()
    if select_flowtype is not None:
        filtered_data = filtered_data[filtered_data['Indicator'] == select_flowtype]
    
    if select_port != 'All':
        filtered_data = filtered_data[filtered_data['Port'] == select_port] if select_port != 'All' else filtered_data
    
    if select_year != 'All':
        filtered_data = filtered_data[filtered_data['Year'] == select_year] if select_year != 'All' else filtered_data

    
    filters = {
        "Year": select_year,
        #"Country": select_country,
        "Port": select_port,
        "Flow Type": select_flowtype
    }
    #st.write(filtered_data.head(10))

    return dfi, filtered_data, filters

def compute_delta(df, select_year, Indicator=None, port=None):
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

        if select_year is None or select_year == 'All':
            return None, None
        
        if Indicator:
            df = df[df['Indicator'] == flow_type]
        
        if port and port != 'All':
            df = df[df['Port'] == port]

        previous_year = select_year - 1
        current_df = df[(df['Year'] == select_year)]
        previous_df = df[(df['Year'] == previous_year)]
        
        tons_current = current_df['Containerized Vessel Total Exports SWT (Tons))'].sum()
        tons_previous = previous_df['Containerized Vessel Total Exports SWT (Tons)'].sum()

        if tons_previous != 0:
            delta_tons = tons_current - tons_previous
            delta_percent = (delta_tons / tons_previous) * 100
            return delta_tons, delta_percent
        else:
            return None, None
        
def metrics_international_trade(df_filtered, dfi, flow_type, year, port):
    st.markdown("""
        <style>
        .metric-box {
            background-color: #eef2f7;
            border-radius: 12px;
            padding: 8px;
            height: 125px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            margin-bottom: 20px;
           
            padding-left: 10px; 
            
        }
        .metric-box::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 10px;
            background: linear-gradient(135deg, #3d7a4d 0%, #3d9a9a 100%);
            border-radius: 15px 15px 0 0;
        } 
        .metric-label {
            font-size: 20px;
            font-weight: 700;
            color: #333;
            margin-bottom: 10px;
            margin-top: 1px;
        }
                
        .metric-icon {
            font-size: 50px;
            margin-bottom: 1px;
        }

        .metric-value {
            font-size: 25px;
            font-weight: 800;
            color: #7F8C8D;
            margin-top: -20px;
            margin-bottom: -10px;
        }

        .metric-delta {
            font-size: 15px;
            font-weight: 500;
            color: #2e7d32;
            margin-top: 5px;
        }
        .metric-subtext {
            font-size: 12px;
            color: #333;
            margin-top: -15px;
            font-weight: 500;
        }
        .metric-midtext {
            font-size: 18px;
            color: #555;
            margin-top: 10px;
            font-weight: 500;
        }
     
        </style>
    """, unsafe_allow_html=True)

    #Function to format the delta values
    def format_delta(delta_tons, delta_percent):
        if delta_tons is None:
            return """
            <span style='
                background-color:#ECEFF1;
                color:#607d8b;
                padding:2px 15px;
                border-radius:25px;
                border: 1px solid #B0BEC5;
                font-weight:600;
                display:inline-block;
            '> No data from previous year </span>
            """

        arrow = "↑" if delta_tons > 0 else "↓"
        color = "#388e3c" if delta_tons > 0 else "#d32f2f"
        background = "#e8f5e9" if delta_tons > 0 else "#ffebee"

        return f"""
        <span style='
            background-color:{background};
            color:{color};
            padding:1px 20px;
            border-radius:20px;
            font-weight:600;
            border: 1px solid #B0BEC5;
            display:inline-block;
        '>{arrow} {delta_tons:,.0f} tons ({delta_percent:.2f}%)</span>
        """

    # Function to render metrics boxes
    def render_metric( label, value, delta, midtext=""):
        value_formatted = f"{float(value):,.0f}"
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">{label}</div>
                <div class="metric-midtext" style="font-size:25px; color:#9E9E9E; margin-bottom:-5px;font-weight: 600;">{midtext}</div>
                <div class="metric-value">{value_formatted}</div>
                <div class="metric-delta">{delta}</div>
            </div>
        """, unsafe_allow_html=True)
    # Imports
    if year != "All":
        year = int(year)
        df_imports = dfi[
            (dfi['Year'] == year) &
            (dfi['Indicator'].str.upper() == "IMPORTS") &
            (dfi['Country'].str.upper() == "WORLD TOTAL")
        ]
        df_imports_prev = dfi[
            (dfi['Year'] == year - 1) &
            (dfi['Indicator'].str.upper() == "IMPORTS") &
            (dfi['Country'].str.upper() == "WORLD TOTAL") &
            (dfi['Continent'] != "NOT APPLICABLE")
        ]
    else:
        df_imports = dfi[
            (dfi['Indicator'].str.upper() == "IMPORTS") &
            (dfi['Country'].str.upper() == "WORLD TOTAL")
        ]
        df_imports_prev = pd.DataFrame()

    import_tons = df_imports['Containerized Vessel Total Exports SWT (Tons)'].sum()
    import_value = df_imports['Containerized Vessel Total Exports Value ($US)'].sum()

    if not df_imports_prev.empty:
        import_tons_prev = df_imports_prev['Containerized Vessel Total Exports SWT (Tons)'].sum()
        import_value_prev = df_imports_prev['Containerized Vessel Total Exports Value ($US)'].sum()
        import_delta_tons = format_delta(import_tons - import_tons_prev, ((import_tons - import_tons_prev) / import_tons_prev) * 100)
        import_delta_value = format_delta(import_value - import_value_prev, ((import_value - import_value_prev) / import_value_prev) * 100)
    else:
        import_delta_tons = format_delta(None, None)
        import_delta_value = format_delta(None, None)

    # Exports
    if year != "All":
        df_exports = dfi[
            (dfi['Year'] == year) &
            (dfi['Indicator'].str.upper() == "EXPORTS") &
            (dfi['Continent'] != "NOT APPLICABLE") &
            (dfi['International Organization'].str.upper() == "NOT APPLICABLE")
        ]
        df_exports_prev = dfi[
            (dfi['Year'] == year - 1) &
            (dfi['Indicator'].str.upper() == "EXPORTS") &
            (dfi['Continent'] != "NOT APPLICABLE") &
            (dfi['International Organization'].str.upper() == "NOT APPLICABLE")
        ]
    else:
        df_exports = dfi[
            (dfi['Indicator'].str.upper() == "EXPORTS") &
            (dfi['Continent'] != "NOT APPLICABLE") &
            (dfi['International Organization'].str.upper() == "NOT APPLICABLE")
        ]
        df_exports_prev = pd.DataFrame()

    export_tons = df_exports['Containerized Vessel Total Exports SWT (Tons)'].sum()
    export_value = df_exports['Containerized Vessel Total Exports Value ($US)'].sum()

    if not df_exports_prev.empty:
        export_tons_prev = df_exports_prev['Containerized Vessel Total Exports SWT (Tons)'].sum()
        export_value_prev = df_exports_prev['Containerized Vessel Total Exports Value ($US)'].sum()
        export_delta_tons = format_delta(export_tons - export_tons_prev, ((export_tons - export_tons_prev) / export_tons_prev) * 100)
        export_delta_value = format_delta(export_value - export_value_prev, ((export_value - export_value_prev) / export_value_prev) * 100)
    else:
        export_delta_tons = format_delta(None, None)
        export_delta_value = format_delta(None, None)

    def compute_delta_international(df_international, select_year, indicator):
        df_international['Year'] = pd.to_numeric(df_international['Year'], errors='coerce')
        df_international['Continent'] = df_international['Continent'].str.strip().str.upper()
        df_international['International Organization'] = df_international['International Organization'].str.strip().str.upper()
        df_international['Indicator'] = df_international['Indicator'].str.strip().str.upper()
        df_international['Country'] = df_international['Country'].str.strip().str.upper()
        df_international['Containerized Vessel Total Exports SWT (Tons)'] = pd.to_numeric(df_international['Containerized Vessel Total Exports SWT (Tons)'], errors='coerce')

        if select_year is None:
            return None, None

        previous_year = select_year - 1

        base_filter = (
            (df_international['Continent'] != "NOT APPLICABLE") &
            (df_international['International Organization'] == "NOT APPLICABLE") &
            (df_international['Indicator'] == indicator.upper())
        )

        if indicator.upper() == "IMPORTS":
            base_filter = base_filter & (df_international['Country'] == "WORLD TOTAL")

        current_df = df_international[(df_international['Year'] == select_year) & base_filter]
        previous_df = df_international[(df_international['Year'] == previous_year) & base_filter]

        tons_current = current_df['Containerized Vessel Total Exports SWT (Tons)'].sum()
        tons_previous = previous_df['Containerized Vessel Total Exports SWT (Tons)'].sum()

        tons_value = current_df['Containerized Vessel Total Exports Value ($US)'].sum()
        tons_value_prev = previous_df['Containerized Vessel Total Exports Value ($US)'].sum()

        if tons_previous != 0:
            delta_tons = tons_current - tons_previous
            delta_percent = (delta_tons / tons_previous) * 100
            return delta_tons, delta_percent
        else:
            return None, None

     #Metrics for international trade
    # Total internacional - Imports
   



    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown("""
        <div style='
            background-color: #ECEFF1;
            padding: 8px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            margin-bottom: 15px;
            margin-top: -15px;
            border-top: 8px solid #333;
        '>
            <h2 style='color:#0C0A09; font-size:32px; font-weight:700; text-align:center; margin-bottom:-15px; margin-top: -15px;'>Imports</h2>
            <p style='font-size:20px; text-align:center; color: #0C0A09;font-weight:600;'>Inbound Maritime cargo arriving to Puerto Rico</p>
        </div>
    """, unsafe_allow_html=True)
        colimpor_value, colimpor_tons = st.columns([1,1])
        with colimpor_value:
            render_metric(
            label="Containerized Vessel Total Imports Value ($USD)",
            value=import_value,
            delta= import_delta_value, 
        )
        with colimpor_tons:
             render_metric(
            label="Containerized Vessel Total Imports SWT (Tons)",
            value=import_tons,
            delta= import_delta_tons,  
        )   

    with col2: 
        st.markdown("""
        <div style='
            background-color: #ECEFF1;
            padding: 8px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            margin-bottom: 15px;
            margin-top: -15px;
            border-top: 8px solid #333;
        '>
        <h2 style='color:#0C0A09; font-size:32px; font-weight:700; text-align: center; margin-bottom:-15px;margin-top: -15px;'>Exports</h2>
        <p style='font-size:20px;text-align:center; color:#0C0A09; font-weight:600;'>Outbound shipments departing from Puerto Rico</p>
        </div>
    """, unsafe_allow_html=True)

        col1, col2= st.columns([1,1])
        with col1:
            render_metric(
            label="Containerized Vessel Total Exports Value ($USD)",
            value=export_value,
            delta= export_delta_tons,  
        )

        with col2:
             render_metric(
            label="Containerized Vessel Total Exports SWT (Tons)",
            value=export_tons,
            delta= export_delta_tons, 
        )
             
def top_trade_countries(df_filtered, year,flow_type, height=600):   
    df_filtered = df_filtered[
        (df_filtered['Continent'].str.upper() == "NOT APPLICABLE") &
        (df_filtered['International Organization'].str.upper() == "NOT APPLICABLE") &
        (df_filtered['Country'].str.upper() != "WORLD TOTAL") 
    ]
    
    #Group by country and sum tons
    top_trade_df = (
        df_filtered.groupby('Country', as_index=False)['Containerized Vessel Total Exports SWT (Tons)']
        .sum()
        .sort_values(by='Containerized Vessel Total Exports SWT (Tons)', ascending=True)
        .tail(10)
    )

    #create horizontal bar chart
    fig = px.bar(
        top_trade_df,
        orientation= 'h',
        x='Containerized Vessel Total Exports SWT (Tons)',
        y='Country',
        labels={'Country': 'Country', 'Containerized Vessel Total Exports SWT (Tons)': 'Total Weight (Tons)'},
        color='Containerized Vessel Total Exports SWT (Tons)',
        color_continuous_scale='Blues',
        opacity=0.8
    )

    if str(year).upper() != "ALL" and flow_type == 'IMPORTS':
        dtick = 1000000
    elif str(year).upper() != "ALL" and flow_type == 'IMPORTS':
        dtick = 1000000
    
    if str(year).upper() != "ALL" and flow_type == 'EXPORTS':
        dtick = 100000
    else:
        dtick = 100000  #ARREGLARRRRRR

    fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=dtick, 
            showgrid=True,
            ticks='outside',
            tickfont= dict(size=16),
            tickformat='.2s'
        ),
        yaxis=dict(
            showgrid=False,
            ticks='outside',
            tickfont= dict(size=16)
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=30),
        margin=dict(t=60, b=40, l=100, r=40),
        height=height,
    )
    #LABELS INSIDE THE BARS
    fig.update_traces(
        texttemplate='%{x:,.0f} Tons',
        textposition='inside',
        insidetextanchor='start',
        textfont=dict(size=14, color="white")
    )
    st.plotly_chart(fig, use_container_width=True)

def pie_chart_commodity_distribution_imports(df_filtered, height=700):
    df_filtered = df_filtered[
        (df_filtered['Continent'].str.upper() == "NOT APPLICABLE") &
        (df_filtered['International Organization'].str.upper() == "NOT APPLICABLE") &
        (df_filtered['Country'].str.upper() != "WORLD TOTAL") 
    ]
    #Group by commodity and sum tons
    commodity_df = (
        df_filtered.groupby('Commodity', as_index=False)['Containerized Vessel Total Exports SWT (Tons)']
        .sum()
        .sort_values(by='Containerized Vessel Total Exports SWT (Tons)', ascending=False)
        .head(10)
    )

    fig = px.pie(
        commodity_df,
        names='Commodity',
        values='Containerized Vessel Total Exports SWT (Tons)',
        color_discrete_sequence=px.colors.sequential.Blues_r,
    )

    fig.update_traces(textposition='inside', textfont =dict (size = 16 ), textinfo='percent', hovertemplate='%{label}: %{value:,.0f} tons')

    fig.update_layout(
        showlegend=True,
        legend_title_text='Commodity',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.9,
            xanchor="left",
            x=1.05,
            font=dict(size=16),
            #bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1
        ),
        margin=dict(t=60, b=60, l=80, r=180),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig, use_container_width=False)

@st.cache_data(show_spinner="Generating annual trade volume chart...")
def bar_chart_by_year(df_filtered, flow_type, height=500):
    df_yearly = (
        df_filtered.groupby('Year', as_index=False)['Containerized Vessel Total Exports SWT (Tons)']
        .sum()
        .sort_values(by='Year', ascending=True)
    )

    fig = px.bar(
        df_yearly,
        x='Year',
        y='Containerized Vessel Total Exports SWT (Tons)',
        title='Annual Trade Volume Over Years',
        labels={'Year': 'Year', 'Containerized Vessel Total Exports SWT (Tons)': 'Total Weight (Tons)'},
        color='Containerized Vessel Total Exports SWT (Tons)',
        color_continuous_scale='Blues',
    )

    fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=df_yearly['Year'].min(),
            dtick=1,
            showgrid=True,
            ticks='outside',
            tickfont=dict(size=16),
            tickformat='.0f'
        ),
        yaxis=dict(
            showgrid=True,
            ticks='outside',
            tickfont=dict(size=16),
            tickformat='.2s'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=30),
        margin=dict(t=60, b=40, l=100, r=40),
        height=height,
        title=dict(
            text='Annual Maritime Trade Volume with Puerto Rico',
            font=dict(size=25, color="#FFFFFF", family='Century Gothic'),
            x=0.5,
            xanchor='center'
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

def continent_pie_chart(df_filtered, height=500):
    df_filtered = df_filtered[
        (df_filtered['Continent'].str.upper() != "NOT APPLICABLE") 
    ]
    #Group by commodity and sum tons
    continent_df = (
        df_filtered.groupby('Continent', as_index=False)['Containerized Vessel Total Exports SWT (Tons)']
        .sum()
        .sort_values(by='Containerized Vessel Total Exports SWT (Tons))', ascending=False)
        .head(10)
    )

    fig = px.pie(
        continent_df,
        names='Continent',
        values='Containerized Vessel Total Exports SWT (Tons)',
        title='Trade Volume by Continent',
        color_discrete_sequence=px.colors.sequential.Tealgrn,
    )

    fig.update_traces(textposition='inside', textfont = dict(size=16),textinfo='percent+label', hovertemplate='%{label}: %{value:,.0f} tons')

    fig.update_layout(
        showlegend=True,
        legend_title_text='Continent',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.8,
            xanchor="left",
            x=1,
            font=dict(size=18),
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=3
        ),

        margin=dict(t=60, b=40, l=40, r=150),
        title=dict(
            text='Trade Volume by Continent',
            font=dict(size=25, color='#0C0A09', family='Century Gothic'),
            x=0.5,
            xanchor='center'
        ),

    )
    st.plotly_chart(fig, use_container_width=True)
def generate_heat_map(filtered_data, access_token):
    puerto_rico_coords = [18.2208, -66.5901]  # Centro inicial
    
    m = folium.Map(
        location=puerto_rico_coords,
        zoom_start=3.5,
        tiles=f'https://tile.jawg.io/jawg-dark/{{z}}/{{x}}/{{y}}{{r}}.png?access-token={access_token}',
        attr='<a href="https://jawg.io" title="Tiles Courtesy of Jawg Maps" target="_blank">&copy; <b>Jawg</b>Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    )
    Fullscreen().add_to(m)

    if filtered_data.empty:
        return m

    # Agrupar datos
    flows = filtered_data.groupby(
        ['Country', 'Latitude_country', 'Longitude_country'],
        as_index=False
    ).agg({
        'Containerized Vessel Total Exports SWT (Tons)': 'sum'
    })

    # Preparar datos para heatmap [lat, lon, intensidad]
    heat_data = [
        [row['Latitude_country'], row['Longitude_country'], row['Containerized Vessel Total Exports SWT (Tons)']]
        for _, row in flows.iterrows()
        if not pd.isna(row['Latitude_country']) and not pd.isna(row['Longitude_country'])
    ]

    # Agregar capa heatmap
    HeatMap(
        heat_data,
        min_opacity=0.4,
        max_zoom=6,
        radius=25,
        blur=20,
        gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 0.8: 'red'}
    ).add_to(m)

    return m

@st.cache_data(show_spinner="Generating annual trade volume chart...")
def bar_chart_by_year(df_filtered, flow_type, height=500):
    df_yearly = (
        df_filtered.groupby('Year', as_index=False)['Containerized Vessel Total Exports SWT (Tons)']
        .sum()
        .sort_values(by='Year', ascending=True)
    )

    fig = px.bar(
        df_yearly,
        x='Year',
        y='Containerized Vessel Total Exports SWT (Tons)',
        title='Annual Trade Volume Over Years',
        labels={'Year': 'Year', 'Containerized Vessel Total Exports SWT (Tons)': 'Total Weight (Tons)'},
        color='Containerized Vessel Total Exports SWT (Tons)',
        color_continuous_scale='blues',
    )

    fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=df_yearly['Year'].min(),
            dtick=1,
            showgrid=True,
            ticks='outside',
            tickfont=dict(size=16),
            tickformat='.0f'
        ),
        yaxis=dict(
            showgrid=True,
            ticks='outside',
            tickfont=dict(size=16),
            tickformat='.2s'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=30),
        margin=dict(t=60, b=40, l=100, r=40),
        height=height,
        title=dict(
            text='Annual Maritime Trade Volume with Puerto Rico',
            font=dict(size=25, color="#FFFFFF", family='Century Gothic'),
            x=0.5,
            xanchor='center'
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

            
def init_dashboard(file_path: str):
    df_base = load_and_prepare_data(file_path)
    return filter_sidebar(df_base)   

dfi, df_filtered, sidebar_filters = init_dashboard("U.S International Trade - Imports and Exports.xlsx")
flow_type = sidebar_filters["Flow Type"]
year = sidebar_filters["Year"]
port = sidebar_filters["Port"]
metrics_international_trade(df_filtered, dfi, flow_type, year, port)

@st.cache_data
def render_ship_animation():
    with open(r"Flow map 2022.html", "r", encoding="utf-8") as f:
        html_data = f.read()

    styled_html = f"""
    <style>
        body {{background: transparent !important;
        }}
        html {{background: transparent !important;
        }}
        .folium-map {{background: transparent !important;
        }}
    </style>
    <div style="
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        border: 1px solid #ccc;
        width: 800px;
        height: 550px;
        margin: auto;
    ">
        {html_data}
    </div>
    """
    st.markdown("""
    <p style='font-size:25px;text-align:center; margin-bottom: 25px;margin-top: 25px; color:#FFFFFF; font-weight:700;'>
        Trade Flow Maritime Map (Domestic and International)
    </p>
    """, unsafe_allow_html=True)

    components.html(styled_html, height=570, width=920, scrolling=False)


col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    <p style='font-size:25px;text-align:center; margin-bottom: 10px; margin-top: 25px; color:#FFFFFF; font-weight:700;'>
       Top 10 Countries by Trade Flow (Tons)
    </p>
    """, unsafe_allow_html=True)
    top_trade_countries(df_filtered, year, flow_type, height=600)

with col2:
    render_ship_animation()

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    <p style='font-size:25px;text-align:center; margin-bottom: 10px; margin-top: 25px; color:#FFFFFF; font-weight:700;'>
       Top 10 Commodities by Trade Flow (Tons)
    </p>
    """, unsafe_allow_html=True)
    pie_chart_commodity_distribution_imports(df_filtered, flow_type)

with col2:
    st.markdown("---")
    bar_map = generate_heat_map(df_filtered, access_token)
    map_html = bar_map._repr_html_()
    styled_map = f"""
    <div style="
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #ccc;
    ">
        {map_html}
    </div>
    """
    st.components.v1.html(styled_map, height=570, width=950, scrolling=True)
    
bar_chart_by_year(df_filtered, flow_type, height=500)

    
def render_ship_animation_routes():
    with open("Interactive_ship_movements.html", "r", encoding="utf-8") as f:
        html_data = f.read()

    styled_html = f"""
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            background: transparent !important;
        }}
        .folium-map {{
            height: 100%;
            width: 100%;
            background: transparent !important;
        }}
    </style>
    <div style="
        width: 100%;
        height: 100%;
        border-radius: 25px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 2px solid #2c2f3e;
        align-items: center;
    ">
        {html_data}
    </div>
    """

    st.markdown("""
    <p style='font-size:25px;text-align:center; margin-bottom: 25px;margin-top: 25px; color:#FFFFFF; font-weight:700;'>
        Trade Flow Maritime Routes Animation - Puerto Rico
    </p>
    """, unsafe_allow_html=True)

    components.html(styled_html, height=900, width=1600, scrolling=False)

render_ship_animation_routes()