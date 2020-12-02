# 翻译后处理器
"""
翻译预处理器
method: postprocessor
input_type: str
output_type: str
"""
import sys

from config import global_config

# 获取当前模块有用的配置
postprocess_pipeline = global_config.get("postprocess_pipeline", [])


def get_remove_whitespace_postprocessor():
    """
    去除文本中的所有空格，中文按字分开时可以将字符间空格去掉。
    """
    def postprocessor(line): return line.replace(" ", "")
    return postprocessor


this = sys.modules[__name__]
all_processors = []
for item in postprocess_pipeline:
    try:
        cur = getattr(this, "get_{}_postprocessor".format(item))()
    except AttributeError:
        raise AttributeError(
            "postprocessor {} is not found. Please check your config file.")
    all_processors.append(cur)


def postprocessor(text):
    for func in all_processors:
        text = func(text)

    return text


__all__ = ["postprocessor"]
