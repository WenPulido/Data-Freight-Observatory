import pandas as pd
import streamlit as st
import requests
from io import BytesIO

#_________________________________________________________________________________________________LOAD AND PREPARE DATA

@st.cache_data
def load_and_prepare_data(file_url: str) -> pd.DataFrame:
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        df_trade = pd.read_csv(BytesIO(response.content))
    except Exception as e:
        st.error(f"Error al cargar el archivo CSV desde la nube: {e}")
        st.stop()
    
    expected_cols = [
        'Indicator','Year', 'Origin', 'Lat_Origin', 'Long_Origin', 'Destination',
        'Lat_dest', 'Long_dest','Commodity code', 'Commodity Description',
        'Air Shipping Weight (Tons)', 'Air Value ($US)'
    ]
    for col in expected_cols:
        if col not in df_trade.columns:
            st.error(f"Error: Falta la columna '{col}' en los datos.")
            st.stop()
    
    for col in ['Lat_Origin', 'Long_Origin', 'Lat_dest', 'Long_dest']:
        df_trade[col] = pd.to_numeric(df_trade[col], errors='coerce')

    df_trade = df_trade.dropna(subset=['Lat_Origin', 'Long_Origin', 'Lat_dest', 'Long_dest'])
    return df_trade


@st.cache_data
def load_and_prepare_international_data(file_url: str) -> pd.DataFrame:
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        df_international = pd.read_excel(BytesIO(response.content))
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel desde la nube: {e}")
        st.stop()

    expected_cols = [
        'Indicator', 'Type Flow', 'Year', 'Port', 'Continent', 'International Organization',
        'Country', 'Latitude_country', 'Longitude_country', 'Commodity',
        'Total Exports Value ($US)', 'Vessel Total Exports Value ($US)',
        'Containerized Vessel Total Exports Value ($US)', 'Vessel Total Exports SWT (kg)',
        'Containerized Vessel Total Exports SWT (kg)', 'Air Total  Value ($US)',
        'Air Total  SWT (kg)', 'Air Total Weight (Tons)'
    ]

    for col in expected_cols:
        if col not in df_international.columns:
            st.error(f"Error: Falta la columna '{col}' en los datos internacionales.")
            st.stop()

    for col in ['Latitude_country', 'Longitude_country']:
        df_international[col] = pd.to_numeric(df_international[col], errors='coerce')

    df_international = df_international.dropna(subset=['Latitude_country', 'Longitude_country'])
    df_international['Year'] = pd.to_numeric(df_international['Year'], errors='coerce')
    df_international['Country'] = df_international['Country'].str.strip().str.upper()
    df_international['Air Total Weight (Tons)'] = pd.to_numeric(df_international['Air Total Weight (Tons)'], errors='coerce')

    return df_international


def initialize_trade_data():
    if "df_domestic" not in st.session_state:
        st.session_state.df_domestic = load_and_prepare_data(
            "https://sistemaupr-my.sharepoint.com/:x:/r/personal/wendy_pulido_upr_edu/Documents/Freight%20Data%20Observatory/U.S%20Domestics%20Trade%20-%20Imports%20and%20Exports.csv?download=1"
        )

def initialize_international_data():
    if "df_international" not in st.session_state:
        st.session_state.df_international = load_and_prepare_international_data(
            "https://sistemaupr-my.sharepoint.com/:x:/g/personal/wendy_pulido_upr_edu/IQATvfbw0026TpZrtawDobcJAZ9Ya9dqcOiUPn-yZ61o7QM?download=1"
        )
