import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Set the page layout to wide
st.set_page_config(layout="wide")

# Assuming you have your DataFrame and other variables defined already
sheet_url = "https://docs.google.com/spreadsheets/d/1bRV811WTUnzpWbip6otEONs4hH-i7qXCsKhwAr6O46A/edit#gid=0"
# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read(spreadsheet=sheet_url)
st.title('HT Helper')

main = conn.read(spreadsheet=sheet_url, worksheet="0")
process_sheet = conn.read(spreadsheet=sheet_url, worksheet="1240509380")
finish_sheet = conn.read(spreadsheet=sheet_url, worksheet="1059488238")
# pushing the data to a dataframe
main_df = pd.DataFrame(main)
process_sheet_df = pd.DataFrame(process_sheet)
finish_df = pd.DataFrame(finish_sheet)
# converting max X, max Y, max Z columns to floats so that they can be used for comparisons
main_df['max X'] = pd.to_numeric(main_df['max X'])
main_df['max Y'] = pd.to_numeric(main_df['max Y'])
main_df['max Z'] = pd.to_numeric(main_df['max Z'])

process = list(process_sheet_df.columns.values[1:])
selected_process = st.selectbox('Please select the Process', process)
selected_material = st.selectbox('Please select the Material',
                                 [material for material in process_sheet_df[selected_process].dropna()])

selected_region = st.radio("Please select the Region", ["United States", "India", "China"])

try:
    with st.form("parameters"):
        col1, col2, col3 = st.columns(3)
        with col1:
            bounding_box_x = st.text_input("Dim in X (in mm)", None, key="x_input", placeholder=0)
        with col2:
            bounding_box_y = st.text_input("Dim in Y (in mm)", None, key="y_input", placeholder=0)
        with col3:
            bounding_box_z = st.text_input("Dim in Z (in mm)", None, key="z_input", placeholder=0)

        hardware_install = st.checkbox("hardware install")
        multi_axis_machine = st.checkbox("multi axis machine")
        cmm_inspection = st.checkbox("CMM inspection")
        tight_tolerance_plastics = st.checkbox("tight tolerance plastics")
        tight_tolerance_metals = st.checkbox("tight tolerance metals")
        edm = st.checkbox("EDM")

        no_post_process = st.checkbox("No post process")

        # Add a dropdown for post process selection
        selected_finish = None
        if not no_post_process:
            selected_finish = st.selectbox('Please select the Post Process',
                                           [finish for finish in finish_df[selected_process].dropna()])

        submitted = st.form_submit_button("Submit")

        if submitted:
            # Filter data based on the selected process
            process_filtered_df = main_df[main_df["process name"] == selected_process]

            # Apply the bounding box filter
            bounding_box_query = (process_filtered_df["max X"] >= float(bounding_box_x)) & \
                                 (process_filtered_df["max Y"] >= float(bounding_box_y)) & \
                                 (process_filtered_df["max Z"] >= float(bounding_box_z))
            bounding_box_filtered_df = process_filtered_df[bounding_box_query]

            # Apply checkbox conditions
            if hardware_install:
                bounding_box_filtered_df = bounding_box_filtered_df[bounding_box_filtered_df["hardware install"] == True]

            if multi_axis_machine:
                bounding_box_filtered_df = bounding_box_filtered_df[bounding_box_filtered_df["multi axis machine"] == True]

            if cmm_inspection:
                bounding_box_filtered_df = bounding_box_filtered_df[bounding_box_filtered_df["CMM inspection"] == True]

            if tight_tolerance_plastics:
                bounding_box_filtered_df = bounding_box_filtered_df[bounding_box_filtered_df["tight tolerance plastics"] == True]

            if tight_tolerance_metals:
                bounding_box_filtered_df = bounding_box_filtered_df[bounding_box_filtered_df["tight tolerance metals"] == True]

            if edm:
                bounding_box_filtered_df = bounding_box_filtered_df[bounding_box_filtered_df["EDM"] == True]

            # Apply post process filter if "No post process" is not checked and a post process is selected
            if selected_finish:
                bounding_box_filtered_df = bounding_box_filtered_df[bounding_box_filtered_df[selected_finish] == True]

            # Select only required columns for display
            display_columns = ['MP name', 'Email', 'MP level', 'Phone No.', 'Notes']
            bounding_box_filtered_df = bounding_box_filtered_df[display_columns]

            # Display filtered results
            if not bounding_box_filtered_df.empty:
                st.write("MP's Recommended :face_with_monocle:")
                st.table(bounding_box_filtered_df)
                st.write("Select 1-2 MPs and cross check the selection with Sara :woman:")

            else:
                st.write("No data found matching the criteria.")

except Exception as e:
    st.write("An error occurred:", e)
    st.write("Please input the parameters correctly")
