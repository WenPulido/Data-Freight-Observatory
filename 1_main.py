import streamlit as st
import pandas as pd
from users import login
import base64
from streamlit_option_menu import option_menu as op


import streamlit as st

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def get_base64_image(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- USERS ---
users = {"Admin": "cetl4321"}

bg_img = get_base64_image("assets/Images/Background/Background2.png")


login_bg_css = f"""
<style>
  [data-testid="stAppViewContainer"] {{
    position: relative;
    background: linear-gradient(135deg, #1a4d4d 0%, #2d5a3d 50%, #1a1d2e 100%);
  }}

  [data-testid="stAppViewContainer"]::before {{
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background-image: url("data:image/png;base64,{bg_img}");
    background-size: cover;
    background-position: center;
    opacity: 0.15;
    z-index: 0;
  }}
  
  [data-testid="stAppViewContainer"] > div {{
    position: relative;
    z-index: 1;
  }}
  
  [data-testid="stHeader"] {{
    background: rgba(0, 0, 0, 0);
    position: relative;
    z-index: 1;
  }}

  /* Login container */
  .login-container {{
    background: rgba(45, 50, 80, 0.4);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    border: 2px solid rgba(74, 157, 95, 0.3);
    padding: 40px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    max-width: 500px;
    margin: 50px auto;
  }}
</style>
"""

reset_bg_css = """
<style>
  [data-testid="stAppViewContainer"] {
    background: #1a1d2e !important;
  }
  [data-testid="stAppViewContainer"]::before {
    display: none !important;
  }
</style>
"""

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    #Background and logo
    st.markdown(login_bg_css, unsafe_allow_html=True)
    st.markdown("""
                <style>
                img[data-testid="stImage"] {
                    width: 90% !important;      
                    max-width: 300px !important; /* No excede 700px */
                    height: auto !important;
                    display: block !important;
                    margin: 5px auto !important; 
                }
                </style>
            """, unsafe_allow_html=True)
    st.image("assets/Images/Logos/CETL.png") 
    
    #Columns for centering
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Contenedor de bienvenida
        st.markdown("""
        <div style="
            background: rgba(45, 90, 61, 0.3);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            border: 1px solid rgba(74, 157, 95, 0.4);
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            margin-top: -45px;
        ">
            <h2 style="
                color: #4a9d5f;
                font-size: 28px;
                font-weight: 700;
                text-align: center;
                margin: 0 0 10px 0;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            ">Welcome to</h2>
            <h3 style="
                color: #3d9a9a;
                font-size: 24px;
                font-weight: 600;
                text-align: center;
                margin: 0;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            ">Puerto Rico Data Freight Observatory</h3>
        </div>
        """, unsafe_allow_html=True)

        # Inputs de usuario y contraseña
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        # CSS para inputs y botón
        st.markdown("""
        <style>
        div.stTextInput > label {
            font-size: 20px !important;
            font-weight: 600 !important;
            color: #4a9d5f !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
            font-weight: bold !important;
        }
        div.stTextInput > div > input {
            font-size: 16px !important;
            padding: 12px !important;
            background: rgba(45, 90, 61, 0.2) !important;
            border: 2px solid rgba(74, 157, 95, 0.4) !important;
            border-radius: 10px !important;
            color: #e8eaed !important;
            transition: all 0.3s ease !important;
        }
        div.stTextInput > div > input:focus {
            border-color: #3d9a9a !important;
            box-shadow: 0 0 15px rgba(61, 154, 154, 0.3) !important;
        }
        div.stTextInput > div > input::placeholder {
            color: rgba(232, 234, 237, 0.5) !important;
        }
        .stTextInput { margin-bottom: 20px !important; }

        div.stButton > button[kind='primary'] {
            background: linear-gradient(135deg, #3d7a4d 0%, #3d9a9a 100%) !important;
            color: white !important;
            font-size: 18px !important;
            font-weight: 700 !important;
            border-radius: 12px !important;
            padding: 14px 24px !important;
            border: 2px solid #4a9d5f !important;
            width: 100% !important;
            box-shadow: 0 4px 15px rgba(61, 154, 154, 0.4) !important;
            transition: all 0.3s ease !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        div.stButton > button[kind='primary']:hover {
            background: linear-gradient(135deg, #4a9d5f 0%, #4aafaf 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(61, 154, 154, 0.6) !important;
        }
        div.stButton > button[kind='primary']:active { transform: translateY(0px) !important; }
        .stAlert {
            background: rgba(239, 68, 68, 0.2) !important;
            border: 1px solid rgba(239, 68, 68, 0.5) !important;
            border-radius: 10px !important;
            color: #fca5a5 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # Botón login
        if st.button("Sign in", type="primary", use_container_width=True, key="login_button"):
            if username in users and users[username] == password:
                st.session_state.logged_in = True
            else:
                st.error("Invalid username or password")

    st.stop()

# --- RESET BACKGROUND WHEN LOGGED IN ---
st.markdown(reset_bg_css, unsafe_allow_html=True)

# --- PAGES ---
pages = {
    "Overview": [st.Page("overview.py", title="Overview")],
    "Domestic Trade": [
        st.Page("pages/2_AirCargo.py", title="Air Cargo Trade (Domestic)"),
        #st.Page("4_MaritimeCargo.py", title="Maritime Cargo Trade (Domestic)")
    ],
    "International Trade": [
        st.Page("pages/3_InternationalTrade.py", title="Air Cargo Trade (International)"),
        st.Page("pages/5_InterMaritimeTrade.py", title="Maritime Cargo Trade (International)")
    ],
    "Highway Movements": [
        st.Page("pages/6_Highways.py", title="Highway Movements")]
}

pg = st.navigation(pages, position="top")
pg.run()
