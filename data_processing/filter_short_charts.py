#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path

def filter_short_charts(input_path, output_path, annotation_path, filtered_annotation_path):    
    # 读取filtered_chart_types_result.json文件
    filtered_keys = set()
    filtered_data = {}
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
            # 遍历每个key-value对
            for key, value in input_data.items():
                # 如果generated_chart_list长度大于5，保留这个key和数据
                if len(value.get('generated_chart_list', [])) <= 5:
                    filtered_keys.add(key)
                    filtered_data[key] = value
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")
    # 保存过滤后的chart数据结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)
    
    
    # 读取annotation_result.json
    with open(annotation_path, 'r', encoding='utf-8') as f:
        annotation_data = json.load(f)
    # 根据filtered_keys过滤annotation_result
    filtered_annotation = {
        k: v for k, v in annotation_data.items()
        if k in filtered_keys
    }   
    # 保存过滤后的annotation结果
    with open(filtered_annotation_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_annotation, f, ensure_ascii=False, indent=4)
    
    print(f"原始数据条数: {len(annotation_data)}")
    print(f"原始chart数据条数: {len(input_data)}")
    print(f"过滤后数据条数: {len(filtered_annotation)}")
    print(f"过滤后chart数据条数: {len(filtered_data)}")
    print(f"结果已保存到: {output_path} 和 {filtered_annotation_path}")

if __name__ == '__main__':
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent
    
    # 设置输入输出路径
    input_path = root_dir / 'data' / 'filtered_chart_types_result.json'
    output_path = root_dir / 'data' / 'filtered_long_charts_result.json'
    annotation_path = root_dir / 'data' / 'annotation_result.json'
    filtered_annotation_path = root_dir / 'data' / 'filtered_long_charts_annotation_result.json'
    
    filter_short_charts(input_path, output_path, annotation_path, filtered_annotation_path)