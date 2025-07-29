import os
import json
import copy
try:
    from .constraint_helper import expand_constraints, get_mark_str
except:
    from constraint_helper import expand_constraints, get_mark_str

trend_constraint = [
    {
        # 'mark': ['bar', 'line', 'area'],
        'mark': ['line', 'area'],
        'encoding': {'x': {'type': 'temporal'},}
    },
    # {
    #     'encoding': {'column': {'type': 'temporal'},}
    # }
]

small_multiple_constraint = [
    {
        'encoding': {'facet': {},}
    },
    {
        'encoding': {'column': {},}
    },
    {
        'encoding': {'row': {},}
    },
]

composition_constraint = [
    {
        'mark': 'bar',
        'encoding': {
            'x': {},
            'y': {'type': 'quantitative'},
            'color': {'type': 'nominal'}
        },
        'x_y_reversable': True
    },
    {
        'mark': 'area',
        'encoding': {
            'x': {},
            'y': {'type': 'quantitative'},
            'color': {'type': 'nominal'}
        }
    },
    {
        'mark': 'arc',
        'encoding': {
            'theta': {'type':'quantitative'},
            'color': {'type': 'nominal'}
        }
    }
]

correlation_constraint = [
    {
        "mark": "circle",
        "encoding": {
            "x": {"type": "quantitative"},
            "y": {"type": "quantitative"},
        }
    }
]

relationship_constraint = [
    {
        "mark": "rect",
        "encoding": {
            "x": {},
            "y": {},
            "color": {}
        }
    }
]

distribution_constraint = [
    {
        'mark': 'bar',
        'encoding': {
            'y': {'aggregate': 'count', 'type': 'quantitative'}
        },
        'x_y_reversable': True
    },
    {
        'mark': 'boxplot',
        'encoding': {
            'x': {'type': 'quantitative'}
        },
        'x_y_reversable': True
    }
]

###############################################################
support_task_constraint = {
    'composition': composition_constraint,
    'correlation': correlation_constraint,
    'distribution': distribution_constraint,
    'trend': trend_constraint,
    'small_multiple': small_multiple_constraint,
}
################################################################

def check_mark(chart_mark, constraint_mark):
    chart_mark = get_mark_str(chart_mark)
    if isinstance(constraint_mark, str) or isinstance(constraint_mark, dict):
        constraint_mark = get_mark_str(constraint_mark)
        if chart_mark == constraint_mark:
            return True
    elif isinstance(constraint_mark, list):
        constraint_mark = [get_mark_str(mark) for mark in constraint_mark]
        if chart_mark in constraint_mark:
            return True
    return False

def check_encode(chart_encode, constraint_encode):
    chart_channel_list = list(chart_encode.keys())
    constraint_channel_list = list(constraint_encode.keys())
    for channel in constraint_channel_list:
        # ignore soft channel, if not exist in chart
        if ('ignore' in constraint_encode[channel]) and constraint_encode[channel]['ignore']:
            if channel not in chart_channel_list:
                continue

        # check hard channel, must exist in chart
        if channel not in chart_channel_list:
            return False
        
        # check field type coherent
        if 'type' in constraint_encode[channel] and 'type' in chart_encode[channel]:
            if constraint_encode[channel]['type'] != chart_encode[channel]['type']:
                return False
            
        # check aggregate type coherent
        if 'aggregate' in constraint_encode[channel] and 'aggregate' in chart_encode[channel]:
            # print(constraint_encode[channel]['aggregate'], chart_encode[channel]['aggregate'])
            if constraint_encode[channel]['aggregate'] != chart_encode[channel]['aggregate']:
                return False
        elif 'aggregate' in constraint_encode[channel] and 'aggregate' not in chart_encode[channel]:
            return False
            
    return True

def check_view_constraint(chart_json, constraint):
    if 'mark' in constraint:
        if not check_mark(chart_json['mark'], constraint['mark']):
            return False
    
    if 'encoding' in constraint:
        if not check_encode(chart_json['encoding'], constraint['encoding']):
            return False

    return True

def check_view_constraint_list(chart_json, constraint_list):

    # expand to simple constraint dict
    # print("constraint_list: ", constraint_list)
    new_constraint_list = expand_constraints(constraint_list) 
    # print("new_constraint_list: ", len(new_constraint_list))

    # check each
    for constraint in new_constraint_list:
        if check_view_constraint(chart_json, constraint):
            # print("!! Fit! ", constraint)
            return True
    return False

def check_task_constraint_list(chart_json, constraint_name):
    if constraint_name not in support_task_constraint:
        return False
    new_constraint = copy.deepcopy(support_task_constraint[constraint_name])
    return check_view_constraint_list(chart_json, new_constraint)
        
stat_encode_num = {}

if __name__ == "__main__":
    pass
    