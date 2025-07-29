import json
import pandas as pd
import os
from pathlib import Path

def load_json_file(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def get_good_charts_data(csv_path, filtered_result_path, original_data_dir, generated_nl_gpt_json_dir, output_path):
    """
    处理和整合数据
    
    Args:
        csv_path: annotated_nl_charts_pairs.csv的路径
        filtered_result_path: filtered_result.json的路径
        original_data_dir: 原始数据集目录路径
        output_path: 输出文件路径
    """
    # 读取CSV文件
    df = pd.read_csv(csv_path)
    
    # 筛选good_charts_count > 1的数据
    filtered_df = df[df['good_charts_count'] > 1]
    
    # 读取filtered_result.json
    filtered_result = load_json_file(filtered_result_path)
    
    # 最终结果字典
    result_data = {}
    
    for _, row in filtered_df.iterrows():
        filename = row['filename']
        good_indices = [int(idx.strip()) for idx in row['good_charts_indices'].split(',')]
        
        # 获取filtered_result.json中的数据
        if filename in filtered_result:
            file_data = filtered_result[filename]
            # 1.获取nl_utterance
            nl_utterance = file_data.get('nl_utterance', '')
            
            # 2.获取generated_chart_list
            generated_charts = file_data.get('generated_chart_list', [])
            good_generated_charts = [generated_charts[i] for i in good_indices if i < len(generated_charts)] # 只保留good的charts
            
            # 3.获取原始数据集中的table_info
            original_json_path = os.path.join(original_data_dir, filename)
            original_data = load_json_file(original_json_path)
            table_info = original_data.get('table_info', {}) if original_data else {}
            
            # 4.获取原始数据集中的refer_fileds, refer_others
            generated_nl_gpt_json_path = os.path.join(generated_nl_gpt_json_dir, filename)
            generated_nl_gpt_json = load_json_file(generated_nl_gpt_json_path)
            refer_fileds = generated_nl_gpt_json.get('gpt_result', []).get('encoded_fields', []) if generated_nl_gpt_json else []
            refer_others = generated_nl_gpt_json.get('gpt_result', []).get('constraints', []) if generated_nl_gpt_json else []

            # 4.构建结果对象
            result_data[filename] = {
                'nl_utterance': nl_utterance,
                'table_info': table_info,
                'fileds_info': refer_fileds,
                'others_info': refer_others,
                'good_generated_chart_list': good_generated_charts
            }
    
    # 保存结果到JSON文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=4, ensure_ascii=False)
    
    print(f"处理完成，共处理了 {len(result_data)} 个文件")
    print(f"结果已保存到 {output_path}")
    
    return result_data

if __name__ == '__main__':
    # 配置路径
    BASE_DIR = Path(__file__).parent.parent  # 项目根目录
    
    config = {
        'csv_path': BASE_DIR / 'eval' / 'raw_data' / 'annotated_nl_charts_pairs.csv',
        'filtered_result_path': BASE_DIR / 'data' / 'filtered_result.json',
        'original_data_dir': BASE_DIR / 'upload_dataset_task_1_new',
        "generated_nl_gpt_json_dir": BASE_DIR / 'generated_nl_gpt_json',
        'output_path': BASE_DIR / 'eval' / 'raw_data' / 'test_data.json'
    }
    
    # 确保所有输入文件都存在
    for key, path in config.items():
        if key != 'output_path' and not path.exists():
            raise FileNotFoundError(f"找不到文件: {path}")
    
    # 运行数据处理
    result = get_good_charts_data(
        csv_path=config['csv_path'],
        filtered_result_path=config['filtered_result_path'],
        original_data_dir=config['original_data_dir'],
        generated_nl_gpt_json_dir=config['generated_nl_gpt_json_dir'],
        output_path=config['output_path']
    ) 