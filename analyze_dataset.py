import os
import json
from collections import defaultdict

def get_json_files(folder_path):
    """获取所有JSON文件的数据"""
    files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    json_data = []
    for file in files:
        try:
            with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 从gpt_result中获取数据
                if isinstance(data, dict) and 'gpt_result' in data:
                    gpt_result = data['gpt_result']
                    # 如果gpt_result是字符串，尝试解析它
                    if isinstance(gpt_result, str):
                        try:
                            gpt_result = json.loads(gpt_result)
                        except json.JSONDecodeError:
                            print(f"Warning: 无法解析gpt_result字符串: {file}")
                            continue
                    json_data.append(gpt_result)
                    
                    # 打印前几个文件的数据结构
                    if len(json_data) < 2:
                        print(f"\n=== 文件 {file} 的数据结构 ===")
                        print(f"原始数据类型: {type(data)}")
                        print(f"gpt_result数据类型: {type(gpt_result)}")
                        print(f"gpt_result内容: {str(gpt_result)[:200]}")
        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")
            continue
            
    return json_data, len(files)

def analyze_encoded_fields(json_data, total_files):
    """分析encoded_fields中field字段的统计"""
    
    # 原有的统计代码，添加类型检查
    field_list_files = sum(1 for data in json_data 
                          if isinstance(data, dict) 
                          and isinstance(data.get('encoded_fields'), list)
                          and any(isinstance(field_info, dict) 
                                and isinstance(field_info.get('field'), list)
                                for field_info in data['encoded_fields']))
    
    print(f"\n=== Fields Info 统计 ===")
    print(f"包含field为list的文件数: {field_list_files}/{total_files}，{field_list_files/total_files:.2%}")

    # 打印对应的field和文件名
    for data in json_data:
        if isinstance(data, dict) and 'encoded_fields' in data:
            for field_info in data['encoded_fields']:
                if isinstance(field_info, dict) and isinstance(field_info.get('field'), list):
                    print(f"文件名: {data.get('file_name', '未知文件')}，field: {field_info['field']}")

def analyze_constraints(json_data, total_files):
    """分析constraints中c_type不同取值的分布"""
    c_type_dist = defaultdict(int)
    nl_ref_type_dist = defaultdict(int)
    non_empty_count = sum(1 for data in json_data 
                         if isinstance(data, dict) and data.get('constraints'))
    empty_count = total_files - non_empty_count
    total_constraints = 0
    
    for data in json_data:
        if not isinstance(data, dict):
            continue
        constraints = data.get('constraints', [])
        if not isinstance(constraints, list):
            continue
            
        total_constraints += len(constraints)
        for ref in constraints:
            if not isinstance(ref, dict):
                continue
            if ref.get('c_type'):
                c_type_dist[ref['c_type']] += 1
            nl_ref_type_dist[ref.get('nl_ref_type', 'unknown')] += 1

    print(f"\n=== Refer Others 统计 ===")
    print(f"constraints为空的文件数: {empty_count}/{total_files}，{empty_count/total_files:.2%}")
    print(f"constraints不为空的文件数: {non_empty_count}/{total_files}，{non_empty_count/total_files:.2%}")
    print(f"constraints对象总数: {total_constraints}")
    print(f"\nc_type分布:")
    for c_type, count in c_type_dist.items():
        print(f"  {c_type}: {count}/{total_constraints}，{count/total_constraints:.2%}")
    
    print(f"\nnl_ref_type分布:")
    for type_name, count in nl_ref_type_dist.items():
        print(f"  {type_name}: {count}/{total_constraints}，{count/total_constraints:.2%}")

def analyze_constraints_by_type(json_data, c_type):
    """分析constraints中特定c_type类型的统计
    
    Args:
        json_data: JSON数据列表
        c_type: 要分析的类型 (mark/task/transform)
    """
    c_type_count = 0
    name_dist = defaultdict(int)
    
    for data in json_data:
        for info in data.get('constraints', []):
            if info.get('c_type') == c_type:
                c_type_count += 1
                name_dist[info.get('c_name', 'unknown')] += 1
    
    print(f"\n=== Others Info {c_type.capitalize()}类型统计 ===")
    print(f"{c_type}类型总数: {c_type_count}")
    print("c_name分布:")
    for name, count in name_dist.items():
        print(f"  {name}: {count}/{c_type_count}，{count/c_type_count:.2%}")

def main():
    folder_path = 'generated_nl_gpt_json'
    json_data, total_files = get_json_files(folder_path)
    
    analyze_encoded_fields(json_data, total_files)
    analyze_constraints(json_data, total_files)
    
    for c_type in ['mark', 'task', 'transform']:
        analyze_constraints_by_type(json_data, c_type)

if __name__ == '__main__':
    main()