import folium.plugins
from folium import plugins
import streamlit.components.v1 as components
from folium.plugins import AntPath
import pandas as pd
import numpy as np
import streamlit as st
import folium
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
from folium.plugins import Fullscreen
import base64
from streamlit_extras.metric_cards import style_metric_cards
from Load_data import load_and_prepare_data


#

placeholder = st.empty()
# Set up the Streamlit app #
st.set_page_config(layout="wide", page_title="U.S Domestic Trade with Puerto Rico ", initial_sidebar_state="expanded", 
                   page_icon="multiple_stop",)

st.markdown("""
<style>
    .main {
        background-color: #1a1d2e;
    }
    .stApp {
        background-color: #1a1d2e;
    }
    /* Cambiar color de texto principal */
    .stMarkdown, p, h1, h2, h3 {
        color: #e8eaed !important;
    }
</style>
""", unsafe_allow_html=True)

access_token = 'sgKt0HmG4TTVt9lXUCAjaLsSPLMoVN7CnA8LegyngahiKtMimaUg83TvgfROeUCe' #Access token jawg.io (MAP)

# File path
Domestic_Trade = "https://drive.google.com/uc?id=1IR94sMD0qB4fVJRWfFY8GmY6NMkYOBK3&export=download"

#_______________________________________________________________________________________________FOLIUM MAP VISUALIZATION
Folium_map = "Folium_trade_map.html"

#Calculate the arc point for the Ant Path
def calculate_arc_points(origin_coords: list, destination_coords:list, num_segments: int, curv_base: float)->list:
    latitudes = np.linspace(origin_coords[0], destination_coords[0], num_segments, endpoint=True)
    longitudes = np.linspace(origin_coords[1],destination_coords[1], num_segments, endpoint=True)
    
    #Adjust curvature based on distance between points
    distance = np.sqrt((origin_coords[0]-destination_coords[0])**2 + (origin_coords[1]-destination_coords[1])**2)
    curvature_adjusted = curv_base + (distance * 0.1)  
    curvature_adjusted = np.clip(curvature_adjusted, 0.5, 5) #reasonable limits for curvature

    arc_points = []
    for j in range(num_segments):
        # Use sine function to create a smooth arc
        displacement = np.sin(np.pi * j / (num_segments - 1)) * curvature_adjusted
        
        delta_lat = destination_coords[0] - origin_coords[0]
        delta_lon = destination_coords[1] - origin_coords[1]

        perp_lat = -delta_lon
        perp_lon = delta_lat

        nom_factor = np.sqrt(perp_lat**2 + perp_lon**2)
        if nom_factor != 0:
            perp_lat /= nom_factor
            perp_lon /= nom_factor
        else:
            perp_lat, perp_lon = 0, 0

        arc_points.append([
            latitudes[j] + displacement * perp_lat,
            longitudes[j] + displacement * perp_lon
        ])
    
    if arc_points:
        arc_points[-1] = destination_coords
    else:
        arc_points = [origin_coords, destination_coords]
    return arc_points
    
#________________________________________________________________________________________________GENERATE INTERACTIVE MAP
@st.cache_resource(show_spinner="Generating map...")
def generate_interactive_map(filtered_data):
    m = folium.Map(location=[35, -90], zoom_start=4.3, tiles=f'https://tile.jawg.io/jawg-dark/{{z}}/{{x}}/{{y}}{{r}}.png?access-token={access_token}',
                   attr='<a href="https://jawg.io" title="Tiles Courtesy of Jawg Maps" target="_blank">&copy; <b>Jawg</b>Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                   )
    Fullscreen().add_to(m)

    #Group data for flow summary
    flow_summary = filtered_data.groupby(['Origin', 'Destination', 'Indicator','Commodity Description']).agg(#, as_index=False).agg(  
        Total_tons = ('Air Shipping Weight (Tons)', 'sum'),
        Total_value = ('Air Value ($US)', 'sum'),
        Lat_origin = ('Lat_Origin', 'first'),
        Long_origin = ('Long_Origin','first'),
        Lat_dest = ('Lat_dest','first'),
        Long_dest = ('Long_dest','first')
).reset_index()
    
    #Collect all unique origins and destinations
    
    if not filtered_data.empty:
        # Origins and destinations for Imports
        imports = filtered_data[filtered_data['Indicator'] == 'Imports']
        if not imports.empty:
            origins_imports = imports[['Origin', 'Lat_Origin', 'Long_Origin']].drop_duplicates()
            destinations_imports = imports[['Destination', 'Lat_dest', 'Long_dest']].drop_duplicates()
            for _, row_o in origins_imports.iterrows():
                folium.CircleMarker(
                    location=[row_o['Lat_Origin'], row_o['Long_Origin']],
                    radius=3.5,
                    weight=1,
                    color='red',
                    fill=True,
                    fill_color='red',
                    popup=f"Origen: {row_o['Origin']} (Import)",
                ).add_to(m)
            for _, row_d in destinations_imports.iterrows():
                folium.CircleMarker(
                    location=[row_d['Lat_dest'], row_d['Long_dest']],
                    radius=3.5,
                    weight=1,
                    color='green',
                    fill=True,
                    fill_color='green',
                    popup=f"Destino: {row_d['Destination']} (Import)",
                ).add_to(m)
            
            grouped_imports = imports.groupby(
                ['Origin','Lat_Origin','Long_Origin','Destination','Lat_dest','Long_dest'],
                as_index=False
            ).agg({'Air Shipping Weight (Tons)':'sum'})

            for _, row in grouped_imports.iterrows():
                arc_points = calculate_arc_points(
                    [row['Lat_Origin'], row['Long_Origin']],
                    [row['Lat_dest'], row['Long_dest']],
                    num_segments=10,  
                    curv_base= -0      
                )

        # Origins and destinations for Exports
        exports = filtered_data[filtered_data['Indicator'] == 'Exports']
        if not exports.empty:
            origins_exports = exports[['Origin', 'Lat_Origin', 'Long_Origin']].drop_duplicates()
            destinations_exports = exports[['Destination', 'Lat_dest', 'Long_dest']].drop_duplicates()
            for _, row_o in origins_exports.iterrows():
                folium.CircleMarker(
                    location=[row_o['Lat_Origin'], row_o['Long_Origin']],
                    radius=3.5,
                    weight=1,
                    color='red',
                    fill=True,
                    fill_color='red',
                    popup=f"Origen: {row_o['Origin']} (Export)",
                ).add_to(m)
            for _, row_d in destinations_exports.iterrows():
                folium.CircleMarker(
                    location=[row_d['Lat_dest'], row_d['Long_dest']],
                    radius=3.5,
                    weight=1,
                    color='green',
                    fill=True,
                    fill_color='green',
                    popup=f"Destino: {row_d['Destination']} (Export)",
                ).add_to(m)


        #Unifided flows
        indicator_vals = filtered_data['Indicator'].unique()
        n_unique = len(indicator_vals)

        if n_unique == 1:
            mode = indicator_vals[0]
            color = '#3d9a9a' if mode=='Imports' else '#3d7a4d'  # Cyan para Imports, Verde para Exports
            df = filtered_data[filtered_data['Indicator']==mode]
        else:
            mode = 'All'
            color = '#4a9d5f'  # Verde CETL
            df = filtered_data
            df.to_pickle("processed_data.pkl") 

        flows = (
            df.groupby(
                ['Origin','Lat_Origin','Long_Origin',
                 'Destination','Lat_dest','Long_dest'],
                as_index=False
            )
            .agg(Total_tons=('Air Shipping Weight (Tons)','sum'))
        )

        for _, row in flows.iterrows():
            arc = calculate_arc_points(
                [row['Lat_Origin'],row['Long_Origin']],
                [row['Lat_dest'],  row['Long_dest']],
                num_segments=10,
                curv_base=-30
            )
            tons = row['Total_tons']
            line_weight = np.log10(tons + 1) * 3 # log scale smooths large range
            line_weight = min(max(line_weight,4 ), 15)  # cap between 1.5 and 8
            
            folium.plugins.AntPath(
                locations=arc,
                color=color,
                pulse_color='white',
                weight=line_weight,
                opacity=0.7,
                delay=500,
                dash_array='1, 20',
                tooltip=(
                  f"{mode}: {row['Origin']} → {row['Destination']}<br>"
                  f"Tons: {row['Total_tons']:,}"
                )
            ).add_to(m)
    #m.get_root().html.add_child(folium.Element(legend_html))
    return m  

def generate_bubble_map(filtered_data, flow_type):
    m = folium.Map(location=[35, -90], zoom_start=4.3, tiles=f'https://tile.jawg.io/jawg-dark/{{z}}/{{x}}/{{y}}{{r}}.png?access-token={access_token}',
                   attr='...')
    Fullscreen().add_to(m)

    
    group_col = "Origin" if flow_type == "Imports" else "Destination"
    lat_col = "Lat_Origin" if group_col == "Origin" else "Lat_dest"
    lon_col = "Long_Origin" if group_col == "Origin" else "Long_dest"

    bubble_df = (
        filtered_data.groupby([group_col, lat_col, lon_col])
        .agg({'Air Shipping Weight (Tons)': 'sum'})
        .reset_index()
    )

    for _, row in bubble_df.iterrows():
        folium.Circle(
            location=[row[lat_col], row[lon_col]],
            radius=np.log1p(row['Air Shipping Weight (Tons)']) * 35000,
            color="",
            fill=True,
            fill_color= "#681FEF",
            fill_opacity=0.6,
            tooltip=(
                f"{row[group_col]}<br>"
                f"{row['Air Shipping Weight (Tons)']:,.0f} tons"
            )
        ).add_to(m)

    return m

#_________________________________________________________________________________________________STREAMLIT APP LAYOUT
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()
logo_base64 = get_base64_image("assets/Images/Logos/CETL.png")

def main():
#[SIDEBAR FILTERS] Create a sidebar for filters 
    st.markdown("#")
    df = load_and_prepare_data(Domestic_Trade)#Load actual data
    years = df['Year'].unique().tolist() if 'Year' in df.columns else []
    years.sort(reverse=True)
    # SIDEFILTERS 
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center; margin-top:-15px; margin-bottom: 30px;'>
            <img src="data:image/png;base64,{logo_base64}" style="width:700px; border-radius:10px; box-shadow: 0 0px 0px rgba(0,0,0,0.1);">
        </div>
        """, unsafe_allow_html=True)

        st.header("Filters", width="stretch")
        selected_flow_type = st.selectbox("Select Flow Type", df['Indicator'].unique().tolist(), index=0)
        # The state filter depends on the selected flow
        if selected_flow_type == 'Imports':
            state_options = ['All'] + sorted(df[df['Indicator'] == 'Imports']['Origin'].unique().tolist())
        elif selected_flow_type == 'Exports':
            state_options = ['All'] + sorted(df[df['Indicator'] == 'Exports']['Destination'].unique().tolist())
        else:
            # All: display both
            state_options = ['All'] + sorted(list(set(df['Origin'].unique().tolist() + df['Destination'].unique().tolist())))
        selected_state_us = st.selectbox("Select U.S City", options=state_options, index=0)
        selected_year = st.selectbox("Select Year", years, index=0 if years else None)

        # Calculate the commodities depends on Indicator
        if selected_flow_type in ['Imports', 'Exports']:
            if selected_flow_type == 'Imports':
                temp_df = df[df['Indicator'] == 'Imports']
                if selected_state_us != 'All':
                    temp_df = temp_df[temp_df['Origin'] == selected_state_us]
            else:
                temp_df = df[df['Indicator'] == 'Exports']
                if selected_state_us != 'All':
                    temp_df = temp_df[temp_df['Destination'] == selected_state_us]
            commodities = sorted(temp_df['Commodity Description'].unique().tolist())
        else:
            # All: all commodities 
            if selected_state_us == 'All':
                commodities = sorted(df['Commodity Description'].unique().tolist())
            else:
                import_df = df[(df['Indicator'] == 'Imports') & (df['Origin'] == selected_state_us) & (df['Destination'] == 'Puerto Rico')]
                export_df = df[(df['Indicator'] == 'Exports') & (df['Destination'] == selected_state_us) & (df['Origin'] == 'Puerto Rico')]
                commodities = sorted(pd.concat([import_df, export_df])['Commodity Description'].unique().tolist())
        selected_commodity = st.selectbox("Select Commodity Group", options=['All'] + commodities, index=0) 
        
    years = df['Year'].unique().tolist() if 'Year' in df.columns else []
    years.sort(reverse=True)

    # Logic to filter the DataFrame based on user selections
    flow_type = selected_flow_type
    filtered_df = df.copy()
    if selected_year is not None:
        filtered_df = filtered_df[filtered_df['Year'] == selected_year]

    if flow_type != 'All':
        filtered_df = filtered_df[filtered_df['Indicator'] == flow_type]

    if selected_commodity != 'All':
        filtered_df = filtered_df[filtered_df['Commodity Description'] == selected_commodity]

    if selected_state_us != 'All':
        if flow_type == 'Imports':
            filtered_df = filtered_df[filtered_df['Origin'] == selected_state_us]
        elif flow_type == 'Exports':
            filtered_df = filtered_df[filtered_df['Destination'] == selected_state_us]
        else:
            import_df = filtered_df[filtered_df['Origin'] == selected_state_us].copy()
            export_df = filtered_df[filtered_df['Destination'] == selected_state_us].copy()
            filtered_df = pd.concat([import_df, export_df], ignore_index=True)
    
    filtered_df['Air Shipping Weight (Tons)'] = pd.to_numeric(filtered_df['Air Shipping Weight (Tons)'], errors='coerce')
    filtered_df['Air Value ($US)'] = pd.to_numeric(filtered_df['Air Value ($US)'].dropna().astype(str).str.replace(',', ''), errors='coerce')
    #st.dataframe(filtered_df)
    
# SET UP: _____________________________________________________________________________METRICS

    if not filtered_df.empty:
        #st.subheader("Key Performance Indicators ")
        previous_year = selected_year - 1

        if flow_type == "All":
            previous_filtered_df = df[df['Year'] == previous_year]
        else:
            previous_filtered_df = df[(df['Year'] == previous_year) & (df['Indicator'] == flow_type)]

        tons_current = filtered_df['Air Shipping Weight (Tons)'].sum()
        tons_previous = previous_filtered_df['Air Shipping Weight (Tons)'].sum()

        if tons_previous != 0:
            delta_tons = tons_current - tons_previous
            delta_percent = (delta_tons / tons_previous) * 100
            delta_text = f"{delta_tons:,.0f} tons ({delta_percent:.2f}%)"
        else:
            delta_text = "No data from previous year"

        value_current = pd.to_numeric(filtered_df['Air Value ($US)'], errors='coerce').sum()
        value_previous = pd.to_numeric(previous_filtered_df['Air Value ($US)'], errors='coerce').sum()

        # Delta
        delta_value = value_current - value_previous
        delta_value_percent = (delta_value / value_previous * 100) if value_previous else 0
        delta_value_text = f"{delta_value:,.0f} ({delta_value_percent:.1f}%)"

        total_tons = filtered_df['Air Shipping Weight (Tons)'].sum()
        total_value = filtered_df['Air Value ($US)'].sum()
        num_commodities = filtered_df['Commodity Description'].count()
        num_states_exports = filtered_df['Destination'].nunique()
        num_states_imports = filtered_df['Origin'].nunique()
        states_exports = filtered_df['Destination'].unique()
        states_imports = filtered_df['Origin'].unique()
        all_states = set(states_exports) | set(states_imports)
        num_total_cities = len(all_states)
     
        #Change the size and style font of metrics
        st.markdown("""
        <style>
        [data-testid="stMetricValue"] {
            font-size: 40px !important;
            font-weight: 900 !important;
            color: #11111 !important;
        }

        [data-testid="stMetricLabel"] p{
            font-size: 27px !important;
            font-weight: 500 !important;
            color: #11111;
        }
        [data-testid="stMetricDelta"] p{
            font-size: 50px !important;
            font-weight: 100 !important;    
        }
        </style>
        """, unsafe_allow_html=True)

        style_metric_cards(background_color="#41404090",border_left_color="#077736",box_shadow="0 0px 0px rgba(1,0,0,0.1)")
    
        #SET UP:________________________________________________________________________APP TITLE
        flow_label = flow_type if flow_type in ['Imports', 'Exports'] else 'Imports & Exports'
        st.markdown(f"""
        <style>
        .block-container {{
            padding-top: -20rem;
        }}
        </style>
        <h1 style='display: flex; align-items: center; gap: 12px; margin-top: -110px;margin-bottom: 1px;'>
            <img src='https://www.thiings.co/_next/image?url=https%3A%2F%2Flftz25oez4aqbxpq.public.blob.vercel-storage.com%2Fimage-vcc48r1OhJqfVn2ylxSxkKPdvfJ0BF.png&w=1000&q=75' width='80' style='margin-bottom: 4px;'/>
            U.S Domestic Trade with Puerto Rico - {flow_label} ({selected_year})
            <span style='color:#c8c9d0; font-weight:normal;'><h1> Air cargo</h1></span>
            </h1> 
        """, unsafe_allow_html=True)
        
        #CONTAINER METRICS________________________________________________________
       
        st.markdown("""<style>.block-container {padding-top: 0.5rem;} </style> """, unsafe_allow_html=True) #Display the title higher
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="Total Tons Shipped", value=f"{tons_current:,.0f} tons", delta=delta_text, delta_color='normal', border=True)
         
        with col2:
            st.metric(label="Total Value Shipped ($US)", value=f"${value_current:,.0f}", delta=delta_value_text, delta_color='normal', border=True)

        with col3:
            st.metric(label="No. of Commodities", value=f"{num_commodities:,.0f}", border=True, delta="-", delta_color="off")

        with col4:
            if flow_type=='Exports':
                st.metric(label="No. of U.S. Cities", value=f"{num_states_exports:,.0f}", border=True, delta="-",delta_color="off")
            elif flow_type=='Imports':
                st.metric(label="No. of U.S. Cities", value=f"{num_states_imports:,.0f}", border=True,delta="-",delta_color="off")
            else:
                st.metric(label="No. of U.S. Cities", value=f"{num_total_cities:,.0f}", border=True,delta="-",delta_color="off")

        #END METRICS_________________________________________________________

        #components.html(m.get_root().render(), height=600, width=1000)
        col_map, col_sankey = st.columns([1, 1])  # Adjust ratio as needed 🌍

        with col_map:
            # Aplicar estilos globales
            st.markdown("""
            <style>
            .map-title {
                color: #4a9d5f; 
                margin-bottom: -10px; 
                font-weight: 600;
                font-size: 24px;
                margin-top: -10px;
            }
            .map-subtitle {
                font-size: 14px; 
                color: #8b92b0; 
                margin: 0 0 15px 0;
            }
            
            .stfolium {
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                border: 2px solid rgba(61, 154, 154, 0.3);
                margin-top: 10px;
            }
            
            .stfolium iframe {
                border-radius: 15px !important;
                overflow: hidden;
            }
            
            .folium-map {
                border-radius: 15px !important;
                overflow: hidden;
            }
            
            /* Aplicar bordes redondeados al canvas del mapa */
            div[class*="leaflet-container"] {
                border-radius: 15px !important;
                overflow: hidden;
            }
            .stRadio {
                margin-bottom: 15px;
            }
            </style>
            """, unsafe_allow_html=True)
    
            # Selector del sidebar
            map_view = st.sidebar.radio(
                "Type of map visualization:", 
                ["Flow Map", "Bubble Map"],
                help="Choose between flow paths or bubble clusters"
            )
            
            # Usar un contenedor de Streamlit para mejor control
            with st.container():
                st.markdown('<div class="map-container">', unsafe_allow_html=True)
                st.markdown('<h3 class="map-title">🗺️ Domestic Trade Flow Map</h3>', unsafe_allow_html=True)
                
                # Generar el mapa según la selección
                if map_view == "Flow Map":
                    m = generate_interactive_map(filtered_df)
                else:
                    m = generate_bubble_map(filtered_df, flow_type)
                
                # Mostrar el mapa dentro del contenedor
                st_folium(m, width=860, height=400)
                
                st.markdown("</div>", unsafe_allow_html=True)
        #m = generate_interactive_map(filtered_df)
        #components.html(m.get_root().render(), height=400, width=850)

        #Display Sankey Diagram_______________________________________________SANKEY DIAGRAM
        with col_sankey:
            st.markdown("""
            <style>
            .sankey-container {
                background: rgba(45, 50, 80, 0.4);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                border: 1px solid rgba(139, 146, 176, 0.2);
                padding: 20px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                
            }
            </style>
            <div class="sankey-container">
                <h3 style='color: #e8eaed; margin-bottom: 5px;'>🔀 Top 15 Air Cargo Flows</h3>
                <p style='font-size: 14px; color: #8b92b0; margin: 0;'>by tons of shipments</p>
            </div>
            """, unsafe_allow_html=True)

            # Dynamic Filter
            if flow_type == "All":
                sankey_data = filtered_df[(filtered_df["Origin"] == "Puerto Rico") & (filtered_df["Destination"] != "Puerto Rico")].copy()
                focus_col = "Destination"
            elif flow_type == "Imports":
                sankey_data = filtered_df[filtered_df["Indicator"] == "Imports"].copy()
                focus_col = "Origin"
            else:
                sankey_data = filtered_df[filtered_df["Indicator"] == "Exports"].copy()
                focus_col = "Destination"

            # Group TOP 15 and calculate participation
            sankey_links = (sankey_data.groupby(['Origin', 'Destination'], as_index=False)
                .agg({'Air Shipping Weight (Tons)': 'sum'})
                .sort_values(by='Air Shipping Weight (Tons)', ascending=False).head(15))
            
            total_weight = sankey_links['Air Shipping Weight (Tons)'].sum()
            focus_percent = (sankey_links.groupby(focus_col)['Air Shipping Weight (Tons)'].sum()
                .apply(lambda x: f"{(x / total_weight) * 100:.1f}%").to_dict())
            
            # Build nodes
            nodes_raw = pd.Series(list(sankey_links['Origin']) + list(sankey_links['Destination'])).unique().tolist()
            nodes = [f"{n}  —  {focus_percent.get(n, '')}" if n in focus_percent else n for n in nodes_raw]
            node_indices = {nodes[i]: i for i in range(len(nodes))}
            
            # Node colors
            node_colors = ["#ec4899" if n == "Puerto Rico" else 
                        "#6366f1" if n in focus_percent and float(focus_percent[n].rstrip('%')) > 20 else
                        "#8b5cf6" if n in focus_percent and float(focus_percent[n].rstrip('%')) > 10 else
                        "#06b6d4" for n in nodes_raw]

            # Create Sankey
            fig = go.Figure(go.Sankey(
                node=dict(pad=15, thickness=20, label=nodes, color=node_colors, 
                        line=dict(color="rgba(139, 146, 176, 0.3)", width=1)),
                link=dict(
                    source=[node_indices[f"{o}  —  {focus_percent.get(o, '')}"] if o in focus_percent else node_indices[o] 
                            for o in sankey_links['Origin']],
                    target=[node_indices[f"{d}  —  {focus_percent.get(d, '')}"] if d in focus_percent else node_indices[d] 
                            for d in sankey_links['Destination']],
                    value=sankey_links['Air Shipping Weight (Tons)'],
                    color=["rgba(99, 102, 241, 0.4)" if v > sankey_links['Air Shipping Weight (Tons)'].median() 
                        else "rgba(16, 185, 129, 0.3)" for v in sankey_links['Air Shipping Weight (Tons)']]
                ),
                textfont=dict(color="#e8eaed", size=13)
            ))

            fig.update_layout(
                height=450, margin=dict(t=30, b=20, l=20, r=20),
                font=dict(size=14, color='#e8eaed'),
                plot_bgcolor='#1f2235', paper_bgcolor='#1f2235'
            )
            
            st.plotly_chart(fig, config={"responsive": True})

    col_left, col_right = st.columns([1,1])

    with col_right: #________________________________________________________________________YEARLY TRENDS - BARCHART  
        st.markdown("""
        <style>
        .element-container:has(.plot-container) {
            padding-top: 0px !important;
            margin-top: -20px !important;
        }
        /* Contenedor del gráfico con efecto glassmorphism */
        .chart-container {
            background: rgba(45, 50, 80, 0.4);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            border: 1px solid rgba(139, 146, 176, 0.2);
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="chart-container">
                <h3 style='color: #e8eaed; margin-bottom: 10px; font-weight: 600;'>
                    Imports and Exports Per Year
                </h3>
                <p style='font-size: 16px; color: #8b92b0; margin-top: -5px; margin-bottom: 20px;'>
                    by tons of shipments
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        year_data = (
            df.groupby(['Year','Indicator'])['Air Shipping Weight (Tons)']
            .sum()
            .reset_index()
            .sort_values(['Indicator','Year'])
        )
        year_data['% var.'] =(
            year_data.groupby('Indicator')['Air Shipping Weight (Tons)']
            .pct_change()
            .fillna(0)*100
        )
        pivot_df = year_data.pivot(index='Year', columns='Indicator', values='Air Shipping Weight (Tons)').fillna(0)
        pivot_df = pivot_df.reset_index() 

        pivot_df['Total'] = pivot_df['Imports'] + pivot_df['Exports']
        pivot_df['Line'] = pivot_df['Total'].rolling(2).mean()
        pivot_df['Variation'] = pivot_df['Total'].pct_change().fillna(0)

        fig = go.Figure()
        
       
        import_colors = ["#3779b4"] * len(pivot_df) 
        import_colors[-1] = "#8b5cf6"  
        export_colors = ["#10b981"] * len(pivot_df) 
        export_colors[-1] = "#34d399"
        
        fig.add_trace(go.Bar(
            x=pivot_df['Year'], 
            y=pivot_df['Exports'], 
            name='Exports', 
            marker_color=export_colors,
            marker_line_color='rgba(16, 185, 129, 0.5)',
            marker_line_width=2
        ))
        
        fig.add_trace(go.Bar(
            x=pivot_df['Year'], 
            y=pivot_df['Imports'], 
            name='Imports', 
            marker_color=import_colors,
            marker_line_color='rgba(99, 102, 241, 0.5)',
            marker_line_width=2
        ))
        
        #
        fig.add_trace(go.Scatter(
            x=pivot_df['Year'],
            y=pivot_df['Imports'],
            name='Trend Imports',
            mode='lines+markers',
            line=dict(color="#ec4899", width=3, dash='solid'),
            marker=dict(size=8, symbol='circle')
        ))
        
        fig.add_trace(go.Scatter(
            x=pivot_df['Year'],
            y=pivot_df['Exports'],
            name='Trend Exports',
            mode='lines+markers',
            line=dict(color="#06b6d4", width=3, dash='solid'),
            marker=dict(size=8, symbol='circle')
        ))
        
        variation_df = (year_data.pivot(index='Year', columns='Indicator', values='% var.').reset_index())
        for i, row in variation_df.iterrows():
            if i == 0:
                continue
            
            # anotations for Imports
            fig.add_annotation(
                x=row['Year'],
                y=pivot_df.loc[i, 'Imports'] + 0.04 * pivot_df['Total'].max(),
                text=f"↑ {row['Imports']:.1f}%" if row['Imports'] > 0 else f"↓ {abs(row['Imports']):.1f}%",
                showarrow=False,
                font=dict(
                    color="#10b981" if row['Imports'] > 0 else "#ef4444",
                    size=13,
                    family="Arial, sans-serif",
                    weight=600
                ),
                bgcolor="rgba(31, 35, 53, 0.8)",
                bordercolor="#8b92b0",
                borderwidth=1,
                borderpad=4
            )
            
            #Anotations for exports
            fig.add_annotation(
                x=row['Year'],
                y=pivot_df.loc[i, 'Exports'] + 0.05 * pivot_df['Total'].max(),
                text=f"↑ {row['Exports']:.1f}%" if row['Exports'] > 0 else f"↓ {abs(row['Exports']):.1f}%",
                showarrow=False,
                font=dict(
                    color="#10b981" if row['Exports'] > 0 else "#ef4444",
                    size=13,
                    family="Arial, sans-serif",
                    weight=600
                ),
                bgcolor="rgba(31, 35, 53, 0.8)",
                bordercolor="#8b92b0",
                borderwidth=1,
                borderpad=4
            )
        
        fig.update_layout(
            barmode='group',
            title="",
            yaxis_title='Tons',
            xaxis_title='Year',
            height=620,
            width=450,
            hovermode='x unified',
            margin=dict(t=40, b=30, l=20, r=20),
            # Estilo dark mode
            plot_bgcolor='#1f2235',
            paper_bgcolor='#1f2235',
            font=dict(color='#e8eaed', size=14, family="Arial, sans-serif"),
            xaxis=dict(
                gridcolor='rgba(139, 146, 176, 0.15)',
                zerolinecolor='rgba(139, 146, 176, 0.2)',
                tickfont=dict(color='#8b92b0', size=16)
            ),
            yaxis=dict(
                gridcolor='rgba(139, 146, 176, 0.15)',
                zerolinecolor='rgba(139, 146, 176, 0.2)',
                tickfont=dict(color='#8b92b0', size=16),
                title_font=dict(color='#e8eaed', size=16)
            ),
            legend=dict(
                bgcolor='rgba(45, 50, 80, 0.8)',
                bordercolor='#8b92b0',
                borderwidth=1,
                font=dict(color='#e8eaed', size=12)
            ),
            hoverlabel=dict(
                bgcolor='#2d3250',
                font_size=13,
                font_color='#e8eaed',
                bordercolor='#8b92b0'
            )
        )
        
        fig.update_xaxes(
            tickmode='array',
            tickvals=df['Year'].unique(),  
            ticktext=df['Year'].unique()
        )
        
        st.plotly_chart(fig, config={"responsive": True})

#_________________________________________________________________________TREEMAP - COMMODITIES
    with col_left:
        st.markdown("""
        <style>
        .treemap-container {
            background: rgba(45, 50, 80, 0.4);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            border: 1px solid rgba(139, 146, 176, 0.2);
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        </style>
        <div class="treemap-container">
            <h3 style='color: #e8eaed; margin-bottom: 5px;'>Key Commodities - Trade with U.S States</h3>
            
        </div>
        """, unsafe_allow_html=True)
        #<p style='font-size: 14px; color: #8b92b0; margin: 0;'>by tons of shipments</p>

        if not filtered_df['Commodity Description'].isnull().all():
            with st.expander("⚙️Adjust grouping threshold", expanded=False):
                threshold = st.slider("Group under 'Others' if below:", 
                    min_value=0.01, max_value=0.035, value=0.010, step=0.001, format="%0.3f")

            # Process data
            grouped = filtered_df.groupby("Commodity Description", as_index=False)['Air Shipping Weight (Tons)'].sum()
            total = grouped["Air Shipping Weight (Tons)"].sum()
            grouped["Proportion"] = grouped["Air Shipping Weight (Tons)"] / total
            grouped["Cleaned Category"] = grouped.apply(
                lambda row: row["Commodity Description"] if row["Proportion"] >= threshold else "others", axis=1)
            
            treemap_data = grouped.groupby("Cleaned Category", as_index=False)["Air Shipping Weight (Tons)"].sum()
            treemap_data["Participation (%)"] = (treemap_data["Air Shipping Weight (Tons)"] / treemap_data["Air Shipping Weight (Tons)"].sum()) * 100
            treemap_data = treemap_data.sort_values(by="Participation (%)", ascending=False)
            
            # Move 'others' to end
            if "others" in treemap_data["Cleaned Category"].values:
                others = treemap_data[treemap_data["Cleaned Category"] == "others"]
                treemap_data = pd.concat([treemap_data[treemap_data["Cleaned Category"] != "others"], others], ignore_index=True)

            # Create treemap with modern colors
            fig = px.treemap(treemap_data, path=['Cleaned Category'], values='Air Shipping Weight (Tons)',
                color='Participation (%)', 
                color_continuous_scale=[[0, "#a9ebfb"], [0.3, "#889bf2"], [0.6, "#466fd8"], [1, "#664EC5"]],
                custom_data=['Cleaned Category', 'Air Shipping Weight (Tons)', 'Participation (%)'])
            
            fig.update_layout(
                width=880, height=500, margin=dict(t=5, b=5, l=5, r=5),
                plot_bgcolor='#1f2235', paper_bgcolor='#1f2235',
                font=dict(color='#e8eaed', size=14)
            )
            
            fig.update_traces(
                texttemplate='<b>%{label}</b><br>%{value:,.0f} tons<br><b>%{customdata[2]:.1f}%</b>',
                textfont=dict(size=16, color='#ffffff', family='Arial'),
                hovertemplate='<b>%{customdata[0]}</b><br>Weight: %{customdata[1]:,.0f} tons<br>Share: %{customdata[2]:.2f}%<extra></extra>',
                marker=dict(line=dict(color='rgba(139, 146, 176, 0.3)', width=2))
            )
            
            st.plotly_chart(fig, config={"responsive": True})
        else:
            st.info("📭 No commodity data available for the selected filters.")
    
        st.markdown("""
            <p style='font-size: 12px; color: #8b92b0; margin-top: 10px; font-style: italic;'>
            💡 Commodity classification based on first 2-digits (Chapters) of Schedule B system, 
            administered by Census Bureau's Foreign Trade Division.
            </p>
        """, unsafe_allow_html=True)
        
    

if __name__ == "__main__":
    main()


