from llm_csv_load import load_dataset
from llm_gpt_call import call_gpt_4
import os
import json
import tqdm
import ast
import random

# Define sentence structure examples for variability
utterance_types = {
    "Commands": [
        "Please show me a histogram of weights with 500 intervals.",
        "Draw a line chart of daily sales forecasts.",
        "Show me a bar graph of the profit for each region.",
        "Make the bars stacked with the ship status.",
        "Give me the number of movies by running time.",
        "Make a simple scatter plot of worldwide Gross by Production Budget categorized by Major Genre.",
        "Create a line chart showing order date and sum of sales, divided by category.",
        "Through a visualization show average horsepower of cars for each country from 1997 to 2011."
        "for country in USA, JAPAN and EUROPE show MPG vs Displacement.",
        "For each country show the relationship between average acceleration and number of cylinders.",
        "Graph to show the acceleration for cars from different countries segregated based on number of cylinders.",
        "Draw axes for AVG(Horsepower) vs Year, colored by Origin.",
        "Sort creative types by number of movies.",
        "Help me see outliers in IMDB and Rotten Tomatoes ratings."
    ],
    "Questions": [
        "What is our profit based on shipping mode by customer segment?",
        "How much do various cars weigh?",
        "How many cars do each country manufacture?",
        "What major genre had the highest average worldwide gross?",
        "How does displacement relate to fuel economy for cars from Europe vs. USA?",
        "Which countries have the highest acceleration for cars of different cylinders?",
        "Have cars gotten lighter over time?",
        "What's the average production budget of the different rated movies, separated by creative type.",
        "Are IMDb rating and rotten tomatoes rating related?",
        "On average, how much was earned by movies of each genre?"
    ],
    "Queries": [
        "Cylinders average mpg.",
        "Scatter Production Budget vs Worldwide Gross, sliced by Content Rating.",
        "mpg vs displacement as a scatter chart.",
        "Gross versus genre.",
        "Plot IMDB rating against Rotten Tomatoes rating.",
        "Line Graph of SUM (Sales Forecast) vs Order Date.",
        "Scatter plot, sales by profit.",
        "Group cars by countries and cylinders.",
        "Compare acceleration vs weight across different countries.",
        "bar chart for mpg v/s cylinders.",
        "sales forecast between Jan 2016 and July 2017.",
        "budget over time.",
        "Total gross by genre and year.",
        "Count the movies by how long they are.",
        "Coloring by Orign, Plot Displacement by MPG.",
        "Count Sub-Category Asc."
    ],
    "Others": [
        "scatter(x=production budget, y=worldwide gross) for content rating.",
        "Trend for average horsepower over time across different origin.",
        "I want to know how many orders there are by the quantity of the order."
    ]
}

base_prompt = """Your Job:
I am developing a NL to Data Visualization Dataset. 
Please help me generate natural language utterance for given dataset and constraints.
Definition about the Taks:
- 'utterance' is what a user would say to make a chart. {structure_description} One NL 'utterance' is in one or two sentences. Here are two examples from {utterance_type} for reference:
    {utterance_example_1}
    {utterance_example_2}
- 'given dataset' is in form of column names, column type, range/unique values of the column.
- 'constraints' are information about the chart that should be included in the utterance. 
    So we can find a reference phrase in the NL utterance that corresponds to the given constraints. 
- 'reference phrase' can be explicit, ambiguous, and by_value. 'ambiguous' means the phrase can map to more than one columns in the dataset, always a hypernym of column names(depending on the dataset values).
    For example:
    {{"column": "gdpPercap", "nl_ref_type": "explicit", "nl_ref_phrase": "GDP per capita"}},
    {{"column": ["country","continent"], "nl_ref_type": "ambiguous", "nl_ref_phrase": "region"}}
    {{"column": ["country","country_short_name"], "nl_ref_type": "ambiguous", "nl_ref_phrase": "countries"}}
    {{"c_type": "mark", "c_name": "point chart", "nl_ref_type": "explicit", "nl_ref_phrase": "scatter plot"}}
    {{"c_type": "mark", "c_name": "arc chart", "nl_ref_type": "explicit", "nl_ref_phrase": "pie chart"}}
    {{"c_type": "transform","c_name": "filter","c_list": [{{"field": "country","oneOf": ["Iceland","Norway"]}}],"nl_ref_type": "explicit","nl_ref_phrase": "for countries Iceland and Norway"}},
    {{"c_type": "transform","c_name": "filter","c_list": [{{"field": "country","oneOf": ["Iceland","Norway"]}}],"nl_ref_type": "by_value","nl_ref_phrase": "for Iceland and Norway"}},
- the 'nl_ref_phrase' for 'ambiguous' columns should be equally near all ambiguous columns, not too near to one of the column since it would not be ambiguous.
    good example: {{"column": ["country","region"], "nl_ref_type": "ambiguous", "nl_ref_phrase": "location"}}
    bad example: {{"column": ["country","region"], "nl_ref_type": "ambiguous", "nl_ref_phrase": "region"}}
- You only include given constraints and no other information. 
    For example, if a column name is not in the given constraint, it will not be included in the NL utterance.
    Also, if a chart mark or chart encoding channel is not in the given constraint, it will not be included in the NL utterance.
- all 'nl_ref_phrase' shoule be included in the 'nl_utterance'. 

The output format is identical to the input format, but fill in the str blanks("...").
### Input:
"""

utterance_weights = {
    "Commands": 1,  
    "Questions": 2,  
    "Queries": 1,   
    "Others": 1     
}

# Function to generate a random prompt with two random examples
def generate_random_prompt():
    # Select random types (Commands, Questions, Queries, Others)    
    utterance_type = random.choices(
        list(utterance_types.keys()),  # sentence structure types
        weights=[utterance_weights[k] for k in utterance_types.keys()],  # corresponding weights
        k=1
    )[0]
    
    # Select one random example from each of the chosen types
    utterance_examples = random.sample(utterance_types[utterance_type], 2)
    
    if utterance_type != "Others":
        structure_description = f"It should be a {utterance_type.lower()} structure."
    else:
        structure_description = ""
    
    # Fill in the base prompt with the two selected examples
    prompt = base_prompt.format(
        utterance_type=utterance_type,
        utterance_example_1=utterance_examples[0],
        utterance_example_2=utterance_examples[1],
        structure_description=structure_description
    )
    
    return prompt

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
        # print(csv_path)
        print(os.path.exists(csv_path))
        csv_info = load_dataset(csv_path)

        column_list = csv_info['table_columns']
        table_sample = csv_info['table_samples']
        dataset_info = {
            "data samples": table_sample,
            "column names": column_list,
        }

        input = f"""Dataset Information: {json.dumps(dataset_info, indent=2)}\n\n""" + generate_random_prompt() + json.dumps(constraints, indent=2) + """\n\n### Output:"""
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
    




