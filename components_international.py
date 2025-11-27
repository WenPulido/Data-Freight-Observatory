import streamlit as st
import base64

def get_image_base64(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8")

def continent_card(continent: str, tons: float, usd_value: float, delta: float, image_path, participation= None):
    
    st.markdown(
        f"""
        <div style="
            border: 1px solid #CCC; 
            border-radius: 15px;
            padding: -20px 20px;
            margin-bottom: 10px;
            margin-top: -30px;
            background-color: #F9F9F9;
        ">
            <div style="display: flex; align-items: center; gap: 5px;">
                <img src="data:image/png;base64,{get_image_base64(image_path)}" width="75" style="margin-right:px;" />
                <div>
                    <h5 style="margin:0;margin-bottom:-15px;">{continent}</h5>
                    <h5 style="margin:-20px 0;margin-bottom:1px;"><span style="color:{'green' if delta >= 0 else 'red'};">{delta:+,.0f}</span> Tons</h5>
                    <h5 style="margin:-20px 1;margin-bottom:-65px;">Tons: <b>{tons:,.0f}</b><h5>
                    <h5 style="margin:-20px 1; margin-bottom: -10px;">💰 <b>${usd_value:,.0f}</b></h5>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
 
