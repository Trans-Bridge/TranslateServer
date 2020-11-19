"""
读取项目配置文件
"""
import yaml

with open("mount/config.yaml", "r") as f:
    global_config = yaml.load(f.read())
