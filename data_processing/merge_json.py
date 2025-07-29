import glob
import json
import os
import re

global nochart_num 
nochart_num = 0

def merge_json(json_files, charts_files_path):
    global nochart_num
    merged_result = {}

    for json_file in json_files:
        # Use the original filename as the key
        file_name = os.path.basename(json_file)

        try:
            # Read the contents of the JSON file
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Generate the corresponding charts JSON file path
            charts_file = os.path.join(charts_files_path, file_name)
            
            # Read the corresponding dataset JSON for chart info
            try:
                with open(charts_file, "r", encoding="utf-8") as charts_file:
                    charts_file_data = json.load(charts_file)
                    generated_chart_list = charts_file_data.get("generated_chart_list", [])
                    
                    # Add the $schema and data URL to each chart in the list
                    for chart in generated_chart_list:
                        csv_file_name = re.match(r"([^_]+_[^_]+)", file_name).group(0)  # Capture part before the second underscore
                        chart_with_schema_and_data = {
                            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                            "data": {
                                "url": f"https://raw.githubusercontent.com/chuuBTS/NL-Quality-Filtering/refs/heads/main/chart_dataset_csv/{csv_file_name}.csv",
                                "format": {"type": "csv"}
                            }
                        }
                        
                        # Merge the original chart data into the new dictionary (this keeps the original keys intact)
                        chart_with_schema_and_data.update(chart)
                        
                        # Now `chart_with_schema_and_data` contains `$schema` and `data` at the front
                        # Directly modify the chart in the list
                        chart.clear()  # Clear current chart contents
                        chart.update(chart_with_schema_and_data)  # Update it with the new dictionary
                    
            except Exception as e:
                print(f"Error reading dataset file {charts_file}: {e}")
                nochart_num += 1
                continue  # Skip the current file and continue with the next
                # generated_chart_list = []  # Set it to an empty list if there's an error
                

            # Extract the required structure, using the get() method to avoid errors when fields are missing
            transformed_data = {
                "nl_utterance": data.get("gpt_result", {}).get(
                    "nl_utterance", ""
                ),  # Default to an empty string
                "encoded_fields": [
                    {
                        "field": ef.get("field", ""),
                        "nl_ref_phrase": ef.get("nl_ref_phrase", ""),
                    }
                    for ef in data.get("gpt_result", {}).get("encoded_fields", [])
                ],
                "transform_constraints": [
                    {
                        "c_name": tc.get("c_name", ""),
                        "field": (
                            tc.get("c_list", [{}])[0].get("field", "")
                            if tc.get("c_list")
                            and isinstance(tc.get("c_list", [{}])[0], dict)
                            and "field" in tc.get("c_list", [{}])[0]
                            else " "
                        ),
                        "details": (
                            # Handle different types of constraints
                            ", ".join(tc.get("c_list", [{}])[0].get("oneOf", []))
                            if tc.get("c_list")
                            and isinstance(tc.get("c_list", [{}])[0], dict)
                            and "oneOf" in tc.get("c_list", [{}])[0]
                            else (
                                tc.get("c_list", [{}])[0].get("aggregate", "")
                                if tc.get("c_list")
                                and isinstance(tc.get("c_list", [{}])[0], dict)
                                and "aggregate" in tc.get("c_list", [{}])[0]
                                else (
                                    str(tc.get("c_list", [{}])[0].get("equal", ""))
                                    if tc.get("c_list")
                                    and isinstance(tc.get("c_list", [{}])[0], dict)
                                    and "equal" in tc.get("c_list", [{}])[0]
                                    else (
                                        f"{tc.get('c_list', [{}])[0].get('range', [])[0]}-{tc.get('c_list', [{}])[0].get('range', [])[1]}"
                                        if tc.get("c_list")
                                        and isinstance(tc.get("c_list", [{}])[0], dict)
                                        and "range" in tc.get("c_list", [{}])[0]
                                        and tc.get("c_list", [{}])[0].get("range")  # 确保range存在且不为空
                                        else (
                                            ", ".join(map(str, tc.get("c_list", [])[0]))
                                            if tc.get("c_list")
                                            and isinstance(tc.get("c_list", [])[0], (list, tuple))
                                            else (
                                                str(tc.get("c_list", [])[0])
                                                if tc.get("c_list")
                                                else " "
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                        "nl_ref_phrase": tc.get("nl_ref_phrase", ""),
                    }
                    for tc in data.get("gpt_result", {}).get("constraints", [])
                    if tc.get("c_type", "") == "transform"
                ],
                "mark_constraints": [
                    {
                        "c_name": mc.get("c_name", ""),
                        "mark": (
                            mc.get("c_list", [{}])[0].get("mark", "")
                            if mc.get("c_list")
                            and isinstance(mc.get("c_list", [{}])[0], dict)
                            and "mark" in mc.get("c_list", [{}])[0]
                            else " "
                        ),
                        "nl_ref_phrase": mc.get("nl_ref_phrase", ""),
                    }
                    for mc in data.get("gpt_result", {}).get("constraints", [])
                    if mc.get("c_type", "") == "mark" or mc.get("c_type", "") == "task"
                ],
                "generated_chart_list": generated_chart_list
            }

            # Add the transformed data to the merged dictionary
            merged_result[file_name] = transformed_data

        except Exception as e:
            # If an error occurs, print the file path and error message
            print(f"Error processing file {json_file}: {e}")
            continue  # Skip the current file and continue with the next

    return merged_result


# List of file paths
json_files = glob.glob("./generated_nl_gpt_json/*.json")
charts_files_path = os.path.join(".", "upload_dataset_task_1_new")
# json_files = ["./generated_nl_gpt_json/vl_0031_combi_0.json","./generated_nl_gpt_json/vl_0031_combi_1.json","./generated_nl_gpt_json/vl_0031_combi_2.json"]
# json_files = ["./generated_nl_gpt_json/vl_1721_combi_4.json"]
merged_result = merge_json(json_files, charts_files_path)

# Output to a new file
with open("./data/merged_result.json", "w", encoding="utf-8") as f:
    json.dump(merged_result, f, ensure_ascii=False, indent=4)
    
print(f"No chart number: {nochart_num}")
