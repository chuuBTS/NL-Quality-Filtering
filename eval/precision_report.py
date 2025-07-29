import json
import os
from check_constraints import check_list_constraints

def load_json_file(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def evaluate_predictions(predict_data):
    """评估预测结果的准确性
    
    Args:
        predict_data: 包含预测结果的字典数据
    
    Returns:
        dict: 包含各项指标的统计结果
    """
    stats = {
        'field': 0,
        'mark': 0,
        'aggregate': 0,
        'filter': 0,
        'bin': 0,
        'sort': 0,
        'transform': 0,
        'all': 0,
        'total': len(predict_data)
    }
    
    for filename, sample in predict_data.items():
        # 获取必要数据
        datacolumn = sample['table_info']['table_columns']
        nl_utterance = sample['nl_utterance']
        refer_fileds = sample.get('refer_fileds', [])
        refer_others = sample.get('refer_others', [])
        predict = sample['predict35']  # GPT-3.5的预测结果

        # 检查field约束
        result = check_list_constraints(predict, refer_fileds, [])
        if result:
            stats['field'] += 1

        # 检查mark约束
        mark_constraints = [d for d in refer_others if d['c_type'] == 'mark']
        result = check_list_constraints(predict, [], mark_constraints)
        if result:
            stats['mark'] += 1

        # 检查aggregate约束
        aggregate_constraints = [d for d in refer_others if d['c_name'] == 'aggregate']
        result = check_list_constraints(predict, [], aggregate_constraints)
        if result:
            stats['aggregate'] += 1

        # 检查filter约束
        filter_constraints = [d for d in refer_others if d['c_name'] == 'filter']
        result = check_list_constraints(predict, [], filter_constraints)
        if result:
            stats['filter'] += 1

        # 检查bin约束
        bin_constraints = [d for d in refer_others if d['c_name'] == 'bin']
        result = check_list_constraints(predict, [], bin_constraints)
        if result:
            stats['bin'] += 1

        # 检查sort约束
        sort_constraints = [d for d in refer_others if d['c_name'] == 'sort']
        result = check_list_constraints(predict, [], sort_constraints)
        if result:
            stats['sort'] += 1
        # else:
        #     print(f"sort constraint not satisfied for {filename}")
        #     print(f"predict: {predict}")
        #     print(f"refer_others: {refer_others}")

        # 检查所有transform约束
        transform_constraints = [d for d in refer_others if d['c_name'] in ['filter', 'aggregate', 'bin']]
        result = check_list_constraints(predict, [], transform_constraints)
        if result:
            stats['transform'] += 1

        # 检查所有约束
        all_constraints = [d for d in refer_others if d['c_type'] == 'mark' or 
                         d['c_name'] in ['filter', 'aggregate', 'sort', 'bin']]
        result = check_list_constraints(predict, refer_fileds, all_constraints)
        if result:
            stats['all'] += 1

    return stats

def print_results(stats):
    """打印评估结果
    
    Args:
        stats: 包含各项指标统计的字典
    """
    total = stats['total']
    print(f"\n评估结果 (总样本数: {total}):")
    print("-" * 50)
    metrics = [
        ('Mark', 'mark'),
        ('Field', 'field'),
        ('Sort', 'sort'),
        ('Filter', 'filter'),
        ('Aggregate', 'aggregate'),
        ('Bin', 'bin'),
        ('All Transform', 'transform'),
        ('All Constraints', 'all')
    ]
    
    for name, key in metrics:
        count = stats[key]
        percentage = (count / total * 100) if total > 0 else 0
        print(f"{name:15} = {count:4d} / {total} = {percentage:6.2f}%")

def main():
    # 配置参数
    config = {
        'predict_path': './result/merged_result_gpt35.json',
    }
    
    # 加载数据
    print(f"\n加载数据源: {config['predict_path']}")
    predict_data = load_json_file(config['predict_path'])
    
    # 评估预测结果
    stats = evaluate_predictions(predict_data)
    
    # 打印结果
    print_results(stats)

if __name__ == '__main__':
    main()
