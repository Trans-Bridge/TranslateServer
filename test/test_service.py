"""
测试项目web api
"""
import json
import os
import time

import requests

CWD = os.path.abspath(os.path.dirname(__file__))

def test_performance(url, src_lang):
    """
    测试翻译接口的性能，测试标准以为中英文100字（词）为标准
    """
    # 从assets文件夹中取出对应的测试语料
    test_file = os.path.join(CWD, "assets", src_lang)
    if not os.path.exists(test_file):
        raise NotImplementedError(
            "Test cases for source language "
            "{} have not been NotImplemented yet. ".format(src_lang))
    with open(test_file, "r") as f_open:
        lines = f_open.readlines()

    start_time = time.time()
    total_lines = len(lines)

    for sent in lines:
        data = {
            "method": "translate",
            "data": {
                "input": sent
            }
        }
        result = requests.post(url, json=data)
    end_time = time.time()

    avg_time = (end_time - start_time) / total_lines
    print("The average response time per request of {} is {}s.".format(url, avg_time))


def test_method_translate(url, src_lang):
    """
    测试翻译接口
    """
    if src_lang == "zh":
        sent = "正确使用数据操作，掌握排序与限量"
    elif src_lang == "en":
        sent = "Please input a word."
    else:
        raise NotImplementedError(
            "Test cases for source language "
            "{} have not been NotImplemented yet. ".format(src_lang))
    data = {
        "method": "translate",
        "data": {
            "input": sent
        }
    }
    result = requests.post(url, json=data)
    response_data = json.loads(result.text)
    assert response_data["status"] == "200"


def test_method_term_protection(url):
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
    result = requests.post(url, json=data)
    response_data = json.loads(result.text)
    assert response_data["status"] == "200"

    # 请求获取当前所有词典
    data = {
        "method": "show_words"
    }
    result = requests.post(url, json=data)
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
        result = requests.post(url, json=data)
        response_data = json.loads(result.text)
        if tgt_word not in response_data["data"]["translation"]:
            print("test_term_protectioin:\nurl: {}\nsrc: {}\nexpected: {}\ntranslation: {}\n".format(
                url, src_word, tgt_word, response_data["data"]["translation"])
            )


def main():
    """
    测试程序入口
    """
    from config import global_config

    src_lang = global_config["translate_src_lang"]
    serve_port = global_config["serve_port"]
    url = "http://127.0.0.1:{}/yyq/translate".format(serve_port)

    test_method_translate(url, src_lang)
    test_method_term_protection(url)
    test_performance(url, src_lang)


if __name__ == "__main__":
    main()
