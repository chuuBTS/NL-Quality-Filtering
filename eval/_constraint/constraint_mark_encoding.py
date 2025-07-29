import os
import json
import copy

# from collections import ChainMap

# init
arc_constraint = {
    'mark': 'arc',
    'encoding': {
        'theta': {'type': 'quantitative'},
        'color': {'type': 'nominal'},
    },
    'unique_map': {'color': 'theta'}
}

bar_constraint = {
    'mark': 'bar',
    'encoding': {
        'x': {'type': ['quantitative', 'nominal']},
        'y': {'type': 'quantitative'},
        'color': {'type': 'nominal', 'ignore': True},
    },
    'unique_map': {'x': 'y'}
}

line_constraint = {
    'mark': 'line',
    'encoding': {
        'x': {'type': 'temporal'},
        'y': {'type': 'quantitative'},
        'color': {'ignore': True, 'type': 'nominal'},
    },
    'unique_map': {'x': 'y'}
}

area_constraint = {
    'mark': 'area',
    'encoding': {
        'x': {'type': 'temporal'},
        'y': {'type': 'quantitative'},
        'color': {'type': 'nominal', 'ignore': True},
    },
    'unique_map': {'x': 'y'}
}

point_constraint = {
    'mark': 'circle',
    'encoding': {
        'x': {'type': ['quantitative', 'nominal']},
        'y': {'type': ['quantitative', 'nominal']},
        'color': {'type': 'nominal', 'ignore': True},
        'size': {'ignore': True, 'type': 'quantitative'},
    }
}

rect_constraint = {
    'mark': 'rect',
    'encoding': {
        'x': {'type': ['quantitative', 'nominal']},
        'y': {'type': ['quantitative', 'nominal']},
        'color': {'type': 'quantitative'},
    },
    'unique_map': {'(x,y)': 'color'}
}

boxplot_constraint = {
    'mark': 'boxplot',
    'encoding': {
        'x': {'type': 'nominal', 'ignore': True},
        'y': {'type': 'quantitative'},
    },
}

facet_encoding_constraint = [
    {
        'column': {'ignore': True, "type": "nominal"},
        'row': {'ignore': True, "type": "nominal"},
    }
]

def merge_dict(dict1, dict2):
    """合并两个字典"""
    return {**dict1, **dict2}

def add_facet_constraint(mark_constraints):
    """添加facet约束"""
    result = []
    facet_encoding = {
        'column': {'type': ['nominal', 'ordinal'], 'ignore': True},
        'row': {'type': ['nominal', 'ordinal'], 'ignore': True}
    }
    
    for mark_constraint in mark_constraints:
        new_constraint = mark_constraint.copy()
        new_encoding = merge_dict(mark_constraint['encoding'], facet_encoding)
        new_constraint['encoding'] = new_encoding
        result.append(new_constraint)
    
    return result

# 支持的图表类型列表
support_mark_list = ['bar', 'line', 'area', 'point', 'circle', 'square', 'tick']

# 基础的mark约束
support_mark_constraint = {
    'bar': [
        {
            'mark': 'bar',
            'encoding': {
                'x': {'type': ['nominal', 'ordinal', 'temporal']},
                'y': {'type': ['quantitative']}
            }
        }
    ],
    'line': [
        {
            'mark': 'line',
            'encoding': {
                'x': {'type': ['temporal', 'ordinal']},
                'y': {'type': ['quantitative']}
            }
        }
    ],
    'area': [
        {
            'mark': 'area',
            'encoding': {
                'x': {'type': ['temporal', 'ordinal']},
                'y': {'type': ['quantitative']}
            }
        }
    ],
    'point': [
        {
            'mark': 'point',
            'encoding': {
                'x': {'type': ['quantitative', 'temporal']},
                'y': {'type': ['quantitative']}
            }
        }
    ],
    'circle': [
        {
            'mark': 'circle',
            'encoding': {
                'x': {'type': ['quantitative', 'temporal']},
                'y': {'type': ['quantitative']}
            }
        }
    ],
    'square': [
        {
            'mark': 'square',
            'encoding': {
                'x': {'type': ['quantitative', 'temporal']},
                'y': {'type': ['quantitative']}
            }
        }
    ],
    'tick': [
        {
            'mark': 'tick',
            'encoding': {
                'x': {'type': ['nominal', 'ordinal', 'temporal']},
                'y': {'type': ['quantitative']}
            }
        }
    ]
}

def reverse_x_y(constraint):
    """反转x和y轴的约束"""
    if 'encoding' not in constraint:
        return constraint
    
    new_constraint = constraint.copy()
    new_encoding = {}
    
    if 'x' in constraint['encoding'] and 'y' in constraint['encoding']:
        new_encoding['x'] = constraint['encoding']['y'].copy()
        new_encoding['y'] = constraint['encoding']['x'].copy()
        
        for channel in constraint['encoding']:
            if channel not in ['x', 'y']:
                new_encoding[channel] = constraint['encoding'][channel].copy()
                
        new_constraint['encoding'] = new_encoding
        return new_constraint
    return None

# 为每种mark类型添加facet约束
for mark in support_mark_list:
    support_mark_constraint[mark] = add_facet_constraint(support_mark_constraint[mark])

if __name__ == "__main__":

    pass