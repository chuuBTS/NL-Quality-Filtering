import json
from collections import Counter
from pathlib import Path

def analyze_mark_constraints(file_path):
    """
    分析mark_constraints中c_name的分布情况
    
    Args:
        file_path: filtered_result.json的路径
    
    Returns:
        Counter: c_name的计数器
    """
    # 加载数据
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 用于统计c_name的计数器
    c_name_counter = Counter()
    
    # 记录总对象数和包含mark_constraints的对象数
    total_objects = len(data)
    objects_with_mark = 0
    
    # 遍历每个对象
    for key, item in data.items():
        mark_constraints = item.get('mark_constraints', [])
        
        if mark_constraints:  # 如果mark_constraints不为空
            objects_with_mark += 1
            # 遍历mark_constraints中的每个对象
            for constraint in mark_constraints:
                c_name = constraint.get('c_name')
                if c_name:
                    c_name_counter[c_name] += 1
    
    return c_name_counter, total_objects, objects_with_mark

def normalize_mark(mark):
    """
    标准化mark字符串，去除空格并转换为小写
    
    Args:
        mark: mark字符串
    
    Returns:
        str: 标准化后的mark字符串
    """
    if mark is None:
        return None
    return str(mark).lower().strip()

def analyze_mark_matching(file_path):
    """
    分析mark_constraints中指定的mark类型与生成的图表类型是否匹配
    如果没有mark约束，则认为任何图表类型都是匹配的
    比较时忽略大小写和空格
    
    Args:
        file_path: 数据文件路径
    
    Returns:
        tuple: (总图表数, 不匹配的图表数, 不匹配的详细信息列表)
    """
    # 加载数据
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_charts = 0
    mismatched_charts = 0
    mismatch_details = []
    
    # 遍历每个对象
    for key, item in data.items():
        mark_constraints = item.get('mark_constraints', [])
        chart_list = item.get('generated_chart_list', [])
        
        # 如果没有图表，跳过
        if not chart_list:
            continue
            
        # 获取mark约束
        required_mark = None
        for constraint in mark_constraints:
            mark = constraint.get('mark')
            if isinstance(mark, str):  # 只处理mark是字符串的情况
                required_mark = normalize_mark(mark)
                break
        
        # 检查每个图表
        for chart_idx, chart in enumerate(chart_list):
            total_charts += 1
            actual_mark = normalize_mark(chart.get('mark'))
            
            # 只有当存在mark约束且不匹配时才计入不匹配
            if required_mark is not None and actual_mark != required_mark:
                mismatched_charts += 1
                mismatch_details.append({
                    'file': key,
                    'chart_index': chart_idx,
                    'required_mark': mark,  # 保存原始的mark值，而不是标准化后的
                    'actual_mark': chart.get('mark')  # 保存原始的mark值
                })
    
    return total_charts, mismatched_charts, mismatch_details

def main():
    # 配置文件路径
    file_path = Path('data/old/merged_result.json')
    
    # 确保文件存在
    if not file_path.exists():
        raise FileNotFoundError(f"找不到文件: {file_path}")
    
    # 分析mark constraints的分布
    c_name_counter, total_objects, objects_with_mark = analyze_mark_constraints(file_path)
    
    # 打印统计结果
    print("\n=== Mark Constraints 统计结果 ===")
    print(f"总对象数: {total_objects}")
    print(f"包含mark_constraints的对象数: {objects_with_mark}")
    print(f"包含mark_constraints的对象占比: {objects_with_mark/total_objects*100:.2f}%")
    print("\nc_name 分布情况:")
    print("-" * 40)
    
    # 按出现次数降序排序并打印
    for c_name, count in c_name_counter.most_common():
        percentage = count / total_objects * 100
        print(f"{c_name:<20} = {count:>4} ({percentage:>6.2f}%)")
    
    # 分析mark匹配情况
    print("\n=== Mark 匹配情况分析 ===")
    total_charts, mismatched_charts, mismatch_details = analyze_mark_matching(file_path)
    
    if total_charts > 0:
        mismatch_percentage = (mismatched_charts / total_charts) * 100
        print(f"总图表数: {total_charts}")
        print(f"不匹配的图表数: {mismatched_charts}")
        print(f"不匹配比例: {mismatch_percentage:.2f}%")
        
        # 打印一些不匹配的示例
        print("\n不匹配示例 (前5个):")
        print("-" * 40)
        for detail in mismatch_details[:5]:
            print(f"文件: {detail['file']}")
            print(f"图表索引: {detail['chart_index']}")
            print(f"要求的mark类型: {detail['required_mark']}")
            print(f"实际的mark类型: {detail['actual_mark']}")
            print("-" * 40)

if __name__ == '__main__':
    main() 