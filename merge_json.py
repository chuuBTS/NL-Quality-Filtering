import glob
import json
import os


def merge_json(json_files):
    merged_result = {}

    for json_file in json_files:
        # Use the original filename as the key
        file_name = os.path.basename(json_file)

        try:
            # Read the contents of the JSON file
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

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
                            # Ensure c_list is a list and has elements before accessing
                            # Check if the first element of c_list is a dictionary (key-value pair)
                            tc.get("c_list", [{}])[0].get("oneOf", "")
                            if tc.get("c_list")
                            and isinstance(tc.get("c_list", [{}])[0], dict)
                            and "oneOf" in tc.get("c_list", [{}])[0]
                            else (
                                tc.get("c_list", [{}])[0].get("aggregate", "")
                                if tc.get("c_list")
                                and isinstance(tc.get("c_list", [{}])[0], dict)
                                and "aggregate" in tc.get("c_list", [{}])[0]
                                # If c_list contains a string, return it directly
                                else (
                                    tc.get("c_list", [])[0]
                                    if tc.get("c_list")
                                    and isinstance(tc.get("c_list", [])[0], str)
                                    else " "
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
# json_files = ["./generated_nl_gpt_json/vl_0031_combi_0.json","./generated_nl_gpt_json/vl_0031_combi_1.json","./generated_nl_gpt_json/vl_0031_combi_2.json"]
# json_files = ["./generated_nl_gpt_json/vl_1721_combi_4.json"]
merged_result = merge_json(json_files)

# Output to a new file
with open("./data/merged_result.json", "w", encoding="utf-8") as f:
    json.dump(merged_result, f, ensure_ascii=False, indent=4)
