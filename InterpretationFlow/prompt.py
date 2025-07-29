from string import Template

# 定义提示词模板
PROMPT_TEMPLATE = Template("""
You are a tagging model designed to annotate natural language queries for data visualization tasks. Your task is to assign a tag to each word or phrase in a query. 

- Use the predefined visualization-related tags if the word or phrase matches any concept in the provided list.
- If the word or phrase is not related to visualization, assign standard NLP part-of-speech (POS) tags (e.g., DET, NOUN, VERB, ADP).
- Always tag from left to right in sequence.
- You can tag either individual words or meaningful phrases as a whole unit.

Here are the predefined visualization-related tags:

| **Tag**        | **Description**                                                          | **Examples**                                                                                   |
|----------------|--------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| **`VisGoal`**  | Visualization task, the analysis task the user wants to complete, including **Find Correlation, Find Trend, Find Distribution, Find Extremum** | `trend`, `the change of`, `compare`, `distribution`, `find extremum`, `relationship`, `correlation`, `variation` |
| **`ChartType`**| Chart type, if explicitly mentioned                                      | `line chart`, `bar chart`, `pie chart`, `scatterplot`, `box plot`, `histogram`, `area chart`  |
| **`Field`**    | Data attribute, the main fields involved in the user query               | `temperature`, `sales`, `revenue`, `expenses`, `age`, `income`, `region`                     |
| **`SORT`**     | Sorting operation                                                       | `sort`, `order`, `ascending`, `descending`, `from high to low`, `highest first`               |
| **`AGG`**      | Aggregation operation, the type of aggregation the user wants to perform | `mean`, `sum`, `average`, `total`, `count`, `maximum`, `minimum`, `median`, `gross`           |
| **`Bin`**      | Binning operation, dividing continuous data into discrete intervals      | `bin`, `bucketize`, `in 5-year bins`, `bucketize by range`, `group into intervals of 10`      |
| **`Filter`**   | Filtering condition, involves selecting specific data                   | `for Action movies`, `greater than 10`, `less than 5`, `only include`, `exclude`, `filter by`, `from 1995 to 2020`, `in 2021`, `before 2020` |

---

### Expected Output Format

For each word or phrase in the query, output a JSON array where each element contains:
- "txt": the word or phrase being tagged
- "tag": the corresponding tag

---



### Example Input NL: What trends can be observed in the rents over the years from 2010 to 2020?

### Example Input table_info: table_columns: ["Year", "Oil rents (% of GDP)", "Natural Gas rents (% of GDP)", "Ratio"], table_sample (first row): {"Year": 1990, "Oil rents (% of GDP)": 9.61381294, "Natural Gas rents (% of GDP)": 2.722685294, "Ratio": 3.531004101}

### Example output:
[
    {"txt": "What", "tag": "DET"},
    {"txt": "trends", "tag": "VisGoal"},
    {"txt": "can be observed", "tag": "VERB"},
    {"txt": "in the rents", "tag": "Field"},
    {"txt": "over the years", "tag": "Field"},
    {"txt": "from 2010 to 2020", "tag": "Filter"},
    {"txt": "?", "tag": "PUNCT"}
]

### current Input NL: $NL
### current Input table_info: table columns: $table_columns table sample (first row): $table_sample
### output: (to be generated)
""")

def get_prompt(NL, table_columns, table_sample):
    """
    生成prompt，使用Template类来处理变量替换
    """
    return PROMPT_TEMPLATE.substitute(
        NL=NL, 
        table_columns=table_columns,
        table_sample=table_sample,
        )