import pandas as pd
import os
import json
from dateutil.parser import parse

# 判断一个字符串是否可以被解析为日期
def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except:
        return False

# 检查一个 DataFrame 的指定列是否为时间列。通过抽样 50 个样本来判断。
def is_temporal_column(df, column_name):
    """
    Checks if a specified column in a pandas DataFrame is a temporal column by sampling n=10 samples.

    :param df: pandas.DataFrame, DataFrame containing the data
    :param column_name: str, name of the column to check
    :return: bool, True if the column is temporal, False otherwise
    """
    # Check if the column exists in the DataFrame
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame.")
    
    non_na_values = df[column_name].dropna()
    n = 50
    if len(non_na_values) >= n: 
        sample_values = non_na_values.sample(n=n)

        # if sample_values.dtype == float:
        #     # Check if all values in sample can be converted to int without loss of information
        #     if all(sample_values == sample_values.astype(int)):
        #         sample_values = sample_values.astype(int)
        # sample_values = sample_values.astype(str)

        return all(sample_values.apply(is_date))
    else:
        new_n = len(non_na_values)
        sample_values = non_na_values.sample(n=new_n)
        return all(sample_values.apply(is_date))
    
# def is_location_column(df, column_name):
#     """
#     Checks if a specified column in a pandas DataFrame is a location column by sampling a single value.
#     """
#     # Check if the column exists in the DataFrame
#     if column_name not in df.columns:
#         raise ValueError(f"Column '{column_name}' not found in DataFrame.")
    
#     non_na_values = df[column_name].dropna()
#     n = 10
#     if len(non_na_values) >= n:  # Ensure there are at least three non-NA values
#         sample_values = non_na_values.sample(n=n)
#         # Check if all sampled values are locations
#         for val in sample_values:
#             # print(val)
#             if check_location_in_str(val):
#                 return True
#     else:
#         # If there are not enough non-NA values to sample, the column can't be determined as location
#         return False

# from scipy.stats import entropy

# # Redefining the calculate_entropy function
# def calculate_entropy(column):
#     value_counts = column.value_counts()
#     probabilities = value_counts / len(column)
#     return round(entropy(probabilities) * 100, 2)

# 生成数据集的统计信息，包括每列的类型、唯一值等。    
def dataset_statistic(df, column_with_type):
    json_output = {}

    for field in df.columns:
        # 检查 column_with_type 中是否包含当前字段
        if field not in column_with_type:
            print(f"字段 {field} 不存在于 column_with_type 中，跳过该字段")
            continue

        json_output[field] = {}
        json_output[field]['name'] = field

        # 后续的代码保持不变
        if column_with_type[field]['type'] == 'temporal':
            json_output[field]['type'] = 'temporal'
            json_output[field]['unique_value'] = df[field].unique().tolist()[:10]
        elif column_with_type[field]['type'] == 'nominal':
            json_output[field]['type'] = 'nominal'
            json_output[field]['unique_value'] = df[field].unique().tolist()[:10]
        elif column_with_type[field]['type'] == 'quantitative':
            json_output[field]['type'] = 'quantitative'
            json_output[field]['range'] = [df[field].min(), df[field].max()]

        json_output[field]['num_unique_value'] = df[field].nunique()

    return json_output


# 确定 DataFrame 中每一列的数据类型（时间、名义或定量）。
def get_column_with_type(df):
    column_with_type = {}
    for field in df.columns:
        # get field name
        if pd.api.types.is_datetime64_any_dtype(df[field]):
            column_with_type[field] = {'type': 'temporal'}
        elif pd.api.types.is_string_dtype(df[field]):
            if is_temporal_column(df, field):
                # print("nomial as temporal: ", field)
                column_with_type[field] = {'type': 'temporal'}
            else:
                column_with_type[field] = {'type': 'nominal'}
        elif pd.api.types.is_numeric_dtype(df[field]):
            column_with_type[field] = {'type': 'quantitative'}
            ##### is_temporal_column does not work for quantitative, so don't do so
            ##### since parse("105.890447", fuzzy=False) -> datetime.datetime(105, 3, 3, 0, 0)
            # if is_temporal_column(df, field):    
            #     column_with_type[field] = {'type': 'temporal'}
            # else:
            #     column_with_type[field] = {'type': 'quantitative'}
        elif pd.api.types.is_bool_dtype(df[field]):
            column_with_type[field] = {'type': 'nominal'}

        # # additional rule
        # if field == "Year" or field == "year":
        #     column_with_type[field] = {'type': 'temporal'}
            
    return column_with_type

# data loading 加载数据集并生成其结构的 JSON 表示，包括列名、样本数据、列的基本信息和类型。
def load_dataset(file_path):
    file_name = os.path.basename(file_path)

    encodings = ['utf-8', 'ISO-8859-1', 'cp1252', 'latin1']
    df = None
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            print(f"Successfully read file with encoding: {encoding}")
            break
        except Exception as e:
            print(f"Error reading file with encoding {encoding}: {e}")
    
    if df is None:
        print("Unable to read the file with any of the specified encodings.")
        return None

    if df.empty:
        print("The DataFrame is empty.")
        return None

    if 'emoji' in df.columns:
        del df['emoji']

    columns = df.columns.tolist()
    first_samples = df.head(1).to_dict(orient='records')
    sample_size = min(4, len(df) - 1)
    random_samples = df.iloc[1:].sample(sample_size).to_dict(orient='records')
    samples = first_samples + random_samples

    column_with_type = get_column_with_type(df)
    statistic = dataset_statistic(df, column_with_type)

    json_structure = {
        "table_name": file_name,
        "table_columns": columns,
        "table_samples": samples,
        "column_info_basic": statistic,
        "column_with_type": column_with_type
    }

    return json_structure

# file_path = "../vega-dataset/csv_data/airports.csv"
# dataset_info = load_dataset(file_path)

# print_json(dataset_info)
