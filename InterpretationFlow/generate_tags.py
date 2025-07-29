import json
import os
from pathlib import Path
from tqdm import tqdm
import time
import sys

# 添加项目根目录到 Python 路径
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# 直接导入，因为 gpt_call.py 在根目录
from gpt_call import call_gpt_3_5, call_gpt_4o_20240806
from prompt import get_prompt

def load_json_file(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(data, file_path):
    """保存JSON文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def extract_json_from_response(response):
    """从GPT响应中提取JSON数组"""
    try:
        # 查找第一个'['和最后一个']'之间的内容
        start = response.find('[')
        end = response.rfind(']')
        if start != -1 and end != -1:
            json_str = response[start:end+1]
            return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {str(e)}")
    except Exception as e:
        print(f"提取JSON时发生错误: {str(e)}")
    return None

def generate_tags(test_data_path, output_dir, model="gpt3.5"):
    """
    为测试数据中的nl_utterance生成标签
    
    Args:
        test_data_path: test_data.json的路径
        output_dir: 输出目录路径
        model: 使用的模型，"gpt3.5"或"gpt4"
    """
    # 加载测试数据
    test_data = load_json_file(test_data_path)
    
    # 遍历每个测试用例
    for filename, data in tqdm(test_data.items(), desc="Processing files"):
        output_path = Path(output_dir) / f"{filename}"
        
        # 如果结果文件已存在，跳过
        if output_path.exists():
            print(f"Skipping {filename} - already exists")
            continue
            
        try:
            # 准备prompt所需数据
            nl_utterance = data['nl_utterance']
            table_columns = data['table_info']['table_columns']
            table_sample = data['table_info']['table_samples'][0]  # 只取第一行数据
            
            # 生成prompt
            prompt = get_prompt(
                NL=nl_utterance,
                table_columns=table_columns,
                table_sample=table_sample
            )
            
            # 调用GPT
            if model == "gpt4":
                result, token_usage = call_gpt_4o_20240806(prompt)
            else:
                result, token_usage = call_gpt_3_5(prompt)
            
            print(result)
            
            # 解析JSON
            parsed_result = extract_json_from_response(result)
            if parsed_result is None:
                print(f"Warning: Could not parse JSON from response for {filename}")
                continue
            
            # 构建输出数据
            output_data = {
                'nl_utterance': nl_utterance,
                'table_info': {
                    'table_columns': table_columns,
                    'table_sample': table_sample
                },
                'tags': parsed_result,
                'token_usage': token_usage
            }
            
            # 保存结果
            save_json_file(output_data, output_path)
            print(f"Saved results to {output_path}")
            
            # 添加延迟以避免API限制
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue

def main():
    # 配置路径
    BASE_DIR = Path(__file__).parent
    #print(f"BASE_DIR: {BASE_DIR}")
    
    config = {
        'test_data_path': BASE_DIR.parent / 'eval' / 'raw_data' / 'test_data.json',
        'output_dir': BASE_DIR / 'result' / 'gpt35_tags',
        'model': 'gpt3.5'  # 或 'gpt4'
    }
    
    # 确保输入文件存在
    if not config['test_data_path'].exists():
        raise FileNotFoundError(f"找不到文件: {config['test_data_path']}")
    
    # 运行生成
    generate_tags(
        test_data_path=config['test_data_path'],
        output_dir=config['output_dir'],
        model=config['model']
    )

if __name__ == '__main__':
    main() 