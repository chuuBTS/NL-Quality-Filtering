# GPT calling
import os
import json
import openai
from retrying import retry
import time
openai.api_base = 'https://gpt-api.hkust-gz.edu.cn/v1'
openai.api_key = "736096cf53d34617afb48933d78d7c405420d6b8e6804e819622b4f2d2091d8c"

@retry(stop_max_attempt_number=3, wait_fixed=4000)  # 重试3次，每次间隔2秒
def call_gpt_3_5(user_content, sys_content=""):
    print("call gpt 3.5")
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


@retry(stop_max_attempt_number=3, wait_fixed=2000)  # 重试3次，每次间隔2秒
def call_gpt_4o_20240806(user_content, sys_content=""):
    print("call gpt 4o.")
    response = openai.ChatCompletion.create(
        model="gpt-4", # gpt-4o-2024-08-06
        messages=[
            {"role": "system", "content": sys_content},
            {"role": "user", "content": user_content}
        ],
    )
    
    result = response.choices[0].message.content
    token_usage = response.usage

    return result, token_usage

# 测试 GPT 模型
if __name__ == "__main__":
    max_attempts = 3
    attempt = 1
    
    while attempt <= max_attempts:
        try:
            print(f"开始第{attempt}次测试 GPT 模型...")
            test_content = "你好,请用一句话介绍你自己"
            result, usage = call_gpt_3_5(test_content)
            print(f"测试成功!")
            print(f"模型返回: {result}")
            print(f"Token 使用情况: {usage}")
            break
        except Exception as e:
            print(f"第{attempt}次测试失败,错误信息: {str(e)}")
            if attempt == max_attempts:
                print("已达到最大重试次数")
            attempt += 1
