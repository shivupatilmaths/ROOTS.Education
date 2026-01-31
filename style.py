import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        .block-container { padding-top: 5rem; padding-bottom: 5rem; }
        .hero {
            background: linear-gradient(135deg, #FF6B6B 0%, #556270 100%);
            padding: 40px;
            border-radius: 15px;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .card {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #FF6B6B;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
    </style>
    """, unsafe_allow_html=True)
