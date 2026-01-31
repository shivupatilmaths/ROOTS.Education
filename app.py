import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px

# --- IMPORT OUR NEW MODULES ---
import logic  # Importing logic.py
import style  # Importing style.py

# 1. Setup
st.set_page_config(page_title="ROOTS Education", page_icon="🌱", layout="wide")
style.apply_custom_css()  # Applying styles from style.py

# 2. Navigation
c1, c2 = st.columns([1, 6])
with c1: st.write("🌱 **ROOTS**") 
with c2:
    selected = option_menu(None, ["Home", "Login"], 
        icons=["house", "person"], 
        default_index=0, orientation="horizontal")

# 3. Content
if selected == "Home":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="hero"><h1>Welcome to ROOTS</h1></div>', unsafe_allow_html=True)
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=200)

elif selected == "Login":
    tab1, tab2 = st.tabs(["Student Login", "Admin Dashboard"])

    with tab1:
        st.title("🔐 Login")
        sid = st.text_input("Student ID")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            sheet = logic.connect_to_gsheet()  # Using the logic file!
            if sheet:
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                # Simple check
                user = df[df["student_id"] == str(sid)]
                if not user.empty:
                    st.success(f"Welcome, {user.iloc[0]['name']}")

                    # PDF Generation using logic file
                    pdf_data = logic.generate_pdf_report(user.iloc[0]['name'], "90%", "Paid")
                    st.download_button("Download Report", pdf_data, "report.pdf")
                else:
                    st.error("User not found")

    with tab2:
        st.write("### 🛡️ Admin Dashboard")
        p = st.text_input("Admin Key", type="password")

        if p == "12345":  # Simple security check

            # --- NEW FEATURE: DIGITAL ADMISSION FORM ---
            with st.expander("➕ Admit New Student"):
                st.write("Enter details for the new student:")

                # 1. The Input Form
                c1, c2 = st.columns(2)
                with c1:
                    new_id = st.text_input("New ID (e.g., ST005)")
                    new_name = st.text_input("Full Name")
                with c2:
                    new_pass = st.text_input("Set Password")
                    new_fees = st.number_input("Fees Due (₹)", min_value=0, step=500)

                # 2. The Submit Button
                if st.button("Submit Admission"):
                    if new_id and new_name:
                        # Call the function from logic.py
                        success = logic.add_student(new_id, new_name, new_pass, "0%", new_fees)

                        if success:
                            st.success(f"✅ Successfully admitted {new_name}!")
                            st.balloons()  # Fun animation!
                        else:
                            st.error("❌ Failed to update database.")
                    else:
                        st.warning("⚠️ Please fill in all fields.")

            st.divider()

            # ... (Your existing 'Access Database' / Graphs code goes here) ...
