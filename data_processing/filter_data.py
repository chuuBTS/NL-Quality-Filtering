import json
import os
from pathlib import Path

def filter_mismatched_chart_types(data):
    """
    过滤不匹配的图表类型，并打印不匹配的详细信息
    """
    # 创建一个副本以避免修改原始数据
    filtered_data = data.copy()
    keys_to_remove = []  # 用于跟踪需要删除的键
    
    # 用于统计不匹配情况
    mismatch_count = 0
    
    for key, value in filtered_data.items():
        # 获取gpt_result中的constraints
        gpt_result = value.get('gpt_result', {})
        constraints = gpt_result.get('constraints', [])
        mark_list = []
        
        # 从constraints中提取mark约束
        for constraint in constraints:
            if constraint.get('c_type') == 'mark':
                mark = constraint.get('c_name')
                if isinstance(mark, list):
                    mark_list.extend(mark)
                elif isinstance(mark, str):
                    mark_list.append(mark)  # 如果是字符串，直接添加

        # 如果没有mark约束，跳过当前数据
        if not mark_list:
            continue

        # 过滤charts并记录不匹配情况
        valid_charts = []
        invalid_charts = []
        for chart_idx, chart in enumerate(value.get('generated_chart_list', [])):
            chart_mark = chart.get('mark')
            if chart_mark in mark_list:
                valid_charts.append(chart)
            else:
                mismatch_count += 1
                invalid_charts.append({
                    'chart_index': chart_idx,
                    'required_marks': mark_list,
                    'actual_mark': chart_mark
                })
        
        # 如果有不匹配的图表，打印详细信息
        if invalid_charts:
            print(f"\n文件: {key}")
            print(f"要求的mark类型: {mark_list}")
            print("不匹配的图表:")
            for invalid_chart in invalid_charts:
                print(f"  - 图表 {invalid_chart['chart_index']}: "
                      f"实际类型 = {invalid_chart['actual_mark']}")
            print("-" * 40)
        
        # 如果没有有效的charts，标记为删除
        if not valid_charts:
            keys_to_remove.append(key)
        else:
            # 更新generated_chart_list为有效的charts
            value['generated_chart_list'] = valid_charts
    
    # 删除没有有效charts的entries
    for key in keys_to_remove:
        del filtered_data[key]
    
    print(f"\n总计发现 {mismatch_count} 个不匹配的图表")
    print(f"删除了 {len(keys_to_remove)} 个没有有效图表的记录")
    
    return filtered_data

def filter_short_charts(data, max_charts=5):
    """
    过滤chart数量小于等于max_charts的数据
    """
    return {
        key: value 
        for key, value in data.items() 
        if len(value.get('generated_chart_list', [])) <= max_charts
    }

def filter_annotations(annotation_data, filtered_data_keys):
    """
    根据过滤后的数据keys过滤annotation文件
    """
    return {
        key: value 
        for key, value in annotation_data.items() 
        if key in filtered_data_keys
    }

def main():
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent
    
    # 设置输入输出路径
    merged_file = root_dir / 'data' / 'merged_result.json'
    filtered_file = root_dir / 'data' / 'filtered_result1.json'
    
    # annotation_file = root_dir / 'data' / 'filtered_annotation_result.json'
    # filtered_annotation_file = root_dir / 'data' / 'filtered_annotation_result1.json'

    # 1. 读取原始数据
    print("开始处理数据...")
    with open(merged_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"原始数据条数: {len(data)}")

    # 2. 过滤不匹配的图表类型
    filtered_by_types = filter_mismatched_chart_types(data)
    print(f"图表类型过滤后数据条数: {len(filtered_by_types)}")

    # 3. 过滤长charts
    filtered_data = filter_short_charts(filtered_by_types)
    print(f"图表数量过滤后数据条数: {len(filtered_data)}")
    
    # 保存过滤结果
    with open(filtered_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=4, ensure_ascii=False)

    # 4. 过滤annotations
    # try:
    #     with open(annotation_file, 'r', encoding='utf-8') as f:
    #         annotation_data = json.load(f)
    #     print(f"原始标注数据条数: {len(annotation_data)}")
        
    #     filtered_annotations = filter_annotations(annotation_data, filtered_data.keys())
    #     print(f"过滤后标注数据条数: {len(filtered_annotations)}")
        
    #     # 保存过滤后的annotations
    #     with open(filtered_annotation_file, 'w', encoding='utf-8') as f:
    #         json.dump(filtered_annotations, f, indent=4, ensure_ascii=False)
            
    # except Exception as e:
    #     print(f"处理标注文件时出错: {str(e)}")

    print(f"\n处理完成！")
    print(f"过滤后的数据保存在: {filtered_file}")
    # print(f"过滤后的标注数据保存在: {filtered_annotation_file}")

if __name__ == '__main__':
    main() 