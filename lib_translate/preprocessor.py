"""
翻译预处理器
method: processor
input_type: str
output_type: str
"""
import sys

from config import global_config

# 获取当前模块有用的配置
preprocess_pipeline = global_config.get("preprocess_pipeline", [])


def get_basic_preprocessor():
    """
    使用bert中的脚本对中文进行分字处理
    >>> processor = get_basic_preprocessor()
    >>> text = "你好"
    >>> processor(text)
    '你 好'
    """
    from lib_translate.bert_tokenizer import BasicTokenizer
    tokenizer = BasicTokenizer(do_lower_case=False)
    def preprocessor(line): return " ".join(tokenizer.tokenize(line))
    return preprocessor


def get_mosestokenize_preprocessor(lang=None):
    """
    获取sacremoses分词器
    >>> processor = get_mosestokenize_preprocessor(lang="en")
    >>> processor("This, is a sentence.")
    'This , is a sentence .'
    """
    from sacremoses import MosesTokenizer
    if not lang:
        lang = global_config["translate_src_lang"]
    mt = MosesTokenizer(lang=lang)

    def processor(line):
        return mt.tokenize(line, return_str=True)
    return processor


def get_truecase_preprocessor():
    """
    get sacremoses truecase processor
    Note: 此预处理器必须用在mosestokenize处理器之后
    >>> text = "How are you"
    >>> get_truecase_preprocessor()(text) if "truecase_model" in global_config else "how are you"
    'how are you'
    """
    from sacremoses import MosesTruecaser
    truecase_model = global_config["truecase_model"]
    mtr = MosesTruecaser(truecase_model)

    def preprocessor(line):
        return mtr.truecase(line, return_str=True)
    return preprocessor


def get_normalize_preprocessor():
    """
    get sacaremoses normalize processor
    >>> processor = get_normalize_preprocessor()
    >>> text = "Hi…"
    >>> processor(text)
    'Hi...'
    """
    from sacremoses import MosesPunctNormalizer
    mpn = MosesPunctNormalizer()

    def preprocessor(line):
        return mpn.normalize(line)
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
