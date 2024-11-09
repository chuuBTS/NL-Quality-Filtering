import json
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
            if not isinstance(constraint["details"], list):
                constraint["details"] = [constraint["details"]]
        transform_constraints_df = pd.DataFrame(transform_constraints)
        st.table(transform_constraints_df)
    else:
        st.markdown("<p style='text-align: center; color: gray; font-style: italic;'>Transform Constraints is empty</p>", unsafe_allow_html=True)

# Mark Constraints Table in Tab 3
with tab3:
    mark_constraints = data[page].get("mark_constraints", [])
    if mark_constraints:
        for constraint in mark_constraints:
            if not isinstance(constraint["mark"], list):
                constraint["mark"] = [constraint["mark"]]
        mark_constraints_df = pd.DataFrame(mark_constraints)
        st.table(mark_constraints_df)
    else:
        st.markdown("<p style='text-align: center; color: gray; font-style: italic;'>Mark Constraints is empty</p>", unsafe_allow_html=True)


# 3. LLM Generated NL Utterance
st.header('LLM Generated NL Utterance')
st.info(f"""{data[page]["nl_utterance"]}""", icon="🔊")

# 4. Human Annotation
st.header('Human Annotation')

# Get the annotation status for the current page
page_annotation = annotation_data.get(page, {"nl_utterance_type": None, "nl_utterance_quality": None})

label_col1, label_col2 = st.columns([1, 1])
with label_col1:
    # NL Utterance Type Radio Button with Placeholder at the End
    nl_utterance_type_options = ["command", "question", "query", "other", "Please select an option~"]
    nl_utterance_type_index = (
        nl_utterance_type_options.index(page_annotation["nl_utterance_type"])
        if page_annotation["nl_utterance_type"] in nl_utterance_type_options else len(nl_utterance_type_options) - 1
    )
    nl_utterance_type = st.radio(
        "NL Utterance Type",
        options=nl_utterance_type_options,
        index=nl_utterance_type_index,
        label_visibility="visible"
    )
    # Exclude the placeholder in the saved annotation
    nl_utterance_type = None if nl_utterance_type == "Please select an option~" else nl_utterance_type

with label_col2:
    # NL Utterance Quality Radio Button with Placeholder at the End
    nl_utterance_quality_options = ["good", "poor", "Please select an option~"]
    nl_utterance_quality_index = (
        nl_utterance_quality_options.index(page_annotation["nl_utterance_quality"])
        if page_annotation["nl_utterance_quality"] in nl_utterance_quality_options else len(nl_utterance_quality_options) - 1
    )
    nl_utterance_quality = st.radio(
        "NL Utterance Quality",
        options=nl_utterance_quality_options,
        index=nl_utterance_quality_index,
        label_visibility="visible"
    )
    # Exclude the placeholder in the saved annotation
    nl_utterance_quality = None if nl_utterance_quality == "Please select an option~" else nl_utterance_quality

# Initialize error type choices
error_type_options = [
    "NL lacks Encoded Fields", 
    "NL lacks Transform Constraints", 
    "NL lacks Mark Constraints", 
    "NL lacks Task Constraints", 
    "NL has redundant information", 
    "Conflict intent", 
    "Others"
]

# If quality is marked as "poor", show the error type selection
if nl_utterance_quality == "poor":
    selected_error_types = st.multiselect(
        "Error type", 
        options=error_type_options, 
        default=page_annotation.get("error_type", [])  # Load previously saved error types
    )
        
else:
    # Clear error types if quality is set to "good"
    selected_error_types = []

# Update annotation status if any selection changes
if (nl_utterance_type != page_annotation["nl_utterance_type"] or 
    nl_utterance_quality != page_annotation["nl_utterance_quality"] or 
    selected_error_types != page_annotation.get("error_type", [])):
    
    annotation_data[page] = {
        "nl_utterance_type": nl_utterance_type,
        "nl_utterance_quality": nl_utterance_quality,
        "error_type": selected_error_types
    }
    
    # Save the updated annotation status to annotation_result.json
    with open("data/annotation_result.json", "w", encoding="utf-8") as file:
        json.dump(annotation_data, file, indent=4)
    
    st.rerun()

