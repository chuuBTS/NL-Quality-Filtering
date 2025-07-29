
import json
import os
import tqdm

source_dir = "../chart_simplify/"

# Loop through all files in the source directory
for filename in os.listdir(source_dir):
    if filename.endswith('.simplify.json'):  # Check if the file is a JSON file
        file_path = os.path.join(source_dir, filename)

        # Open and read the JSON file
        with open(file_path, 'r') as f:
            chart_json = json.load(f)

        if 'transform' in chart_json:
            continue

        if 'encoding' not in chart_json:
            continue

        # remove not valid encode
        channel_ = ['theta', 'x', 'y', 'color', 'size', 'shape', 'facet', 'row', 'column']
        continue_flag = False
        field_list = []
        for key, value in chart_json['encoding'].items():
            if not isinstance(value, dict):
                continue_flag = True
            # remove not valid channel
            if key not in channel_:
                continue_flag = True
            
            for inner_key in value.keys():
                # romove field level task
                if inner_key not in ['field', 'type']:
                    continue_flag = True
                # remove double encode field
                if inner_key == 'field':
                    if value[inner_key] in field_list:
                        continue_flag = True
                    else:
                        field_list.append(value[inner_key])

        if continue_flag:
            continue

        print(file_path)
        # print(file_path, chart_json['mark'])
        # print(chart_json['encoding'])

