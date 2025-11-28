import streamlit as st
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
from folium.plugins import HeatMap,MarkerCluster, Fullscreen
import pydeck as pdk

placeholder = st.empty()


#NAVIGATION PAGE
    #[Set up the Streamlit app]
    #[Set up the page title]
    #[Load and prepare database]

# [Set up the Streamlit app]
st.set_page_config(layout="wide", page_title="International Trade with Puerto Rico ", initial_sidebar_state="expanded")
access_token = 'sgKt0HmG4TTVt9lXUCAjaLsSPLMoVN7CnA8LegyngahiKtMimaUg83TvgfROeUCe' #Access token jawg.io (MAP)

#[Set up the page title]
st.markdown(f"""
        <style>
        .block-container {{
            padding-top: 1rem;
        }} </style>
        <h1 style='display: flex; align-items: center;gap: 12px; margin-top: 10px;'> <img src='https://www.thiings.co/_next/image?url=https%3A%2F%2Flftz25oez4aqbxpq.public.blob.vercel-storage.com%2Fimage-KBUXl6AhDj2IsoZnozHL39yX1acqa5.png&w=320&q=75' width='85' style='margin-bottom: 4px;'/>
            International Trade with Puerto Rico 
            <span style='color:#c8c9d0; font-weight:normal;'> <h1> Air cargo </h1></span> </h1> """, unsafe_allow_html=True)

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
        
        tons_current = current_df['Air Total Weight (Tons)'].sum()
        tons_previous = previous_df['Air Total Weight (Tons)'].sum()

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
            top: 10;
            left: 0;
            width: 30px;
            height: 97%;
            background: linear-gradient(135deg, #3d7a4d 0%, #3d9a9a 100%);
            border-radius: 12px 0 0 12px;
        }
        .metric-label {
            font-size: 20px;
            font-weight: 700;
            color: #111111;
            margin-bottom: 10px;
            margin-top: 1px;
        }
                
        .metric-icon {
            font-size: 50px;
            margin-bottom: 1px;
        }

        .metric-value {
            font-size: 30px;
            font-weight: 800;
            color: #000000;
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
        color = "#388e3c" if delta_tons > 0 else "#C81010"
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
                <div class="metric-midtext" style="font-size:25px; color:#111111; margin-bottom:-5px;font-weight: 600;">{midtext}</div>
                <div class="metric-value">{value_formatted}</div>
                <div class="metric-delta">{delta}</div>
            </div>
        """, unsafe_allow_html=True)
    # Imports
    # Imports
    if year != "All":
        year = int(year)
        df_imports = dfi[
            (dfi['Year'] == year) &
            (dfi['Indicator'].str.strip().str.upper() == "IMPORTS") &
            (dfi['Continent'].str.upper() == "NOT APPLICABLE") &
            (dfi['International Organization'].str.strip().str.upper() == "NOT APPLICABLE") &
            (dfi['Country'].str.strip().str.upper() == "WORLD TOTAL")
        ]
        df_imports_prev = dfi[
            (dfi['Year'] == year - 1) &
            (dfi['Indicator'].str.strip().str.upper() == "IMPORTS") &
            (dfi['Continent'].str.upper() == "NOT APPLICABLE") &
            (dfi['International Organization'].str.strip().str.upper() == "NOT APPLICABLE") &
            (dfi['Country'].str.strip().str.upper() == "WORLD TOTAL")
        ]
    else:
        # Cuando year == "All", tomar todos los años
        df_imports = dfi[
            (dfi['Indicator'].str.strip().str.upper() == "IMPORTS") &
            (dfi['Country'].str.strip().str.upper() == "WORLD TOTAL")
        ]
        df_imports_prev = pd.DataFrame()

    import_tons = df_imports['Air Total Weight (Tons)'].sum()
    import_value = df_imports['Air Total Value ($US)'].sum()

    if not df_imports_prev.empty:
        import_tons_prev = df_imports_prev['Air Total Weight (Tons)'].sum()
        import_value_prev = df_imports_prev['Air Total  Value ($US)'].sum()
        import_delta_tons = format_delta(import_tons - import_tons_prev, ((import_tons - import_tons_prev) / import_tons_prev) * 100)
        import_delta_value = format_delta(import_value - import_value_prev, ((import_value - import_value_prev) / import_value_prev) * 100)
    else:
        import_delta_tons = format_delta(None, None)
        import_delta_value = format_delta(None, None)

    # Exports
    if year != "All":
        year = int(year)
        df_exports = dfi[
            (dfi['Year'] == year) &
            (dfi['Indicator'].str.strip().str.upper() == "EXPORTS") &
            (dfi['Continent'].str.upper() == "NOT APPLICABLE") &
            (dfi['International Organization'].str.strip().str.upper() == "NOT APPLICABLE")
        ]
        df_exports_prev = dfi[
            (dfi['Year'] == year - 1) &
            (dfi['Indicator'].str.strip().str.upper() == "EXPORTS") &
            (dfi['Continent'].str.upper() == "NOT APPLICABLE") &
            (dfi['International Organization'].str.strip().str.upper() == "NOT APPLICABLE")
        ]
    else:
        # Cuando year == "All", tomar todos los años
        df_exports = dfi[
            (dfi['Indicator'].str.strip().str.upper() == "EXPORTS") &
            (dfi['Continent'].str.upper() == "NOT APPLICABLE") &
            (dfi['International Organization'].str.strip().str.upper() == "NOT APPLICABLE")
        ]
        df_exports_prev = pd.DataFrame()

    export_tons = df_exports['Air Total Weight (Tons)'].sum()
    export_value = df_exports['Air Total Value ($US)'].sum()

    if not df_exports_prev.empty:
        export_tons_prev = df_exports_prev['Air Total Weight (Tons)'].sum()
        export_value_prev = df_exports_prev['Air Total  Value ($US)'].sum()
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
        df_international['Air Total Weight (Tons)'] = pd.to_numeric(df_international['Air Total Weight (Tons)'], errors='coerce')

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

        tons_current = current_df['Air Total Weight (Tons)'].sum()
        tons_previous = previous_df['Air Total Weight (Tons)'].sum()

        tons_value = current_df['Air Total  Value ($US)'].sum()
        tons_value_prev = previous_df['Air Total  Value ($US)'].sum()

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
            <h2 style='color:#000000; font-size:32px; font-weight:700; text-align:center; margin-bottom:-15px; margin-top: -15px;'>Imports</h2>
            <p style='font-size:20px; text-align:center; color: #000000;font-weight:600;'>Inbound air cargo arriving to Puerto Rico</p>
        </div>
    """, unsafe_allow_html=True)
        
        colimpor_value, colimpor_tons = st.columns([1,1])
        with colimpor_value:
            render_metric(
            label="Cumulative Import Value ($USD)",
            value=import_value,
            delta= import_delta_value, 
        )
        with colimpor_tons:
             render_metric(
            label="Cumulative Import Weight (Tons)",
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
        <h2 style='color:#111111; font-size:32px; font-weight:700; text-align: center; margin-bottom:-15px;margin-top: -15px;'>Exports</h2>
        <p style='font-size:20px;text-align:center; color:#0C0A09; font-weight:600;'>Outbound shipments departing from Puerto Rico</p>
        </div>
    """, unsafe_allow_html=True)

        col1, col2= st.columns([1,1])
        with col1:
            render_metric(
            label="Cumulative Export Value ($USD)",
            value=export_value,
            delta= export_delta_tons,  
        )

        with col2:
             render_metric(
            label="Cumulative Export Weight (Tons)",
            value=export_tons,
            delta= export_delta_tons, 
        )
             
def enhanced_kpi_cards(df_filtered, year):
    """Tarjetas KPI mejoradas"""

    # Normalizar nombres de columnas
    df_filtered = df_filtered.copy()
    df_filtered.columns = df_filtered.columns.str.strip().str.replace(r"\s+", " ", regex=True)

    # Calcular métricas
    total_countries = df_filtered['Country'].nunique()
    total_commodities = df_filtered['Commodity'].nunique()
    avg_shipment_value = df_filtered['Air Total Value ($US)'].mean()
    total_trade_volume = df_filtered['Air Total Weight (Tons)'].sum()
    
    # CSS para las tarjetas
    st.markdown("""
        <style>
        .kpi-card {
            background: linear-gradient(135deg, #3d7a4d 0%, #3d9a9a 100%);
            border-radius: 15px;
            padding: 10px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 10px;
            margin-top: -10px;
            height: 80px;
        }
        .kpi-value {
            font-size: 32px;
            font-weight: bold;
            margin: -10px 0;
        }
        .kpi-label {
            font-size: 16px;
            opacity: 0.9;
            font-weight: Bold;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Active Countries</div>
                <div class="kpi-value">{total_countries}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Commodities Traded</div>
                <div class="kpi-value">{total_commodities}</div>
            </div>
        """, unsafe_allow_html=True)
    
    #with col3:
       # st.markdown(f"""
        #    <div class="kpi-card">
         #       <div class="kpi-label">Avg Shipment Value</div>
          #      <div class="kpi-value">${avg_shipment_value:,.0f}</div>
           # </div>
        # """, unsafe_allow_html=True)
       
def calculate_arc_points(origin_coords: list, destination_coords: list, num_segments: int, curv_base: float) -> list:
    latitudes = np.linspace(origin_coords[0], destination_coords[0], num_segments, endpoint=True)
    longitudes = np.linspace(origin_coords[1], destination_coords[1], num_segments, endpoint=True)

    distance = np.sqrt((origin_coords[0] - destination_coords[0])**2 + (origin_coords[1] - destination_coords[1])**2)
    curvature_adjusted = curv_base + (distance * 0.1)
    curvature_adjusted = np.clip(curvature_adjusted, 0.5, 5)

    arc_points = []
    for j in range(num_segments):
        displacement = np.sin(np.pi * j / (num_segments - 1)) * curvature_adjusted
        delta_lat = destination_coords[0] - origin_coords[0]
        delta_lon = destination_coords[1] - origin_coords[1]
        perp_lat = -delta_lon
        perp_lon = delta_lat
        norm = np.sqrt(perp_lat**2 + perp_lon**2)
        if norm != 0:
            perp_lat /= norm
            perp_lon /= norm
        else:
            perp_lat, perp_lon = 0, 0
        arc_points.append([
            latitudes[j] + displacement * perp_lat,
            longitudes[j] + displacement * perp_lon
        ])

    arc_points[-1] = destination_coords
    return arc_points
placeholder = st.empty()
@st.cache_resource(show_spinner="Generating international trade map...")
def generate_international_trade_map(filtered_data):
    m = folium.Map(
        location=[18.2, -66.5],  # Puerto Rico center
        zoom_start=3.5,
        tiles=f'https://tile.jawg.io/jawg-dark/{{z}}/{{x}}/{{y}}{{r}}.png?access-token={access_token}',
        attr='<a href="https://jawg.io" title="Tiles Courtesy of Jawg Maps" target="_blank">&copy; <b>Jawg</b>Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors')
    Fullscreen().add_to(m)

    if filtered_data.empty:
        return m

    # Normalize columns
    filtered_data['Country'] = filtered_data['Country'].str.strip().str.upper()
    filtered_data['Indicator'] = filtered_data['Indicator'].str.strip().str.upper()
    filtered_data['Continent'] = filtered_data['Continent'].str.strip().str.upper()
    filtered_data['International Organization'] = filtered_data['International Organization'].str.strip().str.upper()

    # Coordinates for Puerto Rico
    puerto_rico_coords = [18.2, -66.5]

    # Group flows
    flows = filtered_data.groupby(
        ['Country', 'Latitude_country', 'Longitude_country', 'Indicator'],
        as_index=False
    ).agg({
        'Air Total Weight (Tons)': 'sum',
        'Air Total Value ($US)': 'sum'
    })

    for _, row in flows.iterrows():
        country = row['Country']
        lat = row['Latitude_country']
        lon = row['Longitude_country']
        indicator = row['Indicator']
        tons = row['Air Total Weight (Tons)']
        value = row['Air Total Value ($US)']

        if tons == 0 or pd.isna(tons):
            continue


        # Define origin and destination
        if indicator == "IMPORTS":
            origin_coords = [lat, lon]
            destination_coords = puerto_rico_coords
            color = "#ff9800"
        else:  # EXPORTS
            origin_coords = puerto_rico_coords
            destination_coords = [lat, lon]
            color = "#4caf50"

        # Calculate arc
        arc = calculate_arc_points(origin_coords, destination_coords, num_segments=12, curv_base=-20)

        # Line weight based on tons
        line_weight = np.log10(tons + 1) * 2.5
        line_weight = min(max(line_weight, 2), 12)

        # Add marker for country
        folium.CircleMarker(
            location=[lat, lon],
            radius=4,
            color='white',
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=f"{country}<br>{indicator.title()}<br>{tons:,.0f} tons<br>${value:,.0f}",
        ).add_to(m)

        if tons > 100000:
            dash_array = [2, 20]
            delay = 700
            pulse_color = "#ffe082"
        elif tons < 1000:
            dash_array = [1, 15]
            delay = 900
            pulse_color = "#fafafa"
        else:
            dash_array = [1, 10]
            delay = 800
            pulse_color = "white"

        # Add arc line
        AntPath(
            locations=arc,
            color=color,
            pulse_color=pulse_color,
            weight=line_weight,
            opacity=0.8,
            delay=delay,
            dash_array=dash_array,
            reverse=False,
            tooltip=f"{indicator.title()}: {country} ↔ Puerto Rico<br>{tons:,.0f} tons"
        ).add_to(m)

    return m

puerto_rico_coords = [18.2, -66.5]

def generate_heat_map(filtered_data, access_token):
    puerto_rico_coords = [18.2208, -66.5901]  # Centro inicial
    
    m = folium.Map(
        location=puerto_rico_coords,
        zoom_start=5.5,
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
        'Air Total Weight (Tons)': 'sum'
    })

    # Preparar datos para heatmap [lat, lon, intensidad]
    heat_data = [
        [row['Latitude_country'], row['Longitude_country'], row['Air Total Weight (Tons)']]
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

def choose_dtick(flow_type, year, max_value):
        if flow_type.upper() == "EXPORTS":
            if str(year).upper() == "ALL":
                return 1000
            else:
                return 200
        elif flow_type.upper() == "IMPORTS":
            if str(year).upper() == "ALL":
                return 2000
            else:
                return 500
        # fallback dinámico por si cambia el rango en el futuro
        return max(200, int(max_value / 10))

def top_trade_countries(df_filtered, year, flow_type, height=600):   
    df_filtered = df_filtered[
        (df_filtered['Continent'].str.upper() == "NOT APPLICABLE") &
        (df_filtered['International Organization'].str.upper() == "NOT APPLICABLE") &
        (df_filtered['Country'].str.upper() != "WORLD TOTAL") 
    ]
    
    #Group by country and sum
    top_trade_df = (
        df_filtered.groupby('Country', as_index=False)['Air Total Weight (Tons)']
        .sum()
        .sort_values(by='Air Total Weight (Tons)', ascending=True)
        .tail(10)
    )

    # Crear columna con ranking para el selectbox
    top_trade_df = top_trade_df.sort_values(by='Air Total Weight (Tons)', ascending=False).reset_index(drop=True)
    top_trade_df['Ranked Country'] = top_trade_df.apply(lambda x: f"{x.name + 1}. {x['Country']}", axis=1)

    #Create bar chart for top 10 countries (reordenar para el gráfico horizontal)
    top_trade_df_chart = top_trade_df.sort_values(by='Air Total Weight (Tons)', ascending=True)
    
    fig = px.bar(
        top_trade_df_chart,
        orientation='h',
        x='Air Total Weight (Tons)',
        y='Country',
        labels={'Country': 'Country', 'Air Total Weight (Tons)': 'Total Weight (Tons)'},
        color='Air Total Weight (Tons)',
        color_continuous_scale='Bluyl',
        opacity=0.80
    )
    fig.update_traces(marker_line_color = 'green', marker_line_width=1)

    # Elegir dtick según tipo y año
    max_value = top_trade_df['Air Total Weight (Tons)'].max()
    if flow_type.upper() == "EXPORTS":
        dtick = 1000 if str(year).upper() == "ALL" else 200
    elif flow_type.upper() == "IMPORTS":
        dtick = 2000 if str(year).upper() == "ALL" else 500
    else:
        dtick = max(200, int(max_value / 10))  # fallback dinámico

    fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=dtick, 
            showgrid=True,
            ticks='outside',
            tickfont=dict(size=16),
            tickformat='.1s'
        ),
        yaxis=dict(
            showgrid=False,
            ticks='outside',
            tickfont=dict(size=16)
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
    st.plotly_chart(fig, config={"responsive": True})

    # --- Selectbox debajo con ranking ---
    ranked_options = top_trade_df['Ranked Country'].tolist()
    selection = st.selectbox("Select a country to see its evolution:", ranked_options)

    # Checkbox para mostrar/ocultar el gráfico de evolución
    show_evolution = st.checkbox("Show country evolution chart", value=False)
    
    if show_evolution:
        # Obtener el nombre real del país (sin el número del ranking)
        country_selected = selection.split(". ", 1)[1]

        # --- Evolución temporal del país seleccionado ---
        df_country = df_filtered[df_filtered['Country'] == country_selected] \
            .groupby("Year", as_index=False)["Air Total Weight (Tons)"].sum()

        fig2 = px.line(
            df_country,
            x="Year",
            y="Air Total Weight (Tons)",
            markers=True,
            title=f"Evolution of {country_selected} ({flow_type.title()})",
            labels={"Air Total Weight (Tons)": "Total Weight (Tons)"}
        )

        fig2.update_traces(line=dict(width=3), marker=dict(size=8))
        fig2.update_layout(
            xaxis=dict(
                title=dict(
                    text="Year",
                    font=dict(size=16)  # ← ETIQUETA del eje X
                ),
                tickfont=dict(size=15)  # ← VALORES/NÚMEROS del eje X
            ),
            yaxis=dict(
                title=dict(
                    text="Weight (Tons)",
                    font=dict(size=16)  # ← ETIQUETA del eje Y
                ),
                tickformat=".1s",
                tickfont=dict(size=15)  # ← VALORES/NÚMEROS del eje Y
            ),
            title=dict(
                font=dict(size=18)  # ← TÍTULO del gráfico
            )
        )

        st.plotly_chart(fig2, config={"responsive": True})

def pie_chart_commodity_distribution_imports(df_filtered, height=500):
    df_filtered = df_filtered[
        (df_filtered['Continent'].str.upper() == "NOT APPLICABLE") &
        (df_filtered['International Organization'].str.upper() == "NOT APPLICABLE") &
        (df_filtered['Country'].str.upper() != "WORLD TOTAL") 
    ]
    #Group by commodity and sum tons
    commodity_df = (
        df_filtered.groupby('Commodity', as_index=False)['Air Total Weight (Tons)']
        .sum()
        .sort_values(by='Air Total Weight (Tons)', ascending=False)
        .head(10)
    )

    fig = px.pie(
        commodity_df,
        names='Commodity',
        values='Air Total Weight (Tons)',
        title=None,
        color_discrete_sequence=px.colors.sequential.Bluyl,
        opacity=0.75  # Mejor opción para pie charts
    )

    fig.update_traces(textposition='inside', textfont =dict (size = 16 ), textinfo='percent', hovertemplate='%{label}: %{value:,.0f} tons')

    fig.update_layout(
        paper_bgcolor="#1a1d2e",  # Fondo general
        plot_bgcolor="#1a1d2e",   # Fondo del área del gráfico
        font=dict(color="white"),
        showlegend=True,
        legend_title_text='Commodity Groups',
        legend=dict(
            title=dict(font=dict(size=22, color="white")),
            orientation="v",
            yanchor="top",
            y=0.9,
            xanchor="left",
            x=1.05,
            font=dict(size=18),
            borderwidth=1
        ),
        margin=dict(t=60, b=40, l=40, r=150),
       
    )

    st.plotly_chart(fig, use_container_width=False)

@st.cache_data(show_spinner="Generating annual trade volume chart...")
def bar_chart_by_year(df_filtered, flow_type, height=500):
    df_yearly = (
        df_filtered.groupby('Year', as_index=False)['Air Total Weight (Tons)']
        .sum()
        .sort_values(by='Year', ascending=True)
    )

    fig = px.bar(
        df_yearly,
        x='Year',
        y='Air Total Weight (Tons)',
        title=None,
        labels={'Year': 'Year', 'Air Total Weight (Tons)': 'Total Weight (Tons)'},
        color='Air Total Weight (Tons)',
        color_continuous_scale='Bluyl',
        opacity=0.80
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
        height=height
    )
    fig.update_traces(marker_line_color = 'white', marker_line_width=1)

    st.plotly_chart(fig, use_container_width=True)

def continent_pie_chart(df_filtered, height=500):
    df_filtered = df_filtered[
        (df_filtered['Continent'].str.upper() != "NOT APPLICABLE") 
    ]
    #Group by commodity and sum tons
    continent_df = (
        df_filtered.groupby('Continent', as_index=False)['Air Total Weight (Tons)']
        .sum()
        .sort_values(by='Air Total Weight (Tons)', ascending=False)
        .head(10)
    )

    fig = px.pie(
        continent_df,
        names='Continent',
        values='Air Total Weight (Tons)',
        title=None,
        color_discrete_sequence=px.colors.sequential.Bluyl
    )

    fig.update_traces(textposition='inside', textfont = dict(size=16),textinfo='percent+label', hovertemplate='%{label}: %{value:,.0f} tons')

    fig.update_layout(
        paper_bgcolor="#1a1d2e",  # Fondo general
        plot_bgcolor="#1a1d2e",   # Fondo del área del gráfico
        font=dict(color="white"),
        showlegend=True,
        legend_title_text='Continent',
        legend=dict(
            title=dict(font=dict(size=22, color="white")),
            orientation="v",
            yanchor="top",
            y=0.8,
            xanchor="left",
            x=1,
            font=dict(size=25),
            borderwidth=3
        ),
        margin=dict(t=60, b=40, l=40, r=150),

    )
    st.plotly_chart(fig, use_container_width=True)

def init_dashboard(file_path: str):
    df_base = load_and_prepare_data(file_path)
    return filter_sidebar(df_base)   

dfi, df_filtered, sidebar_filters = init_dashboard("https://docs.google.com/spreadsheets/d/1j5hoixO2ptOu5FT3E39eXDeogvS29y8O/export?format=xlsx")

flow_type = sidebar_filters["Flow Type"]
year = sidebar_filters["Year"]
port = sidebar_filters["Port"]
metrics_international_trade(df_filtered, dfi, flow_type, year, port)
enhanced_kpi_cards(df_filtered, year)
international_map = generate_international_trade_map(df_filtered)

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("""
        <p style='font-size:25px;text-align:center; margin-bottom: -40px; color:#FFFFFF; font-weight:700;'>Top 10 Countries by Air Trade Volume with Puerto Rico</p>
    """, unsafe_allow_html=True)
    top_trade_countries(df_filtered, year, flow_type, height=600)

    st.markdown("""
        <p style='font-size:25px;text-align:center; margin-bottom: -20px; color:#FFFFFF; font-weight:700;'>Top 10 Commodities by Air Trade Volume</p>
    """, unsafe_allow_html=True)
    pie_chart_commodity_distribution_imports(df_filtered, flow_type)

with col2:
    st.markdown("""
        <p style='font-size:25px;text-align:center; margin-bottom: -20px; color:#0C0A09; font-weight:700;'>International Trade Flow Map</p>
    """, unsafe_allow_html=True)

    map_html = international_map._repr_html_()
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
    st.markdown("""
        <p style='font-size:25px;text-align:center; margin-bottom: 35px;margin-top: -35px; color:#FFFFFF; font-weight:700;'>International Trade Flow Map by Tons</p>
    """, unsafe_allow_html=True)
    st.components.v1.html(styled_map, height=570, width=950, scrolling=True)


    st.markdown("""
        <p style='font-size:25px;text-align:center; margin-bottom: -20px; color:#FFFFFF; font-weight:700;'>Continent-Level Share of Air Trade</p>
    """, unsafe_allow_html=True)
    continent_pie_chart(df_filtered, flow_type)

st.markdown("""
    <p style='font-size:25px;text-align:center; margin-bottom: -20px; color:#FFFFFF; font-weight:700;'>
        International Trade with Puerto Rico per Year
    </p>
""", unsafe_allow_html=True)
bar_chart_by_year(df_filtered, flow_type, height=500)


bar_map = generate_heat_map(df_filtered, access_token)

# Mostrar título y mapa estilizado
st.markdown("---")


map_html = bar_map._repr_html_()
styled_map = f"""
<div style="
    border-radius: 40px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border: 1px solid #ccc;
">
    {map_html}
</div>
"""

st.components.v1.html(styled_map, height=700, width=1800, scrolling=True)

