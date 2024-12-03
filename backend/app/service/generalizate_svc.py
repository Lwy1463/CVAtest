import requests
import base64
import json
import re
from app.middleware.log import logger as log


# 解码后的 API 密钥
# api_key = base64.b64decode("YXBwLWNSaFQwQjRTdVFVdXpZazJKZFppTTQ1aA==").decode("utf-8")
api_key = "app-vuKWOpRqBnCnnNb8kUUFMzlb"
url = "https://api.dify.ai/v1/chat-messages"


def generalizate(text):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json;charset=UTF-8"
    }

    # 请求数据
    data = {
        "inputs": {},
        "query": text,
        "conversation_id": "",
        "user": "abc-123"
    }
    response = requests.post(url, headers=headers, json=data)
    # 解析响应
    if response.status_code == 200:
        result = response.json().get("answer")
        if "[" in result:
            matches = re.search(r"\[(.*?)\]", result, re.S)
            # 包含方括号的完整字符串
            if matches:
                tmp_str = f"[{matches.group(1)}]"
                json_list = json.loads(tmp_str)
                return json_list
        else:
            result_list = result.split("\n")
            for i in range(len(result_list)):
                result_list[i] = re.sub(r'^\d+\.\s*', '', result_list[i]).strip()
            return result_list
    else:
        log.warn(f"status_code: {response.status_code}, error: {response.json()}")
    return []
