import json
import os
import ast
import re
from _constraint.constraint_helper import get_mark_str
from _constraint.constraint_view_level_task import support_task_constraint, check_view_constraint_list

def check_field_constraints(chart_json, field_constraints):
    try:
        chart_encoding = chart_json['encoding']
    except:
        chart_encoding=[]
    # print(chart_encoding)

    chart_field_list = []
    for channel, c_dict in chart_encoding.items():
        if not isinstance(c_dict, dict):
            continue
        if 'field' in c_dict:
            # print(c_dict['field'])
            if isinstance(c_dict['field'], str):
                # chart_field_list.append(c_dict['field'])
                chart_field_list.append(c_dict['field'].lower())

    cons_field_list = []
    for c_dict in field_constraints:
        if 'field' in c_dict:
            if isinstance(c_dict['field'], str):
                cons_field_list.append(c_dict['field'].lower())
            elif isinstance(c_dict['field'], list):
                for f in c_dict['field']:
                    cons_field_list.append(f.lower())

    # print("chart:", chart_field_list, '\t cons:', cons_field_list)
    
    result_list = []
    for cons_f in cons_field_list:
        if isinstance(cons_f, str):
            if cons_f in chart_field_list:
                result_list.append(True)
            else:
                result_list.append(False)
        elif isinstance(cons_f, list):
            flag = False
            for f in chart_field_list:
                if f in cons_f:
                    flag = True
                    break
            result_list.append(flag)
        else:
            result_list.append(False)
    # print(result_list)

    return result_list


def check_mark(chart_json, mark_constraint):
    chart_mark = get_mark_str(chart_json).lower()
    
    cons_mark = mark_constraint['c_name'].split()[0].lower()

    if chart_mark == cons_mark:
        return True
    else:
        if chart_mark in ['point', 'circle'] and cons_mark in ['point', 'circle']:
            return True
        else:
            return False

def check_task(chart_json, cons):
    c_list = cons['c_list']
    return check_view_constraint_list(chart_json, c_list)

def check_filter(chart_json, cons):
    if isinstance(cons['c_list'], list):
        cons_filter = cons['c_list'][0]
    else:
        cons_filter = cons['c_list']

    if isinstance(cons_filter, dict):
        if 'filter' in cons_filter:
            cons_filter = cons_filter['filter']
        else:
            cons_filter = cons_filter
    
    if isinstance(cons_filter, str):
        # change " to ' and remove all spaces
        cons_filter = cons_filter.replace('"', "'").lower()
        cons_filter = cons_filter.replace(' ', '')
        # 将连续的||替换为单个|
        cons_filter = cons_filter.replace('||', '|')
        # 去掉null前的引号
        cons_filter = cons_filter.replace("'null'", "null")
        # 将==替换为=
        cons_filter = cons_filter.replace('==', '=')

    try:
        transform = chart_json['transform']
        for trans in transform:
            if 'filter' in trans:
                trans_filter = trans['filter']
                
                # 处理字典形式的filter
                if isinstance(trans_filter, dict):
                    if 'field' in trans_filter:
                        field = trans_filter['field']
                        if 'equal' in trans_filter:
                            value = trans_filter['equal']
                            expected_filter = f"datum.{field}='{value}'"
                            if expected_filter.lower() == cons_filter.lower():
                                return True
                        elif 'oneOf' in trans_filter:
                            # 修正oneOf的大小写问题
                            value = trans_filter['oneOf'][0] if isinstance(trans_filter['oneOf'], list) else trans_filter['oneOf']
                            # 处理not条件
                            if 'not' in trans_filter and trans_filter['not']:
                                expected_filter = f"datum.{field}!='{value}'"
                            else:
                                expected_filter = f"datum.{field}='{value}'"
                            if expected_filter.lower() == cons_filter.lower():
                                return True
                
                # 处理字符串形式的filter
                if isinstance(trans_filter, str):
                    trans_filter = trans_filter.replace('"', "'").lower()
                    trans_filter = trans_filter.replace(' ', '')
                    trans_filter = trans_filter.replace('||', '|')
                    trans_filter = trans_filter.replace("'null'", "null")
                    trans_filter = trans_filter.replace('==', '=')
                    if trans_filter == cons_filter:
                        return True
                else:
                    trans_filter = str(trans_filter).replace('"', "'").lower()
                    trans_filter = trans_filter.replace(' ', '')
                    trans_filter = trans_filter.replace('||', '|')
                    trans_filter = trans_filter.replace("'null'", "null")
                    trans_filter = trans_filter.replace('==', '=')
                    if trans_filter == cons_filter:
                        return True
                        
        return False
    except Exception as e:
        #print("Error in check_filter:", e)
        return False

def check_bin(chart_json, cons):
    bin_cons = cons['c_list'][0]
    encoding = chart_json['encoding']
    for channel, e_dict in encoding.items():
        if 'field' in e_dict and e_dict['field'].lower() == bin_cons['field'].lower():
            if 'bin' in e_dict and 'bin' in bin_cons:
                if e_dict['bin'] == True:
                    return True
            elif 'timeUnit' in e_dict and 'timeUnit' in bin_cons:
                if e_dict['timeUnit'].lower() == bin_cons['timeUnit'].lower():
                    return True
    return False

def check_aggregate(chart_json, cons):
    # print("hehhhh", cons)
    if isinstance(cons['c_list'], list):
        aggregate_cons = cons['c_list'][0]
    else:
        aggregate_cons = cons['c_list']
    if aggregate_cons['aggregate'].lower() == 'average':
        aggregate_cons['aggregate'] = 'mean'

    encoding = chart_json['encoding']
    for channel, e_dict in encoding.items():
        if 'aggregate' in e_dict:
            # 添加空值检查
            if 'aggregate' not in e_dict or e_dict['aggregate'] is None:
                return False
            
            # 添加类型检查和处理
            chart_agg = e_dict['aggregate']
            if isinstance(chart_agg, dict):
                # 如果是字典类型，需要提取实际的聚合操作值
                # 这里需要根据实际的数据结构来调整
                chart_agg = str(chart_agg.get('op', ''))  # 假设聚合操作存储在 'op' 键中
            
            chart_agg = str(chart_agg).lower()
            if chart_agg == 'average':
                chart_agg = 'mean'
            if chart_agg == aggregate_cons['aggregate'].lower():
                if 'field' in e_dict:#修改 
                    if 'field' in aggregate_cons and e_dict['field'].lower() == aggregate_cons['field'].lower(): return True
                    else: return False
                else:
                    return True

    return False

def check_sort(chart_json, cons):
    try:
        # 1. 添加参数验证
        if not cons or 'c_list' not in cons or not cons['c_list']:
            return False
            
        try:
            sort_cons = cons['c_list'][0]
        except (IndexError, TypeError):
            return False
        
        encoding = chart_json.get('encoding', {})
        
        # 2. 获取x和y轴的field（移到函数开始处）
        y_field = None
        x_field = None
        if 'y' in encoding and 'field' in encoding['y']:
            y_field = encoding['y']['field'].lower()
        if 'x' in encoding and 'field' in encoding['x']:
            x_field = encoding['x']['field'].lower()
        
        # 3. 检查encoding中的sort
        for channel, e_dict in encoding.items():
            # 添加类型检查
            if not isinstance(e_dict, dict):
                continue
            # 3.1 处理简单sort
            if isinstance(e_dict.get('sort'), str):
                if (e_dict.get('sort', '').lower() == sort_cons.get('order', '').lower() and 
                    e_dict.get('field', '').lower() == sort_cons.get('field', '').lower()):
                    return True
                    
            # 3.2 处理复杂sort字典
            if isinstance(e_dict.get('sort'), dict):
                sort_field = e_dict['sort'].get('field', '').lower()
                sort_order = e_dict['sort'].get('order', '').lower()
                cons_order = sort_cons.get('order', '').lower()
                
                # 处理y轴排序
                if ((cons_order == 'y' and sort_field == y_field and sort_order == 'ascending') or
                    (cons_order == '-y' and sort_field == y_field and sort_order == 'descending')):
                    return True
                    
                # 处理x轴排序
                if ((cons_order == 'x' and sort_field == x_field and sort_order == 'ascending') or
                    (cons_order == '-x' and sort_field == x_field and sort_order == 'descending')):
                    return True
        
        # 4. 检查transform中的sort
        for trans in chart_json.get('transform', []):
            if isinstance(trans.get('sort'), dict):
                sort_field = trans['sort'].get('field', '').lower()
                sort_order = trans['sort'].get('order', '').lower()
                cons_order = sort_cons.get('order', '').lower()
                
                # 使用相同的y轴和x轴排序逻辑
                if ((cons_order == 'y' and sort_field == y_field and sort_order == 'ascending') or
                    (cons_order == '-y' and sort_field == y_field and sort_order == 'descending') or
                    (cons_order == 'x' and sort_field == x_field and sort_order == 'ascending') or
                    (cons_order == '-x' and sort_field == x_field and sort_order == 'descending')):
                    return True
        
        return False
    except Exception as e:
        return False

def check_transform(chart_json, cons):
    if cons['c_name'] == 'filter':
        return check_filter(chart_json, cons)
    if cons['c_name'] == 'bin':
        return check_bin(chart_json, cons)
    if cons['c_name'] == 'aggregate':
        return check_aggregate(chart_json, cons)
    if cons['c_name'] == 'sort':
        return check_sort(chart_json, cons)

def check_other_constraints(chart_json, other_constraints):
    result_list = []
    for cons in other_constraints:
        if cons['c_type'] == 'mark':
            cur_true = check_mark(chart_json, cons)
        elif cons['c_type'] == 'task':
            cur_true = check_task(chart_json, cons)
        elif cons['c_type'] == 'transform':
            cur_true = check_transform(chart_json, cons)

        result_list.append(cur_true)
    return result_list


def process_list_bool(bool_list):
    # print("bool list", bool_list)
    all_true = all(bool_list)
    count_true = sum(bool_list)
    if len(bool_list) == 0:
        p_true = 1
    else:
        p_true = count_true / len(bool_list)

    return all_true, count_true, p_true

def check_constraints(chart_json, field_constraints, other_constraintrs):
    ### Usage:
    #    all_cons_true, all_cons_p_true, all_bool_list = check_constraints(chart_json, refer_fields, refer_others)
    ### Input:
    #    chart_json: dict
    #    refer_fields: list
    #    refer_others: list
    ### Output:
    #    all_cons_true: bool -> True or False
    #    all_cons_p_true: float -> [0,1]
    #    all_bool_list: list -> len(all_bool_list) = len(refer_fields) + len(refer_others)
    ###
    len_all = len(field_constraints) + len(other_constraintrs)
    if 'mark' not in chart_json or 'encoding' not in chart_json:
        all_cons_true = False
        all_cons_p_true = 0
        bool_list = []
        return all_cons_true, all_cons_p_true, bool_list

    if len(field_constraints) > 0:
        field_result_list = check_field_constraints(chart_json, field_constraints)
        field_all_true, field_count_true, field_p_true = process_list_bool(field_result_list)
    else:
        field_result_list = []
        field_all_true = True
        field_count_true = 0
        field_p_true = 0

    if len(other_constraintrs) > 0:
        other_result_list = check_other_constraints(chart_json, other_constraintrs)
        other_all_true, other_count_true, other_p_true = process_list_bool(other_result_list)
    else:
        other_result_list = []
        other_all_true = True
        other_count_true = 0
        other_p_true = 0

    all_cons_true = field_all_true and other_all_true
    len_all = len(field_result_list) + len(other_result_list)
    if len_all == 0:
        all_cons_p_true = 1
    else:
        all_cons_p_true = (field_count_true + other_count_true) / (len(field_result_list) + len(other_result_list))

    # print("field list", field_result_list)
    # print("other list", other_result_list)
    bool_list = field_result_list + other_result_list

    return all_cons_true, all_cons_p_true, bool_list

def check_list_constraints(list_chart, refer_fields, refer_others):
    any_true = False
    any_false = False
    for chart_json in list_chart:
        if isinstance(chart_json, str):
            try:
                chart_json = json.loads(chart_json)
            except:
                try:
                    chart_json = ast.literal_eval(chart_json)
                except:
                    continue

        all_cons_true, all_cons_p_true, all_bool_list = check_constraints(chart_json, refer_fields, refer_others)
        # print("all cons", all_cons_true, all_cons_p_true, all_bool_list)
        if all_cons_true:
            any_true = True
        else:
            # print(file_path, all_bool_list)
            any_false = True

    # if any_true:
    #     print("@ hit k true")
    return any_true


def main():
    file_path = './sample_task_1.json'
    with open(file_path, 'r') as f:
        load_json = json.load(f)
    refer_fields = load_json['refer_fileds']
    refer_others = load_json['refer_others']
    generated_charts_list = load_json['generated_chart_list']

    any_true = False
    any_false = False
    for chart_json in generated_charts_list:
        all_cons_true, all_cons_p_true, all_bool_list = check_constraints(chart_json, refer_fields, refer_others)
        if all_cons_true:
            any_true = True
        else:
            print(file_path, all_bool_list)
            any_false = True

    if any_true:
        print("@ hit k true")

    # if not any_false:
    #     print("all true")

if __name__ == "__main__":


    main()
    
    # dataset_dir = './upload_dataset_task_1'
    # filename_list = os.listdir(dataset_dir)
    # filename_list.sort()
    # for filename in filename_list:
    #     # print(filename)
    #     file_path = os.path.join(dataset_dir, filename)