import json

def filter_annotations(input_file, filter_file, output_file):
    # Step 1: Load the filtered chart types result
    with open(filter_file, 'r', encoding='utf-8') as f:
        filtered_data = json.load(f)
    
    # Extract all valid keys from the filtered result
    valid_keys = set(filtered_data.keys())

    # Step 2: Load the GPT annotation result
    with open(input_file, 'r', encoding='utf-8') as f:
        gpt_data = json.load(f)
    
    # Step 3: Filter the annotations based on the valid keys
    filtered_annotations = {key: value for key, value in gpt_data.items() if key in valid_keys}

    # Step 4: Save the filtered annotations to a new file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_annotations, f, indent=4, ensure_ascii=False)

# Example usage
filter_annotations('../data/gpt_annotation_result.json', '../data/filtered_chart_types_result.json', '../data/annotation_result.json')
