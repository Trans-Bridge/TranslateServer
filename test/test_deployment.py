"""
对部署的模型进行测试
"""
import argparse
import os
from test.test_service import (test_method_term_protection,
                               test_method_translate, test_performance)


def parse_args():
    """
    解析脚本命令行参数
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=str, help="存放模型的目录")
    parser.add_argument("--port", type=str, help="nginx对外提供服务的端口")
    parser.add_argument(
        "--ip", type=str, default="localhost", help="所部署服务器的ip地址")
    args = parser.parse_args()
    return args


def test_deployment(folder, ipaddr, port):
    """
    测试部署的所有模型
    """
    url_base = "http://{ip}:{port}".format(ip=ipaddr, port=port)
    names = (name for name in next(os.walk(folder))[1])
    for name in names:
        config_file = os.path.join(folder, name, "config.yaml")
        if not os.path.isfile(config_file):
            continue
        src_lang = name.split("_")[-2]
        url = url_base + "/" + name.replace("_", "/")
        test_method_translate(url, src_lang)
        test_method_term_protection(url)
        test_performance(url, src_lang)


def main():
    """
    测试入口函数
    """
    args = parse_args()
    test_deployment(args.folder, args.ip, args.port)


if __name__ == "__main__":
    main()
