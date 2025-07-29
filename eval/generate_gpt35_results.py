import json
import os
from pathlib import Path
from tqdm import tqdm
import time
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
    """
    从GPT响应中提取JSON数组
    Args:
        response: GPT返回的字符串
    Returns:
        解析后的JSON数组，如果解析失败则返回None
    """
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

def generate_gpt35_results(test_data_path, output_dir):
    """
    读取测试数据，调用GPT-3.5生成结果并保存
    
    Args:
        test_data_path: test_data.json的路径
        output_dir: 输出目录路径
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
            # 准备prompt
            prompt = get_prompt(
                table_columns=data['table_info']['table_columns'],
                table_sample=data['table_info']['table_samples'][0],
                nl_utterance=data['nl_utterance']
            )
            print(f"\nProcessing {filename}")
            #print("Prompt:", prompt)
            
            # 调用GPT-3.5
            result, token_usage = call_gpt_3_5(prompt)
            #print("Raw response:", result)
            
            # 解析JSON
            parsed_result = extract_json_from_response(result)
            if parsed_result is None:
                print(f"Warning: Could not parse JSON from response for {filename}")
                continue
            print("Parsed result:", parsed_result)
                
            # 构建输出数据
            output_data = {
                'nl_utterance': data['nl_utterance'],
                'table_info': data['table_info'],
                'refer_fileds': data.get('refer_fileds', []),
                'refer_others': data.get('refer_others', []),
                'good_generated_chart_list': data.get('good_generated_chart_list', []),
                'predict35': parsed_result,  # 使用解析后的JSON
            }
            
            # 保存结果
            save_json_file(output_data, output_path)
            print(f"Saved results to {output_path}")
            
            # 添加延迟以避免API限制
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue

if __name__ == '__main__':
    # 配置路径
    BASE_DIR = Path(__file__).parent
    config = {
        'test_data_path': BASE_DIR / 'raw_data' / 'test_data.json',
        'output_dir': BASE_DIR / 'result' / 'gpt35'
    }
    
    # 确保输入文件存在
    if not config['test_data_path'].exists():
        raise FileNotFoundError(f"找不到文件: {config['test_data_path']}")
    
    # 运行生成
    generate_gpt35_results(
        test_data_path=config['test_data_path'],
        output_dir=config['output_dir']
    ) 