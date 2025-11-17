import ssl
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(layout="wide")
st.title("MP Selector")

# Google Sheets setup
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load service account from Streamlit secrets
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPE
)

client = gspread.authorize(creds)

# Google Sheet URL
sheet_url = "https://docs.google.com/spreadsheets/d/1bRV811WTUnzpWbip6otEONs4hH-i7qXCsKhwAr6O46A"

# Load worksheets
sheet = client.open_by_url(sheet_url)

main_df = pd.DataFrame(sheet.get_worksheet(0).get_all_records())
process_sheet_df = pd.DataFrame(sheet.get_worksheet_by_id(1240509380).get_all_records())
finish_df = pd.DataFrame(sheet.get_worksheet_by_id(1059488238).get_all_records())

# Convert bounding box columns
for col in ["Bounding box [x]", "Bounding box [y]", "Bounding box [z]"]:
    main_df[col] = pd.to_numeric(main_df[col], errors="coerce")

# UI selections
process = list(process_sheet_df.columns.values)[1:]
selected_process = st.selectbox("Please select the Process", process)

selected_material = st.selectbox(
    "Please select the Material",
    [m for m in process_sheet_df[selected_process].dropna()]
)

selected_region = st.radio("Please select the Region", ["United States"])

# Form inputs
try:
    with st.form("parameters"):
        col1, col2, col3 = st.columns(3)
        with col1:
            bounding_box_x = st.text_input("Dim in X (mm)", "0")
        with col2:
            bounding_box_y = st.text_input("Dim in Y (mm)", "0")
        with col3:
            bounding_box_z = st.text_input("Dim in Z (mm)", "0")

        # Categories
        with st.expander("Machining Maestros"):
            edm = st.checkbox("EDM")
            Loves_Plastic = st.checkbox("Loves Plastic")
            Hard_Metals = st.checkbox("Hard Metals")
            Rare_Materials = st.checkbox("Rare Materials")
            tight_tolerance_plastics = st.checkbox("tight tolerance plas
