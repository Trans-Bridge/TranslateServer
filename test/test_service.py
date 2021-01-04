"""
测试项目web api
"""
import json
import requests


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
    # print("url: {}\nsrc: {}\ntranslation: {}".format(
    #  url, sent, response_data["data"]["translation"]))


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


if __name__ == "__main__":
    main()
