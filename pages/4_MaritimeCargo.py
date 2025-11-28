import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import folium.plugins
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
import base64
from components_international import continent_card
import pycountry 
from streamlit_folium import st_folium
from folium.plugins import Fullscreen
from folium.plugins import AntPath

access_token = 'sgKt0HmG4TTVt9lXUCAjaLsSPLMoVN7CnA8LegyngahiKtMimaUg83TvgfROeUCe' #Access token jawg.io (MAP)


#[Set up the page title]
st.markdown(f"""
        <style>
        .block-container {{
            padding-top: 1rem;
        }} </style>
        <h1 style='display: flex; align-items: center;gap: 12px; margin-top: 10px;'> <img src='https://www.thiings.co/_next/image?url=https%3A%2F%2Flftz25oez4aqbxpq.public.blob.vercel-storage.com%2Fimage-X7dat6FnLoK14tvhi0ecr3pgW3GHAe.png&w=1000&q=75' width='85' style='margin-bottom: 4px;'/>
            Domestic Trade with Puerto Rico 
            <span style='color:#c8c9d0; font-weight:normal;'> <h1> Maritime cargo </h1></span> </h1> """, unsafe_allow_html=True)

def render_ship_animation():
    with open(r"C:\Users\WENDYPULIDO-VALENCIA\Wendy UPRM\Visualization\Interactive_ship_movements.html", "r", encoding="utf-8") as f:
        html_data = f.read()
    components.html(html_data, height=800, width=1300, scrolling=True)

col1, col2 = st.columns([1, 2])

with col2:
    if "ship_animation_loaded" not in st.session_state:
        st.session_state.ship_animation_loaded = False

    if not st.session_state.ship_animation_loaded:
        render_ship_animation()
        st.session_state.ship_animation_loaded = True
    else:
        st.markdown("✅")

with col1:
    if st.button("Render"):
        st.session_state.ship_animation_loaded = False

international_trade ="https://docs.google.com/spreadsheets/d/1j5hoixO2ptOu5FT3E39eXDeogvS29y8O/export?format=xlsx" #File Path
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
    
    #if select_country != 'All':
     #   filtered_data = filtered_data[filtered_data['Country'] == select_country] if select_country != 'All' else filtered_data
    
    #if select_international_organization != 'All':
     #   filtered_data = filtered_data[filtered_data['International Organization'] == select_international_organization] if select_international_organization != 'All' else filtered_data
    
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
