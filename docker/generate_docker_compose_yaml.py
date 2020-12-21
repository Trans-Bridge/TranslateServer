"""
自动生成docker-compose.yaml
"""
import os
import argparse
import yaml


DOCKER_COMPOSE_TEMPLATE = """
version: '3'
services:
  nginx:
    image: nginx:stable
    container_name: nginx-translate
    ports:
      - "{serve_port}:10000"
    links:
{links}
    networks:
      - "front"
      - "backend"
    volumes:
      - "{folder}/nginx.conf:/etc/nginx/nginx.conf:ro"

{translate_server_py_config}

networks:
  front:
    driver: bridge
  backend:
    driver: bridge
"""

LINKS_NAME_TEMPLATE = "      - {name}\n"

CONTAINER_CONFIG_TEMPLATE = """
  {name}:
    image: translate_server_py:{image_tag}
    runtime: {runtime}
    container_name: translate_server_{name}
    expose:
      - "80"
    networks:
      - "backend"
    volumes:
      - "{folder}/{name}:/root/translate_server_py/mount"

"""


def parse_args():
    """
    解析参数
    """
    parser = argparse.ArgumentParser("解析生成docker-compose.yaml脚本的参数")
    parser.add_argument("folder", type=str,
                        help="存放模型的目录，目录下面每个符合要求的目录都会启动一个容器。")
    parser.add_argument("docker_image_tag", type=str,
                        help="translate_server_py的镜像tag。")
    parser.add_argument("serve_port", type=str, default="10000",
                        help="nginx对外提供服务的接口")
    args = parser.parse_args()
    return args


def generate_docker_compose_yaml(folder,
                                 image_tag,
                                 serve_port):
    """
    制定模型存放目录，生成docker-compose.yaml文件，并写入指定文件夹
    """
    names = (name for name in next(os.walk(folder))[1])
    all_config_strings = ""
    all_links = ""
    for name in names:
        subdir = os.path.join(folder, name)
        config_file = os.path.join(subdir, "config.yaml")
        if not os.path.isfile(config_file):
            continue

        # 读取配置文件中与docker相关的配置
        with open(config_file) as cfg_f:
            config = yaml.load(cfg_f.read())

        docker_image_tag_suffix = config.get("docker_image_tag_suffix", None)
        if docker_image_tag_suffix:
            tag = image_tag + "-"+ docker_image_tag_suffix
        else:
            tag = image_tag

        config_string = CONTAINER_CONFIG_TEMPLATE.format(**{
            "folder": folder,
            "name": name,
            "image_tag": tag,
            "runtime": "runc" if "cuda" not in docker_image_tag_suffix else "nvidia"
        })
        all_config_strings += config_string
        all_links += LINKS_NAME_TEMPLATE.format(**{"name": name})

    output_file = os.path.join(folder, "docker-compose.yaml")
    output_string = DOCKER_COMPOSE_TEMPLATE.format(**{
        "links": all_links,
        "serve_port": serve_port,
        "folder": folder,
        "translate_server_py_config": all_config_strings
    })

    with open(output_file, "w") as output_f:
        output_f.write(output_string)


def main():
    """入口函数"""
    args = parse_args()
    folder_abs_path = os.path.abspath(args.folder)
    generate_docker_compose_yaml(folder_abs_path,
                                 args.docker_image_tag,
                                 args.serve_port)


if __name__ == "__main__":
    main()
