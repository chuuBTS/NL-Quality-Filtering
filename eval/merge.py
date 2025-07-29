import json
import os
from tqdm import tqdm

print("正在合并所有result文件...")

try:
    # 存储所有数据的字典
    merged_data = {}
    
    # 指定result文件夹路径
    result_dir = 'result/gpt35'
    # 指定合并后文件路径
    merge_dir = 'result/merged_result_gpt35.json'

    # 获取result文件夹下所有json文件
    result_files = [f for f in os.listdir(result_dir) if f.endswith('.json')]
    
    # 遍历每个文件并读取数据
    for file_name in tqdm(result_files):
        try:
            file_path = os.path.join(result_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 使用文件名(不含扩展名)作为key
                merged_data[file_name] = data
            print(f"成功读取 {file_name}")
        except Exception as e:
            print(f"处理 {file_name} 时出错: {str(e)}")
            continue
    
    # 保存合并后的数据
    with open(merge_dir, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)
    
    print(f"合并完成! 共合并了 {len(result_files)} 个文件")
    print(f"合并后的数据包含 {len(merged_data)} 个记录")
    print(f"结果已保存到 {merge_dir}")

except Exception as e:
    print(f"发生错误: {str(e)}")
