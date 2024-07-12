import streamlit as st
import json
import glob
import os
import pandas as pd

# 读取所有以 .json 结尾的文件
result_files = glob.glob("./generated_nl_gpt_json/*.json")

# 获取文件名列表
result_names = [os.path.basename(file) for file in result_files]

# 初始化文件索引
if 'file_index' not in st.session_state:
    st.session_state.file_index = 0

if 'error_message' not in st.session_state:
    st.session_state.error_message = ''

def update_index():
    input_file = st.session_state.input_file
    if input_file in result_names:
        st.session_state.file_index = result_names.index(input_file)
        st.session_state.error_message = ''
    else:
        st.session_state.error_message = 'File not found!'

# 页面标题和帮助信息
st.title('NL Quality Filtering')
st.caption("Please carefully review the NL Utterance to ensure it accurately includes all relevant information.")
# 添加横线
st.markdown(
    """
    <style>
    hr.custom-hr {
        margin-top: 0px;
        margin-bottom: 20px;
    }
    </style>
    <hr class="custom-hr">
    """, 
    unsafe_allow_html=True
)

# 侧边栏处理文件选择
with st.sidebar:
    # 处理文件选择
    selected_file = st.selectbox('Select or enter a filename:', result_names, index=st.session_state.file_index, key='input_file')
    st.session_state.file_index = result_names.index(selected_file)
    
    # 显示当前文件位置
    st.write(f"Currently viewing: <strong>{st.session_state.file_index + 1}/{len(result_names)}</strong>", unsafe_allow_html=True)
    
# 翻页
col1, col2, col3 = st.columns([1.5, 5.6, 1])
with col1:
    if st.button('⬅ Previous'):
        st.session_state.file_index = (st.session_state.file_index - 1) % len(result_files)
        st.session_state.error_message = ''
with col3:
    if st.button('Next ➞'):
        st.session_state.file_index = (st.session_state.file_index + 1) % len(result_files)
        st.session_state.error_message = ''

# 获取当前文件路径
current_file = result_files[st.session_state.file_index]

# 加载当前文件的 JSON 数据
with open(current_file, 'r') as file:
    result_json = json.load(file)

# 加载另一个目录中的同名文件以统计charts数量
corresponding_file = f"./upload_dataset_task_1_new/{os.path.basename(current_file)}"
if os.path.exists(corresponding_file):
    with open(corresponding_file, 'r') as file:
        corresponding_json = json.load(file)
    chart_count = len(corresponding_json.get("generated_chart_list", []))
else:
    chart_count = 0

left, right = st.columns([2,1])

with left:
    # 展示 nl_utterance
    st.subheader("NL Utterance")
    st.info(f"""{result_json["gpt_result"]["nl_utterance"]}""")

with right:
    container = st.container(border=True)
# container.write(f'<p style="font-size:18px; ">{result_json["gpt_result"]["nl_utterance"]}</p>', unsafe_allow_html=True)

# 添加单选框
quality_options = ["Good", "Average", "Poor", "Not Labeled"]
# 只在初始加载时设置 current_quality
if 'current_quality' not in st.session_state:
    st.session_state.current_quality = result_json.get("quality_label", "Not Labeled")
selected_quality = container.radio("Quality Label", quality_options, index=quality_options.index(st.session_state.current_quality))

if selected_quality != st.session_state.current_quality:
    if selected_quality == "Not Labeled":
        result_json.pop("quality_label", None)
    else:
        result_json["quality_label"] = selected_quality
    with open(current_file, 'w') as file:
        json.dump(result_json, file, indent=4)
    st.toast(f'Quality labeled as {selected_quality} successfully!', icon='🎉')
    
st.subheader("relevant information")
# 展示对应charts的数量
st.markdown(f'<p style="font-size:18px; font-style:italic;">Number of charts: {chart_count}</p>', unsafe_allow_html=True)

# 创建标签页
tab1, tab2, tab3 = st.tabs(["Encoded Fields", "Transform Constraints", "Mark Constraints"])

with tab1:
    # 提取并展示 encoded_fields 表格
    encoded_fields_data = [
        {"field": field["field"], "nl_ref_phrase": field["nl_ref_phrase"]}
        for field in result_json["gpt_result"]["encoded_fields"]
    ]
    encoded_fields_df = pd.DataFrame(encoded_fields_data)
    # st.markdown('<p style="font-size:20px; font-style:italic;">Encoded Fields:</p>', unsafe_allow_html=True)
    st.table(encoded_fields_df)

with tab2:
    # 提取并展示 transform 表格
    transform_data = []
    for constraint in result_json["gpt_result"]["constraints"]:
        if constraint["c_type"] == "transform":
            other_info = []
            for item in constraint["c_list"]:
                if "oneOf" in item:
                    other_info.extend(item["oneOf"])
                if "aggregate" in item:
                    other_info.append(item["aggregate"])
                if "order" in item:
                    other_info.append(item["order"])
            transform_data.append({
                "c_name": constraint["c_name"],
                "field": item.get("field", "N/A"),
                "other_info": ", ".join(other_info),
                "nl_ref_phrase": constraint["nl_ref_phrase"]
            })

    transform_df = pd.DataFrame(transform_data)
    # st.markdown('<p style="font-size:20px; font-style:italic;">Transform Constraints:</p>', unsafe_allow_html=True)
    st.table(transform_df)

with tab3:
    # 提取并展示 mark 表格
    mark_data = [
        {"c_name": constraint["c_name"], "nl_ref_phrase": constraint["nl_ref_phrase"]}
        for constraint in result_json["gpt_result"]["constraints"]
        if constraint["c_type"] == "mark"
    ]
    mark_df = pd.DataFrame(mark_data)
    # st.markdown('<p style="font-size:20px; font-style:italic;">Mark Constraints:</p>', unsafe_allow_html=True)
    st.table(mark_df)

