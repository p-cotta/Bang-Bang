import streamlit as st
import pandas as pd
import json 
import os   
st.set_page_config(
    page_title="Marathon Training",
    page_icon="🏃‍",
    layout="wide"
)
st.title("Your Weekly Mileage For Marathon Training 📈")
st.write("This page visualizes the mileage you submitted as well as your daily recommended mileage.")
@st.cache_data
def loadData():
    submission_data = pd.DataFrame()
    recommended_miles_list = [] 
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(app_root, "data.csv")
    json_path = os.path.join(app_root, "data.json")
    try:
        if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
            submission_data = pd.read_csv(csv_path, encoding="utf-8-sig")
            submission_data['Value'] = pd.to_numeric(submission_data['Value'], errors='coerce')
            submission_data.dropna(subset=['Value'], inplace=True)
            submission_data = submission_data.reset_index(drop=True)
            st.success(f"Loaded {len(submission_data)} exercise submissions from data.csv.")
        else:
            st.info("No submissions found yet. Fill out the Survey page!")
    except Exception as e:
        st.error(f"Error reading survey data: {e}")
    try:
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                json_content = json.load(f)
            recommended_miles_list = json_content.get("recommended_miles", [])
            st.success("Loaded recommended miles targets from data.json.")
    except Exception as e:
        st.error(f"Error reading JSON data: {e}")
    return submission_data, recommended_miles_list
submissions_df, recommended_miles_data = loadData()
st.divider()


# GRAPH 1: STATIC (Miles Run per Day - Bar Chart)
# Uses CSV Data, Shows total mileage per day based off the inputs

st.header("Graph 1: Total Mileage By Daily")
st.write("Shows the portion of Total mileage for the week run on each day.")
if not submissions_df.empty:
    # Prepare data: Group by 'Category' (Day) and SUM the 'Value' (Mileage) column
    category_totals = submissions_df.groupby('Category')['Value'].sum().reset_index()
    category_totals.columns = ['Day', 'Total Mileage']
    category_totals = category_totals.set_index('Day')
    st.bar_chart(category_totals)  #NEW Creates a bar chart
else:
    st.warning("Cannot generate Graph 1: CSV data is empty.")
st.divider()


# GRAPH 2: DYNAMIC (Single Day Mileage- Line)
# Uses CSV Data, User selects an individual day and is then shown the mileage that they inputted for that day.
#Select a day from the dropdown menu, the graph then displays a point showing the mileage ran on that day.

st.header("Graph 2: Individual Day Mileage")
st.write("Use the dropdown menu to select a day and display your mileage!")
if not submissions_df.empty:
    available_categories = submissions_df['Category'].unique().tolist()
    if 'activity_trend_select' not in st.session_state:
        st.session_state.activity_trend_select = available_categories[0] if available_categories else None
    default_index = available_categories.index(st.session_state.activity_trend_select) if st.session_state.activity_trend_select in available_categories else 0
    selected_activity = st.selectbox( #NEW Creates a dropdown menu for a user to select a single option.
        '**Select one day to view its trend:**',
        options=available_categories,
        index=default_index, 
        key='activity_trend_select' 
    )
    trend_data = submissions_df[submissions_df['Category'] == selected_activity].reset_index()
    trend_data = trend_data[['Value']]
    st.line_chart(trend_data)  #NEW Creates a Line chart
else:
    st.warning("Cannot generate Dynamic Graph 2: CSV data is empty.")
st.divider()


# GRAPH 3: DYNAMIC (Recommended Mileage from JSON - BAR CHART)
# Requirement:Uses JSON Data, User selects multiple days to show multiple bars displaying recommended mileage for selected days.
# Select One or more days, and a bar will display on the bar graph which shows the mileage that you ran on each of those days.

st.header("Graph 3: Recommended Mileage Targets")
st.write("Use the multiselect filter to one or more days to display your recommended mileage!")
if recommended_miles_data:
    try:
        miles_df = pd.DataFrame(recommended_miles_data)
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        miles_df['Day'] = pd.Categorical(miles_df['Day'], categories=day_order, ordered=True)
        miles_df = miles_df.sort_values('Day')
    except Exception as e:
        st.error(f"JSON Structure incorrect. Error: {e}")
        miles_df = pd.DataFrame()
    if not miles_df.empty:
        if 'filtered_days_json' not in st.session_state:
            st.session_state.filtered_days_json = miles_df['Day'].unique().tolist() #NEW stores the variable across app reruns using streamlit session state
        selected_days_from_widget = st.multiselect( #NEW- Creates a multi-select dropdown menu for a user to days to display their recommended mileage
            'Select one or more days to display recommended mileage:',
            options=miles_df['Day'].unique().tolist(),
            default=st.session_state.filtered_days_json,
            key='day_filter_widget_g3' 
        )
        st.session_state.filtered_days_json = selected_days_from_widget
        final_data_to_plot = miles_df[miles_df['Day'].isin(st.session_state.filtered_days_json)]
        final_data_to_plot = final_data_to_plot.set_index('Day')[['Recommended']]
        st.bar_chart(final_data_to_plot)  #NEW Creates a Bar chart
else:
    st.warning("Cannot generate Graph 3: JSON empty or invalid.")
