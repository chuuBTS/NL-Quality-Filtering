from llm_csv_load import load_dataset
from llm_gpt_call import call_gpt_4
import os
import json
import tqdm
import ast

prompt = """Your Job:
I am developing a NL to Data Visualization Dataset. 
Please help me generate natural language utterance for given dataset and constraints.
Definition about the Taks:
- 'utterance' is what a user would say to make a chart, it can be a question or a command. One NL 'utterance' is in one or two sentences. 
- 'given dataset' is in form of column names, column type, range/unique values of the column.
- 'constraints' are information about the chart that should be included in the utterance. 
    So we can find a reference phrase in the NL utterance that corresponds to the given constraints. 
- 'reference phrase' can be explicit, ambiguous, and by_value. 'ambiguous' means the phrase can map to more than one columns in the dataset, always a hypernym of column names(depending on the dataset values).
    For example:
    {"column": "gdpPercap", "nl_ref_type": "explicit", "nl_ref_phrase": "GDP per capita"},
    {"column": ["country","continent"], "nl_ref_type": "ambiguous", "nl_ref_phrase": "region"}
    {"column": ["country","country_short_name"], "nl_ref_type": "ambiguous", "nl_ref_phrase": "countries"}
    {"c_type": "mark", "c_name": "point chart", "nl_ref_type": "explicit", "nl_ref_phrase": "scatter plot"}
    {"c_type": "mark", "c_name": "arc chart", "nl_ref_type": "explicit", "nl_ref_phrase": "pie chart"}
    {"c_type": "transform","c_name": "filter","c_list": [{"field": "country","oneOf": ["Iceland","Norway"]}],"nl_ref_type": "explicit","nl_ref_phrase": "for countries Iceland and Norway"},
    {"c_type": "transform","c_name": "filter","c_list": [{"field": "country","oneOf": ["Iceland","Norway"]}],"nl_ref_type": "by_value","nl_ref_phrase": "for Iceland and Norway"},
- the 'nl_ref_phrase' for 'ambiguous' columns should be equally near all ambiguous columns, not too near to one of the column since it would not be ambiguous.
    good example: {"column": ["country","region"], "nl_ref_type": "ambiguous", "nl_ref_phrase": "location"}
    bad example: {"column": ["country","region"], "nl_ref_type": "ambiguous", "nl_ref_phrase": "region"}
- You only include given constraints and no other information. 
    For example, if a column name is not in the given constraint, it will not be included in the NL utterance.
    Also, it a chart mark or chart encoding channel is not in the given constraint, it will not be included in the NL utterance.
- all 'nl_ref_phrase' shoule be included in the 'nl_utterance'. 

The output format is identical to the input format, but fill in the str blanks("...").
### Input:
"""

if __name__ == "__main__":
    constraints_dir = './selected_constraint/'
    filename_list = os.listdir(constraints_dir)
    filename_list.sort()
    # make filename list random
    import random
    random.seed(0)
    random.shuffle(filename_list)
    random_filename_list = filename_list[:-1]

    run_filename_list = []
    for filename in tqdm.tqdm(random_filename_list):
        save_result_path = f'./generated_nl_gpt/{filename}'
        if os.path.exists(save_result_path):
            continue
        run_filename_list.append(filename)


    for filename in tqdm.tqdm(run_filename_list):
        # save_result_path = f'./generated_nl_gpt/{filename}'
        # if os.path.exists(save_result_path):
        #     continue

        idx_num = filename.split('.')[0].split('_')[1]
        idx_str = 'vl_' + idx_num

        file_path = os.path.join(constraints_dir, filename)
        print(file_path)
        with open(file_path, 'r') as f:
            constraints = json.load(f)

        # print(constraints)

        csv_path = f'./chart_dataset_csv/{idx_str}.csv'

        # 检查CSV文件是否存在
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            continue

        csv_info = load_dataset(csv_path)
        column_list = csv_info['table_columns']
        table_sample = csv_info['table_samples']
        dataset_info = {
            "data samples": table_sample,
            "column names": column_list,
        }

        input = f"""Dataset Information: {json.dumps(dataset_info, indent=2)}\n\n""" + prompt + json.dumps(constraints, indent=2) + """\n\n### Output:"""
        # call gpt 4
        output, token = call_gpt_4(input)
        
        # try parse output
        try:
            output = ast.literal_eval(output)
        except:
            pass

        # save
        save_json = {
            "gpt_result": output,
            "input": input
        }
        save_result_path = f'./generated_nl_gpt/{filename}'
        with open(save_result_path, 'w') as f:
            json.dump(save_json, f, indent=2)
    




