from string import Template

# $variable 作为占位符
PROMPT_TEMPLATE = Template("""
### requirement: Based on the current table_schema, generate a list of the most appropriate charts that best fulfill the current user_query. The user_query may be ambiguous or under_specified, meaning there could be multiple valid charts (approximately 2 to 5) that satisfy the intent.
The output should:
-Be written in Vega-Lite style JSON.
-Include 'mark', 'encoding', and 'transform' that fully capture the user query.
-Generate 2 to 5 valid charts based on the table_schema and user_query, ensuring relevance and diversity in chart types and configurations.
-Refer to the following examples for format and style.

### example1 table_schema: table columns: ["State","Population","Type1","Value","ValueC"] table sample (first row): {"State": "Alabama","Population": 5039877,"Type1": "Lawful Permanent Residents","Value": 2887.0,"ValueC": 0.057283144}
### example1 user_query: Show the sum of ValueC for each Type1 category.
### example1 output: [{"mark":"arc","encoding":{"theta":{"field":"ValueC","type":"quantitative","aggregate":"sum"},"color":{"field":"Type1","type":"nominal"}}}, {"mark":"bar","encoding":{"x":{"field":"Type1","type":"nominal"},"y":{"field":"ValueC","type":"quantitative","aggregate":"sum"}}}, {"mark":"point","encoding":{"x":{"field":"ValueC","type":"quantitative","aggregate":"sum"},"y":{"field":"Type1","type":"nominal"}}}, {"mark":"point","encoding":{"x":{"field":"Type1","type":"nominal"},"y":{"field":"ValueC","type":"quantitative","aggregate":"sum"}}}]

### example2 table_schema: table columns: ["date","month","sourceDataset","updateDate","value","year"] table sample (first row): {"date": "1971 FEB","month": "February", "sourceDataset": "LMS","updateDate": "2015-10-13T23:00:00.000Z","value": 3.8,"year": 1971}
### example2 user_query: What is the trend in value over time based on the date?
### example1 output: [{"mark":"line","encoding":{"x":{"field":"date","type":"temporal"},"y":{"field":"value","type":"quantitative"}}}, {"mark":"area","encoding":{"x":{"field":"date","type":"temporal"},"y":{"field":"value","type":"quantitative"}}}]

### current table_schema: table columns: $table_columns table sample (first row): $table_sample
### current user_query: $nl_utterance
### output: (to be generated)
""")

def get_prompt(table_columns, table_sample, nl_utterance):
    """
    生成prompt，使用Template类来处理变量替换
    """
    return PROMPT_TEMPLATE.substitute(
        table_columns=table_columns,
        table_sample=table_sample,
        nl_utterance=nl_utterance
    )
