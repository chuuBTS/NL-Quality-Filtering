
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

        print(file_path)
        # print(file_path, chart_json['mark'])
        # print(chart_json['encoding'])

