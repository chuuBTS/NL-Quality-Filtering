import json
import random
import pandas as pd
import streamlit as st
import time

# File paths
# DATA = "data/filtered_chart_types_result.json"
# ANNOTATION_RESULT_PATH = "data/annotation_result.json"
DATA = "data/filtered_result.json"
ANNOTATION_RESULT_PATH = "data/filtered_annotation_result.json"

# Set the page configuration
st.set_page_config(layout="centered")

# Load JSON data
with open(DATA, "r", encoding="utf-8") as file:
    data = json.load(file)

with open(ANNOTATION_RESULT_PATH, "r", encoding="utf-8") as file:
    annotation_data = json.load(file)

# 1. Navigation & Previouse/Next Buttons
# Convert keys to a list to use with index-based navigation
data_keys = list(data.keys())
# Randomly shuffle the data_keys list to randomize the order
random.seed(42)
random.shuffle(data_keys) 

# Initialize session state for index and toast if they don't exist
if "page_index" not in st.session_state:
    st.session_state.page_index = 0
    
if "show_toast" not in st.session_state:
    st.session_state.show_toast = False

# 在 Navigation 部分的代码之前添加筛选功能
st.sidebar.title("Filter Options")
filter_option = st.sidebar.radio(
    "Display Data",
    ["All", "Annotated", "Not Annotated"],
    index=0  # default to "All"
)

# 判断一个记录是否完整标注
def is_fully_annotated(filename, record, data):
    # 检查 NL 是否标注
    nl_annotated = "nl_type" in record and record["nl_type"] is not None
    
    # 检查所有图表是否标注
    charts_annotated = False
    if "charts" in record:
        total_charts = len(data[filename]["generated_chart_list"])
        annotated_charts = sum(
            1 for chart_data in record["charts"].values()
            if "chart_quality" in chart_data and chart_data["chart_quality"] is not None
        )
        charts_annotated = annotated_charts == total_charts
    
    return nl_annotated and charts_annotated

# 根据筛选选项过滤数据键
if filter_option == "Annotated":
    data_keys = [
        k for k in data.keys() 
        if k in annotation_data and is_fully_annotated(k, annotation_data[k], data)
    ]
elif filter_option == "Not Annotated":
    data_keys = [
        k for k in data.keys() 
        if k not in annotation_data or not is_fully_annotated(k, annotation_data[k], data)
    ]
else:  # "All"
    data_keys = list(data.keys())


# 随机打乱数据键的顺序（保持原有的随机种子）
random.seed(42)
random.shuffle(data_keys)

# 如果当前页面索引超出了筛选后的范围，重置为0
if st.session_state.page_index >= len(data_keys):
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
page = st.sidebar.selectbox(
    "Select Page", 
    data_keys, 
    index=min(st.session_state.page_index, len(data_keys)-1)
)

# 显示当前页面位置
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

# Get the annotation status for the current page
default_annotation = {
    "nl_type": None,
    "charts": {}
}
current_page_annotation = annotation_data.get(page, {})
current_page_annotation.update({k: v for k, v in default_annotation.items() if k not in current_page_annotation})

# Display the generated NL utterance
st.info(f"""{data[page]["nl_utterance"]}""", icon="🔊")

# Add text input for modifying NL utterance
modified_nl = st.text_area(
    "Modify NL Utterance",
    value=data[page]["nl_utterance"],
    height=68,
    key="nl_modifier"
)

# Add a submit button
if st.button("Submit Changes"):
    # Update the NL utterance in both data dictionaries
    data[page]["nl_utterance"] = modified_nl
    
    # Save the updated data back to the original JSON file
    with open(DATA, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    
    # Set flag to show toast after rerun
    st.session_state.show_toast = True
    st.rerun()

# Show toast notification if flag is set
if st.session_state.show_toast:
    st.toast('NL Utterance has been updated! 🎉', icon='✅')
    st.session_state.show_toast = False  # Reset the flag

# horizontal CSS for radio button layout
st.markdown("""
    <style>
    div[data-testid="stRadio"] > div { 
        display: flex;  /* 设置为弹性盒子布局 */
        flex-direction: row;  /* 横向排列选项 */
        gap: 15px;  /* 设置选项之间的间距 */
    }
    </style>
""", unsafe_allow_html=True)

# NL Utterance Type Radio Button 
nl_type_options = ["command", "question", "query", "other"]
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

# Update annotation status if any selection changes
if nl_type != current_page_annotation["nl_type"]:
    
    annotation_data[page] = {
        "nl_type": nl_type,
    }
    
    # Save the updated annotation status to annotation_result.json
    with open(ANNOTATION_RESULT_PATH, "w", encoding="utf-8") as file:
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
    # Iterate through the generated charts and display each chart with a label
    for chart_index, chart in enumerate(generated_chart_list):
        # Tabs for chart and JSON code
        charts_tab, json_tab = st.tabs(["📈 Chart & Annotation", "🗃 Vega-Lite JSON"])
        with charts_tab:
            # Display the chart and a radio button to label the chart
            charts_json_col, label_col = st.columns([2.3, 1])
            with charts_json_col:
                # Render Vega-Lite chart
                # st.vega_lite_chart(chart, use_container_width=True)
                st.vega_lite_chart(chart)
                
            with label_col:
                chart_quality_options = ["good", "poor", "Please select an option~"]
                chart_quality_index = (
                    chart_quality_options.index(current_page_annotation.get("charts", {}).get(str(chart_index), {}).get("chart_quality", None))
                    if current_page_annotation.get("charts", {}).get(str(chart_index), {}).get("chart_quality", None) in chart_quality_options else len(chart_quality_options) - 1
                )
                # Display radio button to label the chart (good/poor)
                chart_quality = st.radio(
                    f"Chart {chart_index + 1} Anotation", 
                    options = chart_quality_options, 
                    index = chart_quality_index, 
                    key=f"chart_quality_{chart_index}"  # Unique key for each chart's radio button
                )
                
                # Exclude the placeholder in the saved annotation
                chart_quality = None if chart_quality == "Please select an option~" else chart_quality
                
                chart_error_type_options = [
                    "empty", 
                    "duplicate", 
                    "bad aesthetics", 
                    "irrelevant data", 
                    "no sorting",
                    "meaningless",
                    "mismatched chart type", 
                    "Others"
                ]
                
                # If chart quality is marked as "poor", show the error type selection
                if chart_quality == "poor":
                    chart_error_types = st.multiselect(
                        f"Chart {chart_index + 1} Error Type", 
                        options=chart_error_type_options, 
                        default=current_page_annotation.get("charts", {}).get(str(chart_index), {}).get("error_type", [])  # Load previously saved error types
                    )
                else:
                    # Clear error types if chart quality is set to "good" or "empty"
                    chart_error_types = []
                
                # Update annotation status if any selection changes
                if (chart_quality != current_page_annotation.get("charts", {}).get(str(chart_index), {}).get("chart_quality", None) or 
                    chart_error_types != current_page_annotation.get("charts", {}).get(str(chart_index), {}).get("error_type", [])):
                    
                    annotation_data[page].setdefault("charts", {})
                    annotation_data[page]["charts"][str(chart_index)] = {
                        "chart_quality": chart_quality,
                        "error_type": chart_error_types
                    }
                    # Save the updated annotation status to annotation_result.json
                    with open(ANNOTATION_RESULT_PATH, "w", encoding="utf-8") as file:
                        json.dump(annotation_data, file, indent=4)
                    
                    st.rerun() 
                
        with json_tab:
            # Display JSON code for the chart
            st.json(chart)