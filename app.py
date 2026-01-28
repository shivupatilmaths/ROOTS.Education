import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from streamlit_option_menu import option_menu
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONFIGURATION & CSS ---
st.set_page_config(page_title="ROOTS Education", page_icon="resources/images/logo.png", layout="wide")

# --- 2. GOOGLE SHEET CONNECTION FUNCTION ---
# --- 2. GOOGLE SHEET CONNECTION FUNCTION ---
def connect_to_gsheet():
    try:
        # We access the secrets we set up in secrets.toml
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        # Create credentials object from the secrets dictionary
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        
        # Open the Sheet using the ID (Safe & Robust)
        sheet_id = "1QhBhR1vtxBybXvoBWkcB2f1zxOuUOKZ5908wbDOa5Bw"
        sheet = client.open_by_key(sheet_id).sheet1
        return sheet

    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# Helper functions for images
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f: data = f.read()
    return base64.b64encode(data).decode()

def get_img_with_href(local_img_path, width):
    try:
        img_format = os.path.splitext(local_img_path)[-1].replace('.', '')
        bin_str = get_base64_of_bin_file(local_img_path)
        return f'<img src="data:image/{img_format};base64,{bin_str}" width="{width}">'
    except: return ""

st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    header { visibility: hidden; }
    .hero-container { background: linear-gradient(90deg, #f7b733 0%, #fc4a1a 100%); padding: 3rem; color: white; border-radius: 10px; margin-bottom: 20px;}
    .footer { background-color: #262730; color: white; padding: 30px; text-align: center; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'student_name' not in st.session_state: st.session_state.student_name = "Guest"

# --- 4. TOP NAV ---
try: logo_html = get_img_with_href("resources/images/logo.png", 100)
except: logo_html = "ROOTS"
c1, c2 = st.columns([1,3])
with c1: st.markdown(logo_html, unsafe_allow_html=True)
with c2:
    selected = option_menu(None, ["Home", "Courses", "Results", "Contact"], 
        icons=["house", "book", "trophy", "envelope"], orientation="horizontal")

# --- 5. SIDEBAR (Login Logic with Google Sheets) ---
st.sidebar.subheader("🔐 Portal")

if st.session_state.logged_in or st.session_state.is_admin:
    if st.session_state.is_admin: st.sidebar.success("Admin Mode")
    else: st.sidebar.success(f"Hi, {st.session_state.student_name}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()
else:
    mode = st.sidebar.radio("Login As:", ["Student", "Admin"])
    if mode == "Student":
        sid = st.sidebar.text_input("ID")
        pwd = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            sheet = connect_to_gsheet()
            if sheet:
                # Get all records from Google Sheet
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                # Convert ID to string to match input
                df["student_id"] = df["student_id"].astype(str)
                df["password"] = df["password"].astype(str)
                
                user = df[(df["student_id"] == sid) & (df["password"] == pwd)]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.student_name = user.iloc[0]["name"]
                    st.rerun()
                else:
                    st.sidebar.error("Wrong Credentials")
                    
    elif mode == "Admin":
        # Separate the input box from the button
        admin_pass = st.sidebar.text_input("Enter Admin Password", type="password")
        
        if st.sidebar.button("Login as Principal"):
            if admin_pass == "12345":
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.sidebar.error("Incorrect Password!")

# --- 6. PAGES ---
if st.session_state.is_admin:
    st.title("🛡️ Admin Dashboard (Live Google Sheet Data)")
    sheet = connect_to_gsheet()
    if sheet:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        st.dataframe(df)
        
        with st.form("add_stu"):
            st.write("Register New Student")
            c1,c2 = st.columns(2)
            n = c1.text_input("Name"); i = c2.text_input("ID"); p = c1.text_input("Password", "1234")
            f = c2.number_input("Fees", 1000); a = "0%"
            if st.form_submit_button("Save to Cloud Database"):
                # Add row to Google Sheet
                row = [i, n, p, a, f]
                sheet.append_row(row)
                st.success(f"Saved {n} to Google Drive!")
                st.rerun()

else:
    if selected == "Home":
        st.markdown('<div class="hero-container"><h1>Welcome to Roots Digital</h1><p>Powered by Cloud Computing</p></div>', unsafe_allow_html=True)
    elif selected == "Results":
        st.title("🏆 Results")
        if not st.session_state.logged_in: st.warning("Login required")
        else: st.write(f"Results for **{st.session_state.student_name}** coming soon.")

st.markdown('<div class="footer">© 2026 ROOTS Education</div>', unsafe_allow_html=True)