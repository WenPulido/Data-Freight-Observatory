import streamlit as st
import pandas as pd
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards
from Load_data import initialize_trade_data
from Load_data import initialize_international_data
import plotly.express as px

placeholder = st.empty()

# [Set up the Streamlit app]
st.set_page_config(layout="wide", page_title="International Trade with Puerto Rico ", initial_sidebar_state="expanded")

#Load data from domestic dashboard
initialize_trade_data()
df_domestic = st.session_state.df_domestic

#Data cleaning for international data
initialize_international_data()
df_international = st.session_state.df_international
df_international['Continent'] = df_international['Continent'].str.strip().str.upper()
df_international['Indicator'] = df_international['Indicator'].str.strip().str.upper()
df_international['International Organization'] = df_international['International Organization'].str.strip().str.upper()
df_international['Country'] = df_international['Country'].str.strip().str.upper()

#Set up year filter______________________________________
def filter_year(df):
    with st.container():
        col1, col2 = st.columns([3,1])

        with col1:
            st.markdown(f"""
                <style>
                .block-container {{
                    padding-top: 1rem;
                }} </style>
                <h1 style='display: flex; align-items: center;gap: 12px; margin-top: 10px;'> <img src='https://www.thiings.co/_next/image?url=https%3A%2F%2Flftz25oez4aqbxpq.public.blob.vercel-storage.com%2Fimage-Uo5uTZaadWp8wZpXudoa6MF8a5q6VH.png&w=1000&q=75' width='85' style='margin-bottom: 4px;'/>
                    Overview of Logistics and Trade in Puerto Rico
                    <span style='color:#c8c9d0; font-weight:normal;'> <h1> Air cargo </h1></span> </h1> """, unsafe_allow_html=True)


        with col2:
            with st.container():
                col1, col2 = st.columns([2,1])  

                with col2:
                    st.markdown("<div style='margin-top:30px; margin-bottom:-40px; text-align: center;'>Select Year</div>", unsafe_allow_html=True)
                    years = ['All'] + sorted(df['Year'].dropna().unique().tolist(), reverse=True)
                    select_year = st.selectbox("", years, index=0)
          
    filtered_data = df.copy()
    selected_year_int = None

    if select_year != 'All':
        filtered_data = filtered_data[filtered_data['Year'] == select_year]
        selected_year_int = int(select_year)

    filters = {"Year" : select_year}
    #st.write(filtered_data.head(10))
    return filters, filtered_data, selected_year_int

def sunburst_trade(df_domestic, df_international, selected_year_int):
    #Define data based on year selection
    if selected_year_int is None:
        df_dom = df_domestic.copy()
        df_int = df_international.copy()
    else:
        df_dom = df_domestic[df_domestic['Year'] == selected_year_int].copy()
        df_int = df_international[df_international['Year'] == selected_year_int].copy()

    #Domestic trade data 
    imports_us = df_dom[df_dom['Destination'] == "PUERTO RICO"]['Air Shipping Weight (Tons)'].sum()
    exports_us = df_dom[df_dom['Origin'] == "PUERTO RICO"]['Air Shipping Weight (Tons)'].sum()

    #International trade data
    imports_foreign = df_int[
        (df_int['Continent'] != "NOT APPLICABLE") &
        (df_int['Indicator'].str.strip().str.upper() == "IMPORTS")
    ]['Air Total Weight (Tons)'].sum()

    exports_foreign = df_int[
        (df_int['Continent'] != "NOT APPLICABLE") &
        (df_int['Indicator'].str.strip().str.upper() == "EXPORTS")
    ]['Air Total Weight (Tons)'].sum()

    #Hierarchical data for sunburst
    data = pd.DataFrame({
        "Category": ["Total Domestic", "Total Domestic", "Total Foreign", "Total Foreign"],
        "Subcategory": ["Domestic Imports", "Domestic Exports", "Foreign Imports", "Foreign Exports"],
        "Value": [imports_us, exports_us, imports_foreign, exports_foreign]
    })

    #Calculate percentages for sunburst
    total = data["Value"].sum()
    data["Percentage"] = (data["Value"] / total) * 100

    #Suburst chart for share of imports and exports
    fig = px.sunburst(
        data,
        path=['Category', 'Subcategory'],
        values='Percentage',
        color='Category',
        color_discrete_sequence=px.colors.qualitative.Bold #every color is different to distinguish them easily
    )
    fig.update_traces(
        insidetextorientation='tangential',
        texttemplate="<b>%{label}</b><br><b>%{percentParent:.1%}</b>",
        textfont=dict(size=18, color='#ffffff', family='Arial'),
        marker=dict(
            line=dict(
                color='#1a1d2e', 
                width=0.5     
            )
        )
    )

    #Adjust layout 
    fig.update_layout(
        height=800,
        width=650,
        margin=dict(t=10, l=10, r=0, b=30),  # t = espacio arriba
        coloraxis_showscale=False,
        paper_bgcolor='rgba(0,0,0,0)' # Fondo transparente
    )
    st.markdown("""
    <style>
    .my-chart-title {
        text-align: center;
        font-size: 28px;
        font-family: Arial, sans-serif;
        color: white;
        margin-top: 40px;    
        margin-bottom: -25px; 
        font-weight: bold !important;
    }
    .chart-wrapper {
        display: flex;
        justify-content: center;
    }
    .chart-wrapper > div[data-testid="stPlotlyChart"] > div {
        width: 800px !important;
        height: 800px !important;
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    #Render title and chart independently 
    st.markdown('<div class="my-chart-title">Share of Imports and Exports: Domestic vs. Foreign</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
    fig.update_layout(
        title_text=None,
        margin=dict(t=10, l=0, r=20, b=0),
        height=750,
        width=750
    )

    st.plotly_chart(
        fig,
        config={"responsive": True}
    )
    st.markdown('</div>', unsafe_allow_html=True)
 
def metrics_overview(filtered_data, filters, selected_year_int, df_domestic):
    
    st.markdown("""
        <style>
        .metric-box {
            background-color: #eef2f7;
            border-radius: 12px;
            padding: 20px;
            height: 400px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            margin-bottom: 20px;
            border-left: 30px solid transparent;
            padding-left: 12px; 
            margin-top: 40px;
        }
        .metric-box::before {
            content: "";
            position: absolute;
            top: 10;
            left: 0;
            width: 45px;
            height: 90.5%;
            background: linear-gradient(135deg, #3d7a4d 0%, #3d9a9a 100%);
            border-radius: 12px 0 0 12px;
        }
        .metric-label {
            font-size: 35px;
            font-weight: 700;
            color: #333;
            margin-bottom: 10px;
            margin-top: 5px;
        }
                
        .metric-icon {
            font-size: 50px;
            margin-bottom: 1px;
        }

        .metric-value {
            font-size: 36px;
            font-weight: 800;
            color: #111;
            margin-top: -10px;
        }

        .metric-delta {
            font-size: 30px;
            font-weight: 500;
            color: #2e7d32;
            margin-top: -10px;
        }
        .metric-subtext {
            font-size: 15px;
            color: #333;
            margin-top: -10px;
            font-weight: 500;
        }
     
        </style>
    """, unsafe_allow_html=True)

    def compute_delta(df, select_year, origin=None, destination=None):
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        if select_year is None:
            return None, None
        previous_year = select_year - 1
        current_df = df[(df['Year'] == select_year)]
        previous_df = df[(df['Year'] == previous_year)]
        

        if origin:
            current_df = current_df[current_df['Origin'] == "PUERTO RICO"]
            previous_df = previous_df[previous_df['Origin'] == "PUERTO RICO"]
            

        if destination:
            current_df = current_df[current_df['Destination'] == "PUERTO RICO"]
            previous_df = previous_df[previous_df['Destination'] == "PUERTO RICO"]


        tons_current = current_df['Air Shipping Weight (Tons)'].sum()
        tons_previous = previous_df['Air Shipping Weight (Tons)'].sum()

        if tons_previous != 0:
            delta_tons = tons_current - tons_previous
            delta_percent = (delta_tons / tons_previous) * 100
            return delta_tons, delta_percent
        else:
            return None, None
            
            
    def format_delta(delta_tons, delta_percent):
        if delta_tons is None:
            return "<span style='color:#9E9E9E'>No data from previous year</span>"
        arrow = "↑" if delta_tons > 0 else "↓"
        color = "#388e3c" if delta_tons > 0 else "#d32f2f"
        return f"<span style='color:{color}'>{arrow} {delta_tons:,.0f} tons ({delta_percent:.2f}%)</span>"

    def compute_delta_international(df_international, select_year, indicator):
        df_international['Year'] = pd.to_numeric(df_international['Year'], errors='coerce')
        df_international['Port'] = df_international['Port'].str.strip().str.upper()
        df_international['Continent'] = df_international['Continent'].str.strip().str.upper()
        df_international['International Organization'] = df_international['International Organization'].str.strip().str.upper()
        df_international['Indicator'] = df_international['Indicator'].str.strip().str.upper()
        df_international['Country'] = df_international['Country'].str.strip().str.upper()
        df_international['Air Total Weight (Tons)'] = pd.to_numeric(df_international['Air Total Weight (Tons)'], errors='coerce')

        if select_year is None:
            return None, None

        previous_year = select_year - 1

        base_filter = (
            (df_international['Continent'] == "NOT APPLICABLE") &
            (df_international['International Organization'] == "NOT APPLICABLE") &
            (df_international['Indicator'] == indicator.upper()) 
        )

        if indicator.upper() == "IMPORTS":
            base_filter &= (df_international['Country'] == "WORLD TOTAL")

        current_df = df_international[(df_international['Year'] == select_year) & base_filter]
        previous_df = df_international[(df_international['Year'] == previous_year) & base_filter]

        tons_current = current_df['Air Total Weight (Tons)'].sum()
        tons_previous = previous_df['Air Total Weight (Tons)'].sum()

        if tons_previous != 0:
            delta_tons = tons_current - tons_previous
            delta_percent = (delta_tons / tons_previous) * 100
            return delta_tons, delta_percent
        else:
            return None, None
        
    def format_delta(delta_tons, delta_percent):
        if delta_tons is None:
            return "<span style='color:#9E9E9E'>No data from previous year</span>"
        arrow = "↑" if delta_tons > 0 else "↓"
        color = "#388e3c" if delta_tons > 0 else "#d32f2f"
        return f"<span style='color:{color}'>{arrow} {delta_tons:,.0f} tons ({delta_percent:.2f}%)</span>"



    # Función para renderizar una métrica
    def render_metric(icon, label, value, delta, subtext, midtext=""):
        if icon.startswith("http"):
            icon_html = f'<img src="{icon}" alt="icon" style="width:150px; height: 130px; margin-bottom:10px;" />'
        else:
            icon_html = f'<div class="metric-icon">{icon}</div>'

        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">{label}</div>
                {icon_html}
                <div class="metric-midtext" style="font-size:25px; color:#9E9E9E; margin-bottom:-5px;font-weight: 600;">{midtext}</div>
                <div class="metric-value">{value:,.0f} tons </div>
                <div class="metric-delta">{delta}</div>
                <div class="metric-subtext">{subtext}</div>
            </div>
        """, unsafe_allow_html=True)
    

    #Metrics for domestic trade 
    df_imports_us = filtered_data[(filtered_data['Destination'] == "PUERTO RICO")]
    total_import_tons = df_imports_us["Air Shipping Weight (Tons)"].sum()  
    delta_tons, delta_percent = compute_delta(df_domestic, selected_year_int, destination="PUERTO RICO")
    delta_imports_us = format_delta(delta_tons, delta_percent)

    df_exports_us = filtered_data[(filtered_data['Origin'] == "PUERTO RICO")]
    total_exports_tons = df_exports_us["Air Shipping Weight (Tons)"].sum()
    delta_tons, delta_percent = compute_delta(df_domestic, selected_year_int, origin="PUERTO RICO")
    delta_exports_us = format_delta(delta_tons, delta_percent)

    #Metrics for international trade
    # Total internacional - Imports
    if selected_year_int is None:
        df_imports_other = df_international[
            (df_international['Indicator'].str.strip().str.upper() == "IMPORTS") &
            #(df_international['Continent'] != "NOT APPLICABLE") &
            (df_international['Country'] == "WORLD TOTAL") 
            
        ]
    else:
        df_imports_other = df_international[
            (df_international['Year'] == selected_year_int) &
            (df_international['Indicator'].str.strip().str.upper() == "IMPORTS") &
            (df_international['Continent'] == "NOT APPLICABLE") &
            (df_international['International Organization'] == "NOT APPLICABLE") &
            (df_international['Country'] == "WORLD TOTAL") 
            
        ]
    total_import_other_tons = df_imports_other['Air Total Weight (Tons)'].sum()
    #st.write(df_imports_other.head(10))
   
    # Total internacional - Exports
    if selected_year_int is None:
        df_exports_other = df_international[
            (df_international['Indicator'].str.strip().str.upper() == "EXPORTS") &
            (df_international['Continent'] == "NOT APPLICABLE") &
            (df_international['International Organization'] == "NOT APPLICABLE") 
        ]
    else:
        df_exports_other = df_international[
            (df_international['Year'] == selected_year_int) &
            (df_international['Continent'] == "NOT APPLICABLE") &
            (df_international['International Organization']== "NOT APPLICABLE") &
            (df_international['Indicator'].str.strip().str.upper() == "EXPORTS")
        ]

    total_exports_other_tons = df_exports_other['Air Total Weight (Tons)'].sum()
    #st.write(df_exports_other.head(2))

    if selected_year_int is None:
        delta_imports_other = "<span style='color:#9E9E9E'>Total accumulated</span>"
        delta_exports_other = "<span style='color:#9E9E9E'>Total accumulated</span>"
    else:
        delta_tons, delta_percent = compute_delta_international(df_international, selected_year_int, indicator="IMPORTS")
        delta_imports_other = format_delta(delta_tons, delta_percent)

        delta_tons, delta_percent = compute_delta_international(df_international, selected_year_int, indicator="EXPORTS")
        delta_exports_other = format_delta(delta_tons, delta_percent)

    

    # Render metrics OVERVIEW
    col1, col2 = st.columns([1,2])
    with col1:
        sunburst_trade(df_domestic, df_international, selected_year_int)

    with col2:
        col1, col2 = st.columns([1,1])
        with col1:
            icon_url = "https://www.thiings.co/_next/image?url=https%3A%2F%2Flftz25oez4aqbxpq.public.blob.vercel-storage.com%2Fimage-yWrzl9cEKipTE5anAxGTt91QKEyjxu.png&w=320&q=75"
            render_metric(
                label="Imports from United States",
                icon=icon_url,
                value=total_import_tons,
                delta= delta_imports_us,  # Puedes calcular esto si tienes datos anteriores
                subtext="Percentage change from previous year",
                midtext="Air Cargo"
            )
        with col2:
            icon_url_e="https://www.thiings.co/_next/image?url=https%3A%2F%2Flftz25oez4aqbxpq.public.blob.vercel-storage.com%2Fimage-q9gN22SubmqYIlKQZlPQY7lOM5vOIe.png&w=1000&q=75"
            render_metric(
                icon= icon_url_e,
                label="Exports to United States",
                value=total_exports_tons,
                delta= delta_exports_us,  # También ajustable
                subtext="Percentage change from previous year",
                midtext="Air Cargo"
            )
        
        col1, col2 = st.columns([1,1])
        with col1:
            icon_url = "https://www.thiings.co/_next/image?url=https%3A%2F%2Flftz25oez4aqbxpq.public.blob.vercel-storage.com%2Fimage-BrZblspfA12ogcaYEJRCJcjOA2mGwO.png&w=320&q=75"
            render_metric(
                label="🌎Imports from Foreign countries",
                icon=icon_url,
                value=total_import_other_tons,
                delta=delta_imports_other,  # Puedes calcular esto si tienes datos anteriores
                subtext="Percentage change from previous year",
                midtext="Air Cargo"
            )
        with col2:
            icon_url = "https://www.thiings.co/_next/image?url=https%3A%2F%2Flftz25oez4aqbxpq.public.blob.vercel-storage.com%2Fimage-3yDhwbfA3GOB6IIsObXEibckchNUZW.png&w=320&q=75"
            render_metric(
                icon=icon_url,
                label="🌎Exports to Foreign countries",
                value=total_exports_other_tons,
                delta=delta_exports_other,  # También ajustable
                subtext="Percentage change from previous year",
                midtext="Air Cargo"
            )
 
# --- LOGIN LOGIC ---   
filters, filter_data, selected_year_int = filter_year(df_domestic)
metrics_overview(filter_data, filters, selected_year_int, df_domestic)






