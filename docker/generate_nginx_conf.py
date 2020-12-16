"""
自动生成nginx.config
"""
import argparse
import os


NGINX_CONF_TEMPLATE = """
# 工作线程数
worker_processes  1;

#连接数
events {{
    worker_connections  64;
}}

# 配置HTTP
http {{

    # 监听服务器配置
    server {{
        listen       10000;
        server_name  localhost;

{proxy_config}
   }}
}}
"""

PROXY_TEMPLATE = """
        location {api} {{
            proxy_pass http://{name}:80/yyq/translate;
        }}

"""


def parse_args():
    """
    解析参数
    """
    parser = argparse.ArgumentParser("解析生成nginx.conf脚本的参数")
    parser.add_argument("folder", type=str,
                        help="存放模型的目录，目录下面每个符合要求的目录都会启动一个容器。")
    args = parser.parse_args()
    return args


def generate_nginx_conf(folder):
    """
    制定模型存放目录，生成nginx.conf文件，并写入指定文件夹
    """
    names = (name for name in next(os.walk(folder))[1])
    proxy_config_string = ""
    for name in names:
        config_file = os.path.join(folder, name, "config.yaml")
        if not os.path.isfile(config_file):
            continue
        api = "/" + name.replace("_", "/")

        proxy = PROXY_TEMPLATE.format(**{
            "name": name,
            "api": api
        })
        proxy_config_string += proxy

    output_file = os.path.join(folder, "nginx.conf")
    output_string = NGINX_CONF_TEMPLATE.format(**{
        "proxy_config": proxy_config_string
    })

    with open(output_file, "w") as output_f:
        output_f.write(output_string)


def main():
    """入口函数"""
    args = parse_args()
    folder_abs_path = os.path.abspath(args.folder)
    generate_nginx_conf(folder_abs_path)


if __name__ == "__main__":
    main()
