import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Set up page layout
st.set_page_config(page_title="PO Attainment Dashboard", layout="wide")

# Extracted Lecturer Data from image_8e1b5c.png (Name: Staff ID)
LECTURERS = {
    "Ahmad Nurrizal bin Muhammad": "169048",
    "Ts Dr Bibi Sarpinah bt. Sheikh Naimullah": "186681",
    "Ts Dr Saurdi bin Ishak": "204217",
    "Ts Dr Ishak bin Annuar": "220288",
    "Dr Nur Farahiah binti Ibrahim": "222053",
    "Dr Mazlina binti Mansor Hassan": "242415",
    "Dzufi Iszura binti Ispawi": "274632",
    "Fatimatul Anis Binti Bakri": "320010",
    "Dr Nur Atiqah Binti Abdul Rahman": "321019",
    "Dr Hadi Bin Jumaat": "323431",
    "Muhd Firdaus Bin Muhd Yusoff": "323509",
    "Mohd Yazid Bin Mohd Anas Khan": "331012"
}

# Restructured PO Mapping by Semester (Part) derived from PO-mapping.jpg
SEMESTER_MAPPING = {
    "Part 1": {
        "ECE128": ["PO1", "PO5", "PO10"],
        "EEE111": ["PO4", "PO6", "PO8", "PO9"]
    },
    "Part 2": {
        "EEE121": ["PO1", "PO2", "PO4"],
        "ESE122": ["PO1", "PO2", "PO4"],
        "EEE150": ["PO6", "PO7", "PO8"]
    },
    "Part 3": {
        "EEE250": ["PO1", "PO4", "PO5"],
        "ELE232": ["PO1", "PO2", "PO3"],
        "EEE231": ["PO1", "PO2", "PO3"],
        "ECM241": ["PO1", "PO4", "PO5"]
    },
    "Part 4": {
        "ESE241": ["PO1", "PO2", "PO4"],
        "ELE242": ["PO1", "PO2", "PO3"],
        "ECE351": ["PO1", "PO2", "PO5"],
        "ELE355": ["PO3", "PO4", "PO10"], 
        "EEE358": ["PO3", "PO4", "PO8", "PO9", "PO11"]
    },
    "Part 5": {
        "ESE359": ["PO1", "PO2", "PO4"],
        "ECE354": ["PO1", "PO2", "PO5"],
        "EPO244": ["PO1", "PO2", "PO4"],
        "ELE245": ["PO1", "PO2", "PO3"],
        "EEE368": ["PO3", "PO4", "PO8", "PO9", "P10", "PO11"]
    }
}

@st.cache_data
def load_data():
    """Loads and formats the student data from the Excel file."""
    file_path = "PO Attainment Individual.xlsx"
    xls = pd.ExcelFile(file_path)
    df_list = []
    
    # Loop through cohorts 20234, 20244, and 20254
    for sheet in xls.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet, header=1)
        df['Cohort'] = sheet
        df_list.append(df)
        
    master_df = pd.concat(df_list, ignore_index=True)
    master_df = master_df.dropna(subset=['STD_NAME', 'STD_MTX'])
    return master_df

def login():
    """Renders the login screen."""
    st.title("🛡️ Academic Advisor Login")
    st.write("Please select your name and enter your Staff ID to view your advisees.")
    
    lecturer_name = st.selectbox("Select Lecturer Profile", list(LECTURERS.keys()))
    password = st.text_input("Enter Password (Staff ID)", type="password")
    
    if st.button("Secure Login"):
        if LECTURERS.get(lecturer_name) == password:
            st.session_state['logged_in'] = True
            st.session_state['lecturer'] = lecturer_name
            st.rerun()
        else:
            st.error("Invalid password. Please ensure you are using your distinct Staff ID.")

def plot_radar(student_data, student_name):
    """Generates a Plotly radar chart for a student's PO1-PO11."""
    po_cols = [f"PO{i}" for i in range(1, 12)]
    
    values = []
    for col in po_cols:
        val = student_data.get(col, 0)
        values.append(0 if pd.isna(val) else val)
        
    values_closed = values + [values[0]]
    po_cols_closed = po_cols + [po_cols[0]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=po_cols_closed,
        fill='toself',
        name=student_name,
        line=dict(color='#1f77b4')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title=dict(text=f"PO Attainment: {student_name}", x=0.5)
    )
    return fig

def dashboard():
    """Renders the main dashboard for an authenticated lecturer."""
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"Welcome, {st.session_state['lecturer']}")
    with col2:
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()
        
    st.write("---")
    
    try:
        df = load_data()
    except Exception as e:
        st.error("Error loading data. Make sure 'PO Attainment Individual.xlsx' is in the root directory.")
        return
        
    st.subheader("👥 Build Your Advisee Roster")
    st.write("Filter by cohort and current semester, then select your assigned students.")
    
    # FILTER ROW: Cohort & Semester
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        cohort_list = ["All Cohorts"] + list(df['Cohort'].unique())
        selected_cohort = st.selectbox("Filter by Cohort:", cohort_list)
    with filter_col2:
        selected_semester = st.selectbox("Select Current Semester:", ["Part 1", "Part 2", "Part 3", "Part 4", "Part 5"])
    
    if selected_cohort != "All Cohorts":
        filtered_df = df[df['Cohort'] == selected_cohort]
    else:
        filtered_df = df
        
    filtered_df['Display Name'] = filtered_df['STD_NAME'] + " (" + filtered_df['STD_MTX'].astype(str) + ") - Cohort: " + filtered_df['Cohort']
    
    # STUDENT SELECTION DROPDOWN
    selected_students = st.multiselect(
        "Select your assigned students:",
        options=filtered_df['Display Name'].tolist()
    )
    
    if selected_students:
        st.write("### Advisee Radar Charts & Active Semester Action Plan")
        cols = st.columns(2)
        
        po_cols = [f"PO{i}" for i in range(1, 12)]
        
        for idx, student_display in enumerate(selected_students):
            student_row = filtered_df[filtered_df['Display Name'] == student_display].iloc[0]
            fig = plot_radar(student_row, student_row['STD_NAME'])
            
            with cols[idx % 2]:
                st.plotly_chart(fig, use_container_width=True)
                
                # WEAK PO IDENTIFICATION & SEMESTER-SPECIFIC SUGGESTIONS
                st.markdown(f"**Action Plan for {selected_semester}: {student_row['STD_NAME']}**")
                
                po_scores = pd.to_numeric(student_row[po_cols], errors='coerce').dropna()
                if not po_scores.empty:
                    lowest_pos = po_scores.nsmallest(3)
                    
                    for po, score in lowest_pos.items():
                        # Find subjects in the selected semester that map to this weak PO
                        semester_subjects = SEMESTER_MAPPING.get(selected_semester, {})
                        target_subjects = [subj for subj, target_pos in semester_subjects.items() if po in target_pos]
                        
                        if target_subjects:
                            subjects_str = ", ".join(target_subjects)
                        else:
                            subjects_str = f"No specific subjects in {selected_semester} map directly to {po}."
                            
                        st.info(f"**{po} (Current Score: {score:.2f}%)** \n\nTarget Subjects: {subjects_str}")
                else:
                    st.warning("No valid PO data available to generate suggestions.")

                with st.expander("View Raw Matrix Data"):
                    st.dataframe(student_row[po_cols].to_frame().T)
    else:
        st.info("Please select students from the dropdown to visualize their PO attainments.")

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        
    if not st.session_state['logged_in']:
        login()
    else:
        dashboard()

if __name__ == "__main__":
    main()