import pandas as pd
import streamlit as st

#_________________________________________________________________________________________________LOAD AND PREPARE DATA

@st.cache_data
def load_and_prepare_data(file_path: str)-> pd.DataFrame:
    try:
        df_trade =pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Error: File '{file_path}' was not found.")
        st.stop()
    
    expected_cols = [
        'Indicator','Year', 'Origin', 'Lat_Origin', 'Long_Origin', 'Destination',
        'Lat_dest', 'Long_dest','Commodity code', 'Commodity Description',
        'Air Shipping Weight (Tons)', 'Air Value ($US)'
    ]
    for col in expected_cols:
        if col not in df_trade.columns:
            st.error(f"Error: Column '{col}' is missing from the data.")
            st.stop()
    
    for col in ['Lat_Origin', 'Long_Origin', 'Lat_dest', 'Long_dest']:
        df_trade[col] = pd.to_numeric(df_trade[col], errors='coerce')
    #st.write(df_trade.dtypes) 

    df_trade = df_trade.dropna(subset=['Lat_Origin', 'Long_Origin', 'Lat_dest', 'Long_dest'])
    return df_trade

@st.cache_data
def load_and_prepare_international_data(file_path: str) -> pd.DataFrame:
    try:
        df_international = pd.read_excel(file_path)
    except FileNotFoundError:
        st.error(f"Error: File '{file_path}' was not found.")
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
            st.error(f"Error: Column '{col}' is missing from the international data.")
            st.stop()

    # Convert coordinates to numeric
    for col in ['Latitude_country', 'Longitude_country']:
        df_international[col] = pd.to_numeric(df_international[col], errors='coerce')

    # Drop rows with missing coordinates
    df_international = df_international.dropna(subset=['Latitude_country', 'Longitude_country'])

    # Normalize key fields
    df_international['Year'] = pd.to_numeric(df_international['Year'], errors='coerce')
    df_international['Country'] = df_international['Country'].str.strip().str.upper()
    df_international['Air Total Weight (Tons)'] = pd.to_numeric(df_international['Air Total Weight (Tons)'], errors='coerce')

    return df_international


def initialize_trade_data():
    if "df_domestic" not in st.session_state:
        st.session_state.df_domestic = load_and_prepare_data("U.S Domestics Trade - Imports and Exports.csv")

def initialize_international_data():
    if "df_international" not in st.session_state:
        st.session_state.df_international = load_and_prepare_international_data("International Trade - Imports and Exports.xlsx")
