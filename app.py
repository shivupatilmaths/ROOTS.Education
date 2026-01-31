import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px

# --- IMPORT OUR MODULES ---
import logic
import style

# 1. Setup
st.set_page_config(page_title="ROOTS Education", page_icon="🌱", layout="wide")
style.apply_custom_css()

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
        st.markdown('<div class="hero"><h1>Welcome to ROOTS</h1><p>Future of Learning</p></div>', unsafe_allow_html=True)
        st.markdown("### 📢 Notice Board")
        st.info("📅 New Batch starts Feb 1st")
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=200)

elif selected == "Login":
    st.title("🔐 Portal Access")
    
    tab1, tab2 = st.tabs(["Student Login", "Principal Dashboard"])
    
    # --- STUDENT TAB ---
    with tab1:
        sid = st.text_input("Student ID")
        pwd = st.text_input("Password", type="password")
        
        if st.button("Login"):
            sheet = logic.connect_to_gsheet()
            if sheet:
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                df["student_id"] = df["student_id"].astype(str)
                
                user = df[df["student_id"] == sid]
                if not user.empty and str(user.iloc[0]["password"]) == pwd:
                    st.success(f"Welcome, {user.iloc[0]['name']}")
                    
                    pdf_data = logic.generate_pdf_report(
                        user.iloc[0]['name'], 
                        user.iloc[0]['attendance'],
                        "Paid" if user.iloc[0]['fees_due'] == 0 else "Pending"
                    )
                    st.download_button("📄 Download Report Card", pdf_data, "report.pdf", "application/pdf")
                else:
                    st.error("Invalid Credentials")

    # --- ADMIN TAB (Updated) ---
    with tab2:
        st.write("### 🛡️ Admin Dashboard")
        p = st.text_input("Admin Key", type="password")
        
        if st.button("Access") or p == "12345":
            if p == "12345":
                sheet = logic.connect_to_gsheet()
                if sheet:
                    df = pd.DataFrame(sheet.get_all_records())
                    all_ids = df["student_id"].astype(str).tolist()

                    # --- FEATURE 1: ADD STUDENT ---
                    with st.expander("➕ Admit New Student"):
                        c1, c2 = st.columns(2)
                        with c1:
                            new_id = st.text_input("New ID (e.g., ST005)")
                            new_name = st.text_input("Full Name")
                        with c2:
                            new_pass = st.text_input("Set Password")
                            new_fees = st.number_input("Fees Due", step=500)
                        
                        if st.button("Submit Admission"):
                            if logic.add_student(new_id, new_name, new_pass, "0%", new_fees):
                                st.success("Student Added!")
                                st.balloons()
                    
                    # --- FEATURE 2: UPDATE ATTENDANCE ---
                    with st.expander("📝 Update Attendance"):
                        target_student = st.selectbox("Select Student", all_ids)
                        new_att = st.slider("New Attendance %", 0, 100, 75)
                        
                        if st.button("Update Now"):
                            if logic.update_attendance(target_student, new_att):
                                st.success(f"Updated {target_student} to {new_att}%")
                                st.cache_data.clear() # Refresh data

                    st.divider()

                    # --- FEATURE 3: DANGER ZONE (DELETE) ---
                    st.subheader("⛔ Danger Zone")
                    with st.expander("🗑️ Delete Student Permanently"):
                        st.error("Warning: This action cannot be undone.")
                        
                        del_student = st.selectbox("Select Student to Remove", all_ids)
                        confirm = st.checkbox(f"I understand that {del_student} will be deleted forever.")
                        
                        if st.button("❌ Delete Student"):
                            if confirm:
                                if logic.delete_student(del_student):
                                    st.success("Student Deleted.")
                                    st.cache_data.clear()
                                    st.rerun()
                            else:
                                st.warning("Check the box to confirm.")
                    
                    st.divider()
                    st.dataframe(df) # Show full data
            else:
                st.error("Wrong Key")
