# GPT calling
import os
import json
import openai
from retrying import retry

openai.api_base = 'https://gpt-api.hkust-gz.edu.cn/v1'
openai.api_key = "736096cf53d34617afb48933d78d7c405420d6b8e6804e819622b4f2d2091d8c"

def call_gpt_3_5(user_content, sys_content):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": sys_content},
            {"role": "user", "content": user_content}
        ],
    )
    result = response.choices[0].message.content
    token_usage = response.usage
    return result, token_usage

@retry(stop_max_attempt_number=3, wait_fixed=2000)  # 重试3次，每次间隔2秒
def call_gpt_4(user_content, sys_content=""):
    print("call gpt 4.")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": sys_content},
            {"role": "user", "content": user_content}
        ],
    )
    # print("gpt4 response: ", response)
    result = response.choices[0].message.content
    token_usage = response.usage
    return result, token_usage


def call_gpt_4_1106(user_content, sys_content):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": sys_content},
            {"role": "user", "content": user_content}
        ],
    )
    
    result = response.choices[0].message.content
    token_usage = response.usage

    return result, token_usage