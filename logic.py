import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fpdf import FPDF
import streamlit as st

# --- DATABASE CONNECTION ---
def connect_to_gsheet():
    try:
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        # YOUR SHEET ID
        sheet_id = "1QhBhR1vtxBybXvoBWkcB2f1zxOuUOKZ5908wbDOa5Bw"
        return client.open_by_key(sheet_id).sheet1
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None

# --- PDF GENERATOR ---
def generate_pdf_report(student_name, attendance, fees_status):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 20, "ROOTS Education", ln=True, align="C")
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Official Student Report Card", ln=True, align="C")
    pdf.ln(20)
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Name: {student_name}", ln=True)
    pdf.cell(0, 10, f"Attendance: {attendance}", ln=True)
    pdf.cell(0, 10, f"Fees Status: {fees_status}", ln=True)
    
    return bytes(pdf.output(dest="S"))

# --- ADD NEW STUDENT ---
def add_student(student_id, name, password, attendance, fees_due):
    try:
        sheet = connect_to_gsheet()
        if sheet:
            sheet.append_row([student_id, name, password, attendance, fees_due])
            return True
    except Exception as e:
        st.error(f"Error adding student: {e}")
        return False

# --- UPDATE ATTENDANCE ---
def update_attendance(student_id, new_attendance):
    try:
        sheet = connect_to_gsheet()
        if sheet:
            cell = sheet.find(student_id)
            sheet.update_cell(cell.row, 4, f"{new_attendance}%")
            return True
    except Exception as e:
        st.error(f"Update Error: {e}")
        return False

# --- NEW: DELETE STUDENT ---
def delete_student(student_id):
    try:
        sheet = connect_to_gsheet()
        if sheet:
            # 1. Find the row where the student is
            cell = sheet.find(student_id)
            # 2. Delete that specific row
            sheet.delete_rows(cell.row)
            return True
    except Exception as e:
        st.error(f"Deletion Error: {e}")
        return False
