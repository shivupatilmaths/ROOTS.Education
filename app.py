import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from streamlit_option_menu import option_menu

# --- 1. CONFIGURATION & CSS ---
st.set_page_config(
    page_title="ROOTS Education",
    page_icon="resources/images/logo.png",
    layout="wide"
)

# Helper functions
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f: data = f.read()
    return base64.b64encode(data).decode()

def get_img_with_href(local_img_path, width):
    try:
        img_format = os.path.splitext(local_img_path)[-1].replace('.', '')
        bin_str = get_base64_of_bin_file(local_img_path)
        return f'<img src="data:image/{img_format};base64,{bin_str}" width="{width}">'
    except:
        return ""

st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    header { visibility: hidden; }
    
    /* Hero Gradient */
    .hero-container {
        background: linear-gradient(90deg, #f7b733 0%, #fc4a1a 100%);
        padding: 3rem;
        color: white;
        margin-top: 20px;
        margin-bottom: 30px;
        border-radius: 10px;
    }
    
    /* Course/Download Cards */
    .course-box {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 10px;
        transition: 0.3s;
    }
    .course-box:hover {
        border-color: #fc4a1a;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .footer {
        background-color: #262730;
        color: white;
        padding: 30px;
        text-align: center;
        margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'student_name' not in st.session_state: st.session_state.student_name = "Guest"

# --- 3. HEADER & MENU ---
try:
    logo_html = get_img_with_href("resources/images/logo.png", 100)
except:
    logo_html = "<h2>ROOTS</h2>"

col1, col2 = st.columns([1, 3])
with col1:
    st.markdown(logo_html, unsafe_allow_html=True)
with col2:
    selected = option_menu(
        menu_title=None,
        options=["Home", "Courses", "Results", "Downloads", "Contact"], # Added DOWNLOADS back
        icons=["house", "book", "trophy", "cloud-download", "envelope"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#bf0a30"},
        }
    )

# --- 4. SIDEBAR (SECURE LOGIN) ---
st.sidebar.subheader("🔐 Access Portal")

if st.session_state.logged_in or st.session_state.is_admin:
    if st.session_state.is_admin:
        st.sidebar.success("👤 Mode: ADMIN")
    else:
        st.sidebar.success(f"👤 Student: {st.session_state.student_name}")
        
    if st.sidebar.button("Logout", type="primary"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()
else:
    login_mode = st.sidebar.radio("Login As:", ["Student", "Admin"])
    
    if login_mode == "Student":
        sid = st.sidebar.text_input("Student ID")
        spass = st.sidebar.text_input("Password", type="password")
        
        if st.sidebar.button("Login"):
            try:
                df = pd.read_csv("resources/data/students.csv")
                df["student_id"] = df["student_id"].astype(str)
                
                # Auto-fix password column
                if "password" not in df.columns:
                    df["password"] = "1234"
                    df.to_csv("resources/data/students.csv", index=False)
                
                df["password"] = df["password"].astype(str)
                user = df[(df["student_id"] == sid) & (df["password"] == spass)]
                
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.student_name = user.iloc[0]["name"]
                    st.session_state.student_att = user.iloc[0]["attendance"]
                    st.session_state.student_fees = user.iloc[0]["fees_due"]
                    st.rerun()
                else:
                    st.sidebar.error("Invalid ID or Password")
            except Exception as e:
                st.sidebar.error(f"DB Error: {e}")
                
    elif login_mode == "Admin":
        pwd = st.sidebar.text_input("Master Password", type="password")
        if st.sidebar.button("Admin Login"):
            if pwd == "12345":
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.sidebar.error("Access Denied")

# --- 5. PAGE LOGIC ---

# 🛑 ADMIN DASHBOARD
if st.session_state.is_admin:
    st.title("🛡️ Principal's Command Center")
    try:
        df_students = pd.read_csv("resources/data/students.csv")
        df_msgs = pd.read_csv("resources/data/messages.csv")
        df_results = pd.read_csv("resources/data/results.csv")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Students", len(df_students))
        m2.metric("Pending Fees", f"₹{df_students['fees_due'].sum()}")
        m3.metric("Inquiries", len(df_msgs))
        try: avg = round(df_results['Score'].mean(), 1)
        except: avg = 0
        m4.metric("Avg Quiz Score", f"{avg}/3")
        
        st.write("---")
        t1, t2, t3 = st.tabs(["Students", "Inquiries", "Register"])
        
        with t1: st.dataframe(df_students)
        with t2: st.dataframe(df_msgs)
        with t3:
            with st.form("add"):
                n = st.text_input("Name")
                i = st.text_input("ID")
                f = st.number_input("Fees")
                p = st.text_input("Password", value="1234")
                if st.form_submit_button("Add"):
                    new = pd.DataFrame([{"student_id": i, "name": n, "fees_due": f, "password": p, "attendance": "85%"}])
                    pd.concat([df_students, new], ignore_index=True).to_csv("resources/data/students.csv", index=False)
                    st.success("Added!")
                    st.rerun()
    except: st.error("Database Missing")

# 🛑 STUDENT PAGES
else:
    if selected == "Home":
        try: boy_html = get_img_with_href("resources/images/boy_hero.png", 300)
        except: boy_html = ""
        st.markdown(f"""
        <div class="hero-container" style="display: flex; align-items: center; justify-content: center; gap: 40px;">
            <div style="flex: 1; text-align: right;">{boy_html}</div>
            <div style="flex: 2;">
                <span style="background:black; padding:5px 10px; font-size:12px; border-radius:4px; color: #f7b733;">INDIA'S FIRST 3M MODEL</span>
                <h1 style="font-size: 3rem; line-height: 1.1; margin-top: 10px;">Unlocking Potential.<br>Building Toppers.</h1>
            </div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.info("**Mentorship**"); c2.warning("**Methodology**"); c3.success("**Mindset**")

    elif selected == "Courses":
        st.title("📚 Academic Programs")
        tab1, tab2, tab3 = st.tabs(["Foundation", "Advanced", "Board Prep"])
        with tab1: st.info("Class 6-8 Basics")
        with tab2: st.warning("Class 9 Advanced")
        with tab3: st.error("Class 10 Target 100")

    # ✅ RESTORED: THE FULL ONLINE TEST
    elif selected == "Results":
        st.title("🏆 Student Corner")
        if not st.session_state.logged_in:
            st.warning("🔒 Please Login to attempt tests.")
        else:
            st.subheader(f"Student: {st.session_state.student_name}")
            t1, t2 = st.tabs(["📝 Weekly Challenge", "📈 My Report"])
            
            with t1:
                st.write("### Math Quiz (Algebra & Geometry)")
                with st.form("quiz_form"):
                    st.write("1. What is the next term: 2, 5, 8, 11...?")
                    q1 = st.radio("", ["13", "14", "15"], key="q1")
                    
                    st.write("2. Sum of angles in a triangle?")
                    q2 = st.radio("", ["180°", "360°", "90°"], key="q2")
                    
                    st.write("3. Value of sin(90°)?")
                    q3 = st.radio("", ["0", "1", "0.5"], key="q3")
                    
                    if st.form_submit_button("Submit Answers"):
                        score = 0
                        if q1 == "14": score += 1
                        if q2 == "180°": score += 1
                        if q3 == "1": score += 1
                        
                        if score == 3:
                            st.balloons()
                            st.success(f"🎉 Perfect Score! 3/3")
                        else:
                            st.info(f"You scored {score}/3")
                        
                        # Save Data
                        try: df=pd.read_csv("resources/data/results.csv")
                        except: df=pd.DataFrame(columns=["Name","Score","Date"])
                        new={"Name":st.session_state.student_name,"Score":score,"Date":datetime.now().strftime("%Y-%m-%d")}
                        pd.concat([df,pd.DataFrame([new])],ignore_index=True).to_csv("resources/data/results.csv",index=False)
            
            with t2:
                try:
                    df=pd.read_csv("resources/data/results.csv")
                    my=df[df["Name"]==st.session_state.student_name]
                    if not my.empty: st.line_chart(my[["Date","Score"]].set_index("Date"))
                    else: st.info("No test history found.")
                except: st.warning("No data yet.")

    # ✅ RESTORED: THE DOWNLOADS PAGE
    elif selected == "Downloads":
        st.title("📂 Resource Center")
        if not st.session_state.logged_in:
            st.warning("🔒 Please Login to download files.")
        else:
            st.write("### 📄 Available Question Papers")
            
            # The original dictionary
            files = {
                "Grade 10 - Algebra": "PS5 Math Ans.pdf",
                "Grade 10 - Geometry": "PS5 Math QP.pdf"
            }
            
            for name, filename in files.items():
                filepath = f"resources/docs/{filename}"
                
                # Card Styling for files
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f'<div class="course-box" style="padding:10px;"><b>{name}</b></div>', unsafe_allow_html=True)
                with col2:
                    try:
                        with open(filepath, "rb") as f:
                            st.download_button(
                                label="⬇️ Download",
                                data=f,
                                file_name=filename,
                                mime="application/pdf",
                                key=filename
                            )
                    except FileNotFoundError:
                        st.error("File Missing")

    elif selected == "Contact":
        st.title("📞 Contact Us")
        with st.form("contact"):
            n=st.text_input("Name"); m=st.text_input("Msg")
            if st.form_submit_button("Send"):
                try: df=pd.read_csv("resources/data/messages.csv")
                except: df=pd.DataFrame(columns=["Name","Message"])
                pd.concat([df,pd.DataFrame([{"Name":n,"Message":m}])],ignore_index=True).to_csv("resources/data/messages.csv",index=False)
                st.success("Sent!")

# --- 6. FOOTER ---
st.markdown('<div class="footer"><p>© 2026 ROOTS Education.</p></div>', unsafe_allow_html=True)
