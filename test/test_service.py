import requests
import json
from config import global_config

# 加载所需要的配置
domain = global_config["domain"]
src_lang = global_config["src_lang"]
tgt_lang = global_config["tgt_lang"]
logdir = global_config["logdir"]


# 测试正常请求
url = "http://127.0.0.1:10000/yyq/translate/{}/{}/{}".format(domain, src_lang, tgt_lang)
data = {
    "input": "正确使用数据操作，掌握排序与限量"
}
result = requests.post(url, json=data)
response_data = json.loads(result.text)
assert response_data["status"] == "200"

# 测试请求字符串过长或者过短
data = {
    "input": ""
}
result = requests.post(url, json=data)
response_data = json.loads(result.text)
assert response_data["status"] == "500"