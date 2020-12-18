"""
测试项目web api
"""
import json
import requests
from config import global_config

SRC_LANG = global_config["translate_src_lang"]
SERVE_PORT = global_config["serve_port"]
URL = "http://127.0.0.1:{}/yyq/translate".format(SERVE_PORT)


def test_method_translate():
    """
    测试翻译接口
    """
    if SRC_LANG == "zh":
        sent = "正确使用数据操作，掌握排序与限量"
    elif SRC_LANG == "en":
        sent = "Please input a word."
    data = {
        "method": "translate",
        "data": {
            "input": sent
        }
    }
    result = requests.post(URL, json=data)
    response_data = json.loads(result.text)
    assert response_data["status"] == "200"


def test_method_term_protection():
    """
    测试术语保护相关的接口
    """
    # 添加术语
    words = [
        ["填方", "filling"],
        ["跳线线夹", "jumper clamp"]
    ]
    data = {
        "method": "add_words",
        "data": {
            "words": words
        }
    }
    result = requests.post(URL, json=data)
    response_data = json.loads(result.text)
    assert response_data["status"] == "200"

    # 请求获取当前所有词典
    data = {
        "method": "show_words"
    }
    result = requests.post(URL, json=data)
    response_data = json.loads(result.text)
    for item in words:
        assert item in response_data["data"]["words"]

    # 请求翻译
    for src_word, tgt_word in words:
        data = {
            "method": "translate",
            "data": {
                "input": src_word
            }
        }
        result = requests.post(URL, json=data)
        response_data = json.loads(result.text)
        assert response_data["data"]["translation"] == tgt_word


def main():
    """
    测试程序入口
    """
    test_method_translate()
    test_method_term_protection()


if __name__ == "__main__":
    main()
