import streamlit as st


# [Set up the Streamlit app]
st.set_page_config(layout="wide", page_title="Puerto Rico Highways Performance ", initial_sidebar_state="expanded")

st.markdown(f"""
                <style>
                .block-container {{
                    padding-top: 1rem;
                }} </style>
                <h1 style='display: flex; align-items: center;gap: 12px; margin-top: 10px;'> <img src='https://www.thiings.co/_next/image?url=https%3A%2F%2Flftz25oez4aqbxpq.public.blob.vercel-storage.com%2Fimage-uBD2X8E9FMFPGgAZv0YYRXCMZbaJTt.png&w=1000&q=75' width='85' style='margin-bottom: 4px;'/>
                    Puerto Rico Highways Performance - 
                    <span style='color:#c8c9d0; font-weight:normal;'> <h1> Estimated Road Freight Volume </h1></span> </h1> """, unsafe_allow_html=True)

st.container()
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.image("Flow map - Puerto Rico Highways.png", width=1600)
    st.image("AADT Gradient.png", width=1600, )
