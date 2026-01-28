import streamlit as st
import pandas as pd
import os
import base64
from streamlit_option_menu import option_menu
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px

# --- 1. CONFIGURATION & VISUAL STYLING ---
st.set_page_config(page_title="ROOTS Education", page_icon="🌱", layout="wide")

# Custom CSS for "Cards" and "Hero Section"
st.markdown("""
<style>
    .block-container { padding-top: 5rem; padding-bottom: 5rem; }
    
    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, #FF6B6B 0%, #556270 100%);
        padding: 40px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .hero h1 { font-size: 3rem; margin-bottom: 10px; color: white;}
    .hero p { font-size: 1.2rem; opacity: 0.9; }

    /* Card Design */
    .card {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF6B6B;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.3s;
    }
    .card:hover { transform: scale(1.02); }
    .card h3 { color: #333; margin-top: 0;}
    
    /* Footer */
    .footer { 
        position: fixed; bottom: 0; left: 0; width: 100%; 
        background-color: #262730; color: white; 
        text-align: center; padding: 10px; font-size: 0.8rem; z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. GOOGLE SHEET CONNECTION ---
def connect_to_gsheet():
    try:
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        # Load credentials from secrets.toml
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        
        # --- PASTE YOUR SHEET ID BELOW ---
        sheet_id = "1QhBhR1vtxBybXvoBWkcB2f1zxOuUOKZ5908wbDOa5Bw"
        
        return client.open_by_key(sheet_id).sheet1
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# --- 3. NAVIGATION ---
c1, c2 = st.columns([1, 6])
with c1: st.write("🌱 **ROOTS**") 
with c2:
    selected = option_menu(None, ["Home", "Downloads", "PDP Session", "Login"], 
        icons=["house", "cloud-download", "lightbulb", "person"], 
        menu_icon="cast", default_index=0, orientation="horizontal")

# --- 4. PAGE CONTENT ---

if selected == "Home":
    # 🌟 HERO SECTION
    st.markdown("""
    <div class="hero">
        <h1>Welcome to ROOTS Education</h1>
        <p>Transforming Minds | Ethical Thinking | Futuristic Learning</p>
    </div>
    """, unsafe_allow_html=True)

    # 📢 NOTICE BOARD
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('### 🚀 What We Offer')
        st.markdown("""
        <div class="card">
            <h3>🧮 Advanced Mathematics</h3>
            <p>Deep dive into calculus, algebra, and real-world applications.</p>
        </div>
        <div class="card">
            <h3>🤖 Future Tech</h3>
            <p>Coding, AI, and ethical use of technology.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown('### 📢 Updates')
        st.info("📅 **New Batch:** Starts Feb 1st")
        st.warning("⚠️ **Exam Alert:** Math Test on Monday")
        st.success("🎉 **Event:** Science Fair Winners Announced!")

elif selected == "Downloads":
    st.title("📂 Student Resources")
    st.write("Download syllabus, notes, and question papers.")
    
    c1, c2, c3 = st.columns(3)
    
    # --- DOWNLOAD BUTTON LOGIC ---
    with c1:
        st.image("https://cdn-icons-png.flaticon.com/512/337/337946.png", width=50)
        st.subheader("Syllabus")
        
        # This code looks for 'resources/files/syllabus.pdf'
        file_path = "resources/files/syllabus.pdf"
        
        if os.path.exists(file_path):
            with open(file_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Syllabus PDF",
                    data=pdf_file,
                    file_name="Roots_Maths_Syllabus.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("⚠️ File not found. Please upload 'syllabus.pdf' to 'resources/files/'")
             
    with c2:
        st.image("https://cdn-icons-png.flaticon.com/512/29/29302.png", width=50)
        st.subheader("Lecture Notes")
        st.button("View Notes", key="notes")
        
    with c3:
        st.image("https://cdn-icons-png.flaticon.com/512/201/201283.png", width=50)
        st.subheader("Assignments")
        st.button("Get Homework", key="hw")

elif selected == "PDP Session":
    st.title("🧠 Personality Development")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ### The Art of Communication
        * **Public Speaking:** Overcoming stage fear.
        * **Ethical Leadership:** Leading with integrity.
        """)
        st.button("Join Live Session")
    with c2:
        st.video("https://www.youtube.com/watch?v=ysz5S6PUM-U") 

elif selected == "Login":
    st.title("🔐 Student Portal")
    
    tab1, tab2 = st.tabs(["Student Login", "Principal Dashboard"])
    
    # --- STUDENT LOGIN ---
    with tab1:
        sid = st.text_input("Student ID")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            sheet = connect_to_gsheet()
            if sheet:
                try:
                    data = sheet.get_all_records()
                    df = pd.DataFrame(data)
                    df["student_id"] = df["student_id"].astype(str)
                    
                    user = df[df["student_id"] == sid]
                    if not user.empty and str(user.iloc[0]["password"]) == pwd:
                        st.success(f"Welcome back, {user.iloc[0]['name']}!")
                        st.metric("Attendance", user.iloc[0]["attendance"])
                    else:
                        st.error("Invalid ID or Password")
                except Exception as e:
                    st.error(f"Login Error: {e}")

    # --- PRINCIPAL DASHBOARD (WITH GRAPHS) ---
    with tab2:
        st.write("### 🛡️ Admin Analytics")
        p = st.text_input("Admin Key", type="password")
        
        if st.button("Access Database"):
            if p == "12345":
                st.success("Access Granted")
                sheet = connect_to_gsheet()
                
                if sheet:
                    # 1. Get Data
                    data = sheet.get_all_records()
                    df = pd.DataFrame(data)
                    
                    # 2. Clean Data (Fix numbers)
                    df['fees_due'] = pd.to_numeric(df['fees_due'], errors='coerce').fillna(0)
                    df['attendance_num'] = df['attendance'].astype(str).str.replace('%','').astype(float)
                    
                    # 3. Top Metrics
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Total Students", len(df))
                    m2.metric("Total Fees Due", f"₹{df['fees_due'].sum():,}")
                    m3.metric("Avg Attendance", f"{df['attendance_num'].mean():.1f}%")
                    
                    st.divider()

                    # 4. PLOTLY GRAPHS 📊
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        st.subheader("💰 Fees Status")
                        paid = df[df['fees_due'] == 0].shape[0]
                        pending = df[df['fees_due'] > 0].shape[0]
                        # Pie Chart
                        fig_pie = px.pie(names=['Paid', 'Pending'], values=[paid, pending], 
                                         color_discrete_sequence=['#00CC96', '#EF553B'])
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                    with c2:
                        st.subheader("📉 Attendance vs Fees")
                        # Scatter Plot
                        fig_scatter = px.scatter(df, x="attendance_num", y="fees_due", 
                                                 color="name", size="fees_due",
                                                 hover_data=['student_id'])
                        st.plotly_chart(fig_scatter, use_container_width=True)

                    # 5. Data Table
                    with st.expander("📂 View Full Register"):
                        st.dataframe(df)
            else:
                st.error("Incorrect Admin Key")

# Footer
st.markdown('<div class="footer">© 2026 ROOTS Education</div>', unsafe_allow_html=True)

