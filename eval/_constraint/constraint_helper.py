try:
    from ._constraint_mark_encoding import support_mark_constraint, support_mark_list, reverse_x_y
except:
    from _constraint.constraint_mark_encoding import support_mark_constraint, support_mark_list, reverse_x_y
import re

def get_mark_str(chart_json):
    # print("hello", chart_json)
    if 'mark' in chart_json:
        if isinstance(chart_json['mark'], str): return chart_json['mark']
        else: return chart_json['mark']['type']
    else:
        if isinstance(chart_json, str): return chart_json
        else: return chart_json['type']

def intersection_two_constraint(cons_a, cons_b):
    new_cons = {}
    # intersect mark
    if 'mark' not in cons_a and 'mark' not in cons_b:
        pass
    elif 'mark' not in cons_a or 'mark' not in cons_b:
        new_cons['mark'] = cons_a['mark'] if 'mark' in cons_a else cons_b['mark']
    
    # print(cons_a, cons_b)
    # print(cons_a['mark'], cons_b['mark'])
    if cons_a['mark'] == cons_b['mark']:
        new_cons['mark'] = cons_a['mark']
    else:
        return None
    
    # intersect encoding
    if 'encoding' not in cons_a and 'encoding' not in cons_b:
        pass
    elif 'encoding' not in cons_a or 'encoding' not in cons_b:
        new_cons['encoding'] = cons_a['encoding'] if 'encoding' in cons_a else cons_b['encoding']
    else:
        result = merge_encode_constraint(cons_a['encoding'], cons_b['encoding'])
        # print("result: ", result)
        if result and result != {}:
            new_cons['encoding'] = result
        else:
            return None
        
    # intersect unique map
    new_unique_map = {}
    if ('unique_map' in cons_a) and ('unique_map' in cons_b):
        if cons_a['unique_map'] == cons_b['unique_map']:
            new_unique_map = cons_a['unique_map']
        else:
            return None
    elif ('unique_map' in cons_a) or ('unique_map' in cons_b):
        new_unique_map = cons_a['unique_map'] if 'unique_map' in cons_a else cons_b['unique_map']
    if new_unique_map != {}:
        key_channel = list(new_unique_map.keys())[0]
        if '(' in key_channel:
            pattern = r'\(([^,]+),([^)]+)\)'
            match = re.search(pattern, key_channel.strip())
            key_channel_list = [match.group(1), match.group(2)]
        else: key_channel_list = [key_channel]
        for key in key_channel_list:
            if key not in new_cons['encoding']:
                return None
            if "aggregate" in new_cons['encoding'][key]:
                return None
            else:
                new_cons['unique_map'] = new_unique_map

    return new_cons

def expand_mark_encoding(view_constraint_list):
    # expand mark
    new_constraint_list = []
    for view_constraint in view_constraint_list:
        if 'mark' in view_constraint:
            if isinstance(view_constraint['mark'], str):
                new_mark_list = [view_constraint['mark']]
            elif isinstance(view_constraint['mark'], dict):
                new_mark_list = [get_mark_str(view_constraint['mark'])]
            elif isinstance(view_constraint['mark'], list):
                new_mark_list = [get_mark_str(mark) for mark in view_constraint['mark']]
        else:
            new_mark_list = support_mark_list
        for mark in new_mark_list:
            new_constraint = view_constraint.copy()
            new_constraint['mark'] = mark
            new_constraint_list.append(new_constraint)

    # expand encoding with support_mark_constraints
    result_list = []
    # print("result: ", result_list)
    for view_constraint in new_constraint_list:
        # print("result: ", result_list)
        mark = view_constraint['mark']
        if mark == 'point': mark = 'circle'
        support_mark_constraint_list = support_mark_constraint[mark]
        for mark_constraint in support_mark_constraint_list:
            inter_constraint = intersection_two_constraint(view_constraint, mark_constraint)
            # print("inter: ", inter_constraint)
            if inter_constraint:
                add_new_constraint(result_list, inter_constraint)

    return result_list

def expand_x_y_reverse(constraint_list):
    new_constraint_list = []
    for constraint in constraint_list:
        if 'x_y_reversable' in constraint:

            constraint.pop('x_y_reversable')
            reversed = reverse_x_y(constraint)
            if reversed:
                new_constraint_list.append(reversed)
            
        new_constraint_list.append(constraint)
    return new_constraint_list

def expand_constraints(constraints_list):
    # no x y reversable
    # print("\nbefore: ", constraints_list)
    constraints_list = expand_x_y_reverse(constraints_list)
    # print("\nX Y reversed: ", constraints_list)
    # each constraint has 1 and only 1 mark
    constraints_list = expand_mark_encoding(constraints_list)
    # print("\nMark expanded: ", constraints_list)

    return constraints_list

def expand_task_constraints(task_constraints):
    constraints_list = []
    for cur_dict in task_constraints:
        # print(cur_dict)
        cur_constraints = cur_dict['c_list']
        # print("cur: ", cur_constraints)
        cur_constraints = expand_constraints(cur_constraints)
        # print(cur_constraints)
        constraints_list.append(cur_constraints)
    return constraints_list

def merge_type(type_1, type_2):
    if isinstance(type_1, str): type_1 = [type_1]
    if isinstance(type_2, str): type_2 = [type_2]
    union = list(set(type_1) & set(type_2))
    # print(type_1, type_2, union)
    if union == []:
        return None
    elif len(union) == 1:
        return union[0]
    else:
        return union

def merge_encode_constraint(view_encode_cons, mark_encode_cons):
    new_encoding = {}

    for channel in view_encode_cons.keys():
        # special channel: facet and (column, row) don't merge
        if channel == 'facet':
            if ('column' in mark_encode_cons) or ('row' in mark_encode_cons):
                return None
        if channel in ['column', 'row']:
            if 'facet' in mark_encode_cons:
                return None

        # other channels
        if channel not in mark_encode_cons:
            new_encoding[channel] = view_encode_cons[channel]
            continue

        new_encoding[channel] = {}

        # check and merge type. only merge when both exist type
        if ('type' not in view_encode_cons[channel]) and ('type' not in mark_encode_cons[channel]):
            pass
        elif 'type' not in view_encode_cons[channel]:
            new_encoding[channel]['type'] = mark_encode_cons[channel]['type']
        elif 'type' not in mark_encode_cons[channel]:
            new_encoding[channel]['type'] = view_encode_cons[channel]['type']
        else: # merge type
            merged_type = merge_type(view_encode_cons[channel]['type'], mark_encode_cons[channel]['type'])
            if merged_type:
                new_encoding[channel] = {'type': merged_type}
            else:
                return None

        # check and merge ignorable. still ignore only when both ignorable
        if 'ignore' in view_encode_cons[channel] and 'ignore' in mark_encode_cons[channel]:
            if view_encode_cons[channel]['ignore'] and mark_encode_cons[channel]['ignore']:
                # print("--- ignore = True, channel =  ", channel, ", ", view_encode_cons, mark_encode_cons)
                new_encoding[channel]['ignore'] = True

        # check and merge aggregate
        if 'aggregate' in view_encode_cons[channel] and 'aggregate' not in mark_encode_cons[channel]:
            new_encoding[channel]['aggregate'] = view_encode_cons[channel]['aggregate']

        # check and merge sort
        if 'sort' in view_encode_cons[channel] and 'sort' not in mark_encode_cons[channel]:
            new_encoding[channel]['sort'] = view_encode_cons[channel]['sort']

    for channel in mark_encode_cons.keys():
        if channel not in view_encode_cons:
            new_encoding[channel] = mark_encode_cons[channel]

    return new_encoding


def add_new_constraint(constraint_list, new_constraint, print_tag = False):
    intersection = False
    for idx in range(len(constraint_list)):
        old_constraint = constraint_list[idx]
        inter_constraint = intersection_two_constraint(old_constraint, new_constraint)

        if inter_constraint and inter_constraint != {}:
            intersection = True
            if print_tag: print("intersection: \n", inter_constraint)

            if identical_two_constraint(inter_constraint, new_constraint):
                return constraint_list
            elif identical_two_constraint(inter_constraint, old_constraint):
                constraint_list.pop(idx)
                if print_tag: print("add new constraint: \n", new_constraint)
                constraint_list.append(new_constraint)
                return constraint_list
            else:
                if print_tag: print("add new constraint: \n", new_constraint)
                constraint_list.append(new_constraint)
                return constraint_list
            
    if not intersection:
        if print_tag: print("add new constraint: \n", new_constraint)
        constraint_list.append(new_constraint)

    return constraint_list

def identical_two_constraint(cons_a, cons_b):
    for key in cons_a.keys():
        if key not in cons_b:
            return False
        
        if isinstance(cons_a[key], dict):
            if not isinstance(cons_b[key], dict):
                return False
            if not identical_two_constraint(cons_a[key], cons_b[key]):
                return False
        if isinstance(cons_a[key], list):
            if not isinstance(cons_b[key], list):
                return False
            if len(cons_a[key]) != len(cons_b[key]):
                return False
            for idx in range(len(cons_a[key])):
                if cons_a[key][idx] != cons_b[key][idx]:
                    return False
        if isinstance(cons_a[key], str):
            if cons_a[key] != cons_b[key]:
                return False
    return True