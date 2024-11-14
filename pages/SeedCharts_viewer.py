import streamlit as st
import json
import glob
import os

# Set the page configuration
st.set_page_config(layout="centered")

# 定义函数来转换 JSON 中的值，并在顶层的 title 字段中添加 anchor 和 align 属性
def convert_json_values(json_data, in_root=True):
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == "title" and in_root and isinstance(value, (str, dict)):
                if isinstance(value, str):
                    json_data[key] = {
                        "text": value,
                        "anchor": "middle",
                        "align": "center"
                    }
                elif isinstance(value, dict):
                    value["anchor"] = "middle"
                    value["align"] = "center"
            if value is False:
                json_data[key] = False
            elif value is True:
                json_data[key] = True
            elif value is None:
                json_data[key] = None
            elif isinstance(value, (dict, list)):
                convert_json_values(value, False)
    elif isinstance(json_data, list):
        for index, item in enumerate(json_data):
            if item is False:
                json_data[index] = False
            elif item is True:
                json_data[index] = True
            elif item is None:
                json_data[index] = None
            elif isinstance(item, (dict, list)):
                convert_json_values(item, False)
    return json_data

# 读取所有以 origin.json 结尾的文件
chart_files = glob.glob("./chart_simplify/*origin.json")

# 获取文件名列表
chart_names = [os.path.basename(file) for file in chart_files]

# 初始化文件索引
if 'file_index' not in st.session_state:
    st.session_state.file_index = 0

if 'error_message' not in st.session_state:
    st.session_state.error_message = ''

def update_index():
    input_file = st.session_state.input_file
    if input_file in chart_names:
        st.session_state.file_index = chart_names.index(input_file)
        st.session_state.error_message = ''
    else:
        st.session_state.error_message = 'File not found!'

# 页面标题和帮助信息
st.title('Vega-Lite Charts Viewer')
st.caption("Use the dropdown menu or buttons to browse charts or enter a filename directly.")

# 侧边栏处理文件选择
with st.sidebar:
    # 处理文件选择
    selected_file = st.selectbox('Select or enter a filename:', chart_names, index=st.session_state.file_index, key='input_file')
    st.session_state.file_index = chart_names.index(selected_file)
    
    # 显示当前文件位置
    st.write(f"Currently viewing: <strong>{st.session_state.file_index + 1}/{len(chart_names)}<strong>", unsafe_allow_html=True)
    
#翻页
col1, col2, col3 = st.columns([1.5, 5.6, 1])
with col1:
    if st.button('⬅ Previous'):
        st.session_state.file_index = (st.session_state.file_index - 1) % len(chart_files)
        st.session_state.error_message = ''
with col3:
    if st.button('Next ➞'):
        st.session_state.file_index = (st.session_state.file_index + 1) % len(chart_files)
        st.session_state.error_message = ''

# 获取当前文件路径
current_file = chart_files[st.session_state.file_index]

# 加载当前文件的 JSON 数据
with open(current_file, 'r') as file:
    chart_json = json.load(file)

# 创建标签页
tab1, tab2 = st.tabs(["📈 Chart & NL", "🗃 Json"])

with tab2:
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
    else:
        st.json(chart_json)

with tab1:
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
    else:
        st.vega_lite_chart(convert_json_values(chart_json), use_container_width=True)