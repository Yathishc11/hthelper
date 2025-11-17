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
            tight_tolerance_plastics = st.checkbox("tight tolerance plastics")
            tight_tolerance_metals = st.checkbox("tight tolerance metals")

        with st.expander("Speedy Squad"):
            Quick_LT = st.checkbox("Quick LT")
            Production_Qty = st.checkbox("Production Qty")
            Complex_Job = st.checkbox("Complex Job")
            hardware_install = st.checkbox("hardware install")
            multi_axis_machine = st.checkbox("multi axis machine")
            Quick_SLA = st.checkbox("Quick SLA")

        with st.expander("Compliance Cowboys"):
            cmm_inspection = st.checkbox("CMM inspection")
            ISO_9001 = st.checkbox("ISO 9001")
            AS9100D = st.checkbox("AS9100D")
            ISO_13485 = st.checkbox("ISO 13485")
            ITAR = st.checkbox("ITAR")

        no_post_process = st.checkbox("No post process")

        selected_finish = None
        if not no_post_process:
            selected_finish = st.selectbox(
                "Please select the Post Process",
                [x for x in finish_df[selected_process].dropna()]
            )

        submitted = st.form_submit_button("Submit")

        if submitted:
            # Filter by process and material
            df = main_df[main_df["Process offered"] == selected_process]
            df = df[df[selected_material] == True]

            # Bounding box filter
            df = df[
                (df["Bounding box [x]"] >= float(bounding_box_x)) &
                (df["Bounding box [y]"] >= float(bounding_box_y)) &
                (df["Bounding box [z]"] >= float(bounding_box_z))
            ]

            # Checkbox filters applied dynamically
            checkbox_map = {
                "hardware install": hardware_install,
                "multi axis machine": multi_axis_machine,
                "CMM inspection": cmm_inspection,
                "tight tolerance plastics": tight_tolerance_plastics,
                "tight tolerance metals": tight_tolerance_metals,
                "EDM": edm,
                "Quick LT": Quick_LT,
                "Production Qty": Production_Qty,
                "Complex Job": Complex_Job,
                "Loves Plastic": Loves_Plastic,
                "Hard Metals": Hard_Metals,
                "Rare Materials": Rare_Materials,
                "Quick SLA": Quick_SLA,
                "ISO 9001": ISO_9001,
                "AS9100D": AS9100D,
                "ISO 13485": ISO_13485,
                "ITAR": ITAR
            }

            for col, flag in checkbox_map.items():
                if flag:
                    df = df[df[col] == True]

            # Post process
            if selected_finish:
                df = df[df[selected_finish] == True]

            display_columns = ["MP name", "Email", "Phone No.", "Notes"]
            df = df[display_columns]

            df = df.sample(frac=1).head(4)

            if not df.empty:
                st.write("MPs Recommended:")
                st.table(df)
            else:
                st.write("No data found matching the criteria.")

    # Independent MP name search
    st.write("### Search MP by Name")
    mp_name_search = st.text_input("Enter MP name to search")

    if mp_name_search:
        result = main_df[main_df["MP name"].str.contains(mp_name_search, case=False)]
        if not result.empty:
            st.write(result[["MP name", "Email"]])
        else:
            st.write("No MP found with that name.")

except Exception as e:
    st.write("An error occurred:", e)
