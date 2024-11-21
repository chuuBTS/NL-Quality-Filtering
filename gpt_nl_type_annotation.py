import openai
import json
import os

from llm_gpt_call import call_gpt_4

# Set OpenAI API key
openai.api_base = 'https://gpt-api.hkust-gz.edu.cn/v1'
openai.api_key = "736096cf53d34617afb48933d78d7c405420d6b8e6804e819622b4f2d2091d8c"

prompt = """You are an expert in natural language understanding. Your task is to classify the given natural language (NL) utterance into one of four types. Respond **only in lowercase**.

1. **command**: Instructions or requests that ask the system to perform a specific action. These often contain imperatives like "show", "create", "draw", or "make".
   Examples:
   - "Please show me a histogram of weights with 500 intervals."
   - "Draw a line chart of daily sales forecasts."
   - "Make a simple scatter plot of worldwide Gross by Production Budget categorized by Major Genre.",

2. **question**: Requests for information or insights that require a response, often starting with "what", "how", "which", or "are".
   Examples:
   - "What is our profit based on shipping mode by customer segment?"
   - "How much do various cars weigh?"
   - "Have cars gotten lighter over time?"

3. **query**: Statements that describe data relationships, charts, or summaries, often concise and focusing on what to display.
   Examples:
   - "Cylinders average mpg."
   - "Scatter Production Budget vs Worldwide Gross, sliced by Content Rating."
   - "bar chart for mpg v/s cylinders."

4. **other**: NL utterances that don’t fit into the above categories, such as incomplete sentences, unclear instructions, or unrelated statements.
   Examples:
   - "scatter(x=production budget, y=worldwide gross) for content rating."
   - "Trend for average horsepower over time across different origin."
   - "I want to know how many orders there are by the quantity of the order."

Now, classify the following NL utterance:
"{nl_utterance}"

Type (choose one from: command, question, query, other):"""


# Define the main function
def annotate_file(input_file, output_file):
    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"The input file {input_file} does not exist.")
        return

    # Load the input JSON file
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Create a new dictionary to store the annotated results
    annotated_data = {}

    # Iterate through each entry and predict the type for "nl_utterance"
    for file_name, content in data.items():
        nl_utterance = content.get("nl_utterance", "")
        
        input = prompt.format(nl_utterance=nl_utterance)
        # call gpt 4
        nl_type, token = call_gpt_4(input)# Call GPT API to predict the type
        
        annotated_data[file_name] = {"nl_type": nl_type}
        print(f"Processed: {file_name}, Type: {nl_type}")

    # Write the annotated results to a new JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(annotated_data, f, ensure_ascii=False, indent=4)
    print(f"Annotation results have been saved to {output_file}")

# File paths
input_file = "data/mr_test.json"
output_file = "data/gpt_annotation_result.json"

# Run the annotation process
annotate_file(input_file, output_file)
