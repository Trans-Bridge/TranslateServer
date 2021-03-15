"""
读取项目配置文件
"""
import yaml

# 有默认值的参数
global_config = dict()
global_config["serve_port"] = 80
global_config["translate_beam_size"] = 3

with open("mount/config.yaml", "r") as f:
    config = yaml.load(f.read())

global_config.update(config)
