import json

def filter_mismatched_chart_types(input_file, output_file):
    # Step 1: Load the JSON data with explicit UTF-8 encoding
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Step 2: Process each entry in the data
    keys_to_remove = []  # To keep track of keys to remove
    
    for key, value in data.items():
        # Get the mark constraints and make sure it's a list
        mark_constraints = value.get('mark_constraints', [])
        mark_list = []
        
        if isinstance(mark_constraints, list):
            for mark_constraints_value in mark_constraints:
                if isinstance(mark_constraints_value, dict):
                    mark_list.extend(mark_constraints_value.get('mark', []))  # Handle if mark is a list inside a dict
                elif isinstance(mark_constraints_value, str):
                    mark_list.append(mark_constraints_value)
        elif isinstance(mark_constraints, dict) and 'mark' in mark_constraints:
            mark_list.append(mark_constraints['mark'])

        # Step 3: Skip filtering if mark_list is empty
        if not mark_list:
            continue  # Skip to the next chart if no mark constraints are provided

        # Step 4: Filter the charts only if mark_list is not empty
        valid_charts = []
        for chart in value.get('generated_chart_list', []):
            chart_mark = chart.get('mark')
            if chart_mark in mark_list:
                valid_charts.append(chart)
        
        # If no valid charts are found, mark the entry for removal
        if not valid_charts:
            keys_to_remove.append(key)
        else:
            # Update the generated chart list with valid charts
            value['generated_chart_list'] = valid_charts
    
    # Step 5: Remove the entries with no valid charts
    for key in keys_to_remove:
        del data[key]
        
    print(len(data))
    # Step 6: Save the filtered result to a new file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Example usage
filter_mismatched_chart_types('data/merged_result.json', 'data/filtered_chart_types_result1.json')
