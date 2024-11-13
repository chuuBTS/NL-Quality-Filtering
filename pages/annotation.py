import json
import random
import pandas as pd
import streamlit as st

# Load JSON data
with open("data/merged_result.json", "r", encoding="utf-8") as file:
    data = json.load(file)

with open("data/annotation_result.json", "r", encoding="utf-8") as file:
    annotation_data = json.load(file)

# 1. Navigation & Previouse/Next Buttons
# Convert keys to a list to use with index-based navigation
data_keys = list(data.keys())
# Randomly shuffle the data_keys list to randomize the order
random.seed(42)
random.shuffle(data_keys) 

# Initialize session state for index if it doesn't exist
if "page_index" not in st.session_state:
    st.session_state.page_index = 0

# Update page index based on button clicks
col1, col2, col3 = st.columns([1.5, 5.6, 1])
with col1:
    if st.button("⬅ Previous"):
        # If on the first page, go to the last page
        if st.session_state.page_index == 0:
            st.session_state.page_index = len(data_keys) - 1
        else:
            st.session_state.page_index -= 1
with col3:
    if st.button("Next ➞"):
        # If on the last page, go back to the first page
        if st.session_state.page_index == len(data_keys) - 1:
            st.session_state.page_index = 0
        else:
            st.session_state.page_index += 1

# Get the current key based on page index
page = data_keys[st.session_state.page_index]
# Update the page index when a selection is made in the sidebar
st.session_state.page_index = data_keys.index(page)


# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select Page", data_keys, index=st.session_state.page_index)
# If the selected page in the sidebar is different from the current `page_index`, update it
new_page_index = data_keys.index(page)
if new_page_index != st.session_state.page_index:
    st.session_state.page_index = new_page_index  # Update the page index
    st.rerun()  # Rerun the app to update the page

st.sidebar.markdown(
    f"Current Page: <span style='color:red; font-weight:bold'>{st.session_state.page_index + 1} / {len(data_keys)}</span>",
    unsafe_allow_html=True
)

# 2. Input Intent
st.header('Input Intent')
# Tabs for different constraint types
tab1, tab2, tab3 = st.tabs(["Encoded Fields", "Transform Constraints", "Mark & Task Constraints"])

# Encoded Fields Table in Tab 1
with tab1:
    for entry in data[page]["encoded_fields"]:
        if isinstance(entry["field"], list):
            entry["field"] = ", ".join(entry["field"])
    encoded_fields_df = pd.DataFrame(data[page]["encoded_fields"])
    if not encoded_fields_df.empty:
        st.table(encoded_fields_df)
    else:
        st.markdown("<p style='text-align: center; color: gray; font-style: italic;'>Encoded Fields is empty</p>", unsafe_allow_html=True)

# Transform Constraints Table in Tab 2
with tab2:
    transform_constraints = data[page].get("transform_constraints", [])
    if transform_constraints:
        for constraint in transform_constraints:
            if isinstance(constraint.get("details"), list):
                constraint["details"] = ", ".join(constraint["details"])
        transform_constraints_df = pd.DataFrame(transform_constraints)
        st.table(transform_constraints_df)
    else:
        st.markdown("<p style='text-align: center; color: gray; font-style: italic;'>Transform Constraints is empty</p>", unsafe_allow_html=True)

# Mark Constraints Table in Tab 3
with tab3:
    mark_constraints = data[page].get("mark_constraints", [])
    if mark_constraints:
        for constraint in mark_constraints:
            if isinstance(constraint.get("mark"), list):
                constraint["mark"] = ", ".join(constraint["mark"])
        mark_constraints_df = pd.DataFrame(mark_constraints)
        st.table(mark_constraints_df)
    else:
        st.markdown("<p style='text-align: center; color: gray; font-style: italic;'>Mark Constraints is empty</p>", unsafe_allow_html=True)


st.header('Human Annotation')
# 3. LLM Generated NL Utterance
st.markdown('<h4 style="color:green;">LLM Generated NL Utterance</h3>', unsafe_allow_html=True)
st.info(f"""{data[page]["nl_utterance"]}""", icon="🔊")

# Get the annotation status for the current page
current_page_annotation = annotation_data.get(page, {"nl_type": None, "nl_quality": None, "nl_error_type": [], "chart_annotation": {}})

label_col1, label_col2 = st.columns([1, 1])
with label_col1:
    # NL Utterance Type Radio Button with Placeholder at the End
    nl_type_options = ["command", "question", "query", "other", "Please select an option~"]
    nl_type_index = (
        nl_type_options.index(current_page_annotation["nl_type"])
        if current_page_annotation["nl_type"] in nl_type_options else len(nl_type_options) - 1
    )
    nl_type = st.radio(
        "NL Utterance Type",
        options=nl_type_options,
        index=nl_type_index,
        label_visibility="visible"
    )
    # Exclude the placeholder in the saved annotation
    nl_type = None if nl_type == "Please select an option~" else nl_type

with label_col2:
    # NL Utterance Quality Radio Button with Placeholder at the End
    nl_quality_options = ["good", "poor", "Please select an option~"]
    nl_quality_index = (
        nl_quality_options.index(current_page_annotation["nl_quality"])
        if current_page_annotation["nl_quality"] in nl_quality_options else len(nl_quality_options) - 1
    )
    nl_quality = st.radio(
        "NL Utterance Quality",
        options=nl_quality_options,
        index=nl_quality_index,
        label_visibility="visible"
    )
    # Exclude the placeholder in the saved annotation
    nl_quality = None if nl_quality == "Please select an option~" else nl_quality

# Initialize error type choices
nl_error_type_options = [
    "NL lacks Encoded Fields", 
    "NL lacks Transform Constraints", 
    "NL lacks Mark Constraints", 
    "NL lacks Task Constraints", 
    "NL has redundant information", 
    "Conflict intent", 
    "Others"
]

# If quality is marked as "poor", show the error type selection
if nl_quality == "poor":
    nl_error_types = st.multiselect(
        "Error type", 
        options=nl_error_type_options, 
        default=current_page_annotation.get("nl_error_type", [])  # Load previously saved error types
    )
        
else:
    # Clear error types if quality is set to "good"
    nl_error_types = []

# Update annotation status if any selection changes
if (nl_type != current_page_annotation["nl_type"] or 
    nl_quality != current_page_annotation["nl_quality"] or 
    nl_error_types != current_page_annotation.get("nl_error_type", [])):
    
    annotation_data[page] = {
        "nl_type": nl_type,
        "nl_quality": nl_quality,
        "nl_error_type": nl_error_types
    }
    
    # Save the updated annotation status to annotation_result.json
    with open("data/annotation_result.json", "w", encoding="utf-8") as file:
        json.dump(annotation_data, file, indent=4)
    
    st.rerun()


# 4. Display Generated Charts and Annotation
st.markdown('<h4 style="color:green;">Charts</h3>', unsafe_allow_html=True)

# Load generated chart list from the data
generated_chart_list = data[page].get("generated_chart_list", [])
# Display total number of charts
st.warning(f"""Total Generated Charts: {len(generated_chart_list)}""", icon="📊")
#st.markdown(f"<p style='font-weight:bold;'>Total Generated Charts: {len(generated_chart_list)}</p>", unsafe_allow_html=True)
if generated_chart_list:
    # Iterate through the generated charts and display each chart with a label (good/poor)
    for chart_index, chart in enumerate(generated_chart_list):
        charts_col, label_col = st.columns([2, 1])
        with charts_col:
            # Render Vega-Lite chart
            st.vega_lite_chart(chart)
        with label_col:
            chart_annotation_options = ["good", "empty", "bad aesthetics", "duplicate", "irrelevant", "too complex", "Please select an option~"]
            chart_annotation_index = (
                chart_annotation_options.index(current_page_annotation.get("chart_annotation", {}).get(str(chart_index), None))
                if current_page_annotation.get("chart_annotation", {}).get(str(chart_index), None) in chart_annotation_options else len(chart_annotation_options) - 1
            )
            # Display radio button to label the chart (good/poor)
            chart_annotation = st.radio(
                f"Chart {chart_index + 1} Anotation", 
                options = chart_annotation_options, 
                index = chart_annotation_index, 
                key=f"chart_annotation_{chart_index}"  # Unique key for each chart's radio button
            )
            
            # Exclude the placeholder in the saved annotation
            chart_annotation = None if chart_annotation == "Please select an option~" else chart_annotation
            
            if chart_annotation != current_page_annotation.get("chart_annotation", {}).get(str(chart_index), None):
                # Save the chart quality and error types to the annotation data 
                annotation_data[page].setdefault("chart_annotation", {})
                annotation_data[page]["chart_annotation"][str(chart_index)] = chart_annotation
                # Save the updated annotation status to annotation_result.json
                with open("data/annotation_result.json", "w", encoding="utf-8") as file:
                    json.dump(annotation_data, file, indent=4)
                
                st.rerun()
