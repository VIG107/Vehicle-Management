import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Fleet Command", page_icon="🏎️", layout="wide")

# --- CUSTOM CSS FOR UI & ANIMATIONS ---
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e0ef;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"] * {
        color: #0f172a !important; 
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        border-color: #4CAF50 !important;
    }
    .big-font {
        font-size: 40px !important;
        font-weight: 700;
        color: #1E3A8A !important;
        margin-bottom: 0px;
    }
    .stApp {
        background-color: #f8fafc;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    return pd.read_excel("fleet_data.xlsx")

df = load_data()

# --- HELPER FUNCTIONS ---

def format_display_date(val):
    if pd.isna(val):
        return "N/A"
    if hasattr(val, 'strftime'):
        return val.strftime("%d-%m-%Y")
    val_str = str(val)
    if " 00:00:00" in val_str:
        try:
            return pd.to_datetime(val_str).strftime("%d-%m-%Y")
        except:
            return val_str.replace(" 00:00:00", "")
    if ("-" in val_str or "/" in val_str) and len(val_str) >= 6:
        try:
             return pd.to_datetime(val_str, dayfirst=True).strftime("%d-%m-%Y")
        except:
             pass
    return val_str

def check_expiry(date_val):
    if pd.isna(date_val):
        return "N/A"
    try:
        if isinstance(date_val, (int, float)):
            if date_val > 30000:
                date_obj = pd.to_datetime(date_val, unit='D', origin='1899-12-30')
            else:
                return str(int(date_val)) 
        elif isinstance(date_val, str):
            date_obj = pd.to_datetime(date_val, dayfirst=True)
        else:
            date_obj = date_val

        days_until_expiry = (date_obj - datetime.now()).days
        date_str = date_obj.strftime("%d-%m-%Y") 

        if days_until_expiry <= 0:
            return f"🚨 :red[**EXPIRED ({date_str})**]"
        elif days_until_expiry <= 30:
            return f"⚠️ :orange[**Due Soon ({date_str})**]"
        else:
            return f"✅ :green[{date_str}]"
    except Exception:
        return str(date_val).replace(" 00:00:00", "")

# --- SIDEBAR: CAR SELECTOR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3202/3202926.png", width=80)
    st.title("Garage Menu")
    selected_car = st.selectbox("Select a Vehicle", df['Car Name'].dropna().unique())
    st.markdown("---")
    st.write(f"**Total Fleet:** {len(df['Car Name'].dropna())} Vehicles")

# --- MAIN DASHBOARD AREA ---
if selected_car:
    st.toast(f"Loading profile for {selected_car}...", icon="🏎️")
    car_data = df[df['Car Name'] == selected_car].iloc[0]

    st.markdown(f'<p class="big-font">{selected_car}</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns([2.5, 1.5]) 

    with col1:
        st.markdown("### 📋 Identity & Registration")
        m1, m2, m3 = st.columns(3)
        m1.metric("License Plate", str(car_data.get('Regn No', 'N/A')))
        m2.metric("Owner", str(car_data.get('Owner', 'N/A')))
        m3.metric("Purchase Year", format_display_date(car_data.get('Year of Purchase', 'N/A')))
        
        st.write("") 

        st.markdown("### 🛡️ Legal Compliance")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("**PUC Status**")
            st.markdown(check_expiry(car_data.get('PUC Expiry Date')))
        with c2:
            st.write("**OD Insurance**")
            st.markdown(check_expiry(car_data.get('Insurance OD Expiry Date')))
        with c3:
            st.write("**3rd Party Insurance**")
            st.markdown(check_expiry(car_data.get('Insurance 3rd party expiry', 'N/A')))

        st.write("")

        st.markdown("### 🔧 Maintenance & Health")
        s1, s2, s3 = st.columns(3)
        s1.metric("Last Service Date", format_display_date(car_data.get('Last Service (Date)', 'N/A')))
        s2.metric("Last Service KM", str(car_data.get('Last Service (KM)', 'N/A')))
        s3.metric("Next Service Due", format_display_date(car_data.get('Next Service Date or KM', 'N/A')))

        if pd.notna(car_data.get('Additional Comments')):
            st.info(f"**📝 Notes:** {car_data.get('Additional Comments')}")

    with col2:
        image_filename = str(car_data.get('Image', '')).strip()
        
        # CHANGED: We removed os.path.join("images", ...) 
        # Python now looks for the file right next to app.py
        image_path = image_filename 
        
        if image_filename and image_filename.lower() != 'nan' and os.path.exists(image_path):
            try:
                st.image(image_path, use_container_width=True)
            except Exception:
                st.error(f"⚠️ Found '{image_filename}', but it appears corrupted.")
        else:
            st.warning("🖼️ No image available for this vehicle.")
            # Add this line to see EXACTLY what it is searching for:
            st.code(f"Looking for exactly: '{image_filename}'")
