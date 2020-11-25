"""
翻译预处理器
"""
import sys

from config import global_config

# 获取当前模块有用的配置
preprocess_pipeline = global_config.get("preprocess_pipeline", [])


def get_basic_preprocessor():
    from . bert_tokenizer import BasicTokenizer
    tokenizer = BasicTokenizer(do_lower_case=False)
    def preprocessor(line): return " ".join(tokenizer.tokenize(line))
    return preprocessor


this = sys.modules[__name__]
all_processors = []
for item in preprocess_pipeline:
    try:
        cur = getattr(this, "get_{}_preprocessor".format(item))()
    except AttributeError:
        raise AttributeError(
            "Preprocessor {} is not found. Please check your config file.")
    all_processors.append(cur)


def processor(text):
    for func in all_processors:
        text = func(text)

    return text


__all__ = ["processor"]
