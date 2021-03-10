# 翻译后处理器
"""
翻译预处理器
method: postprocessor
input_type: str
output_type: str
"""
import sys
import re

from config import global_config

# 获取当前模块有用的配置
postprocess_pipeline = global_config.get("postprocess_pipeline", [])


def get_remove_whitespace_postprocessor():
    """
    去除文本中的所有空格，中文按字分开时可以将字符间空格去掉。
    >>> processor = get_remove_whitespace_postprocessor()
    >>> text = "本 • 富 兰 克 林 （ Ben Franklin ） 称 德 国 人 愚 蠢 而 剽 悍 。"
    >>> processor(text)
    '本•富兰克林（ Ben Franklin ）称德国人愚蠢而剽悍。'
    """
    re_han = re.compile("([^A-Za-z0-9])(\\s+)([^A-Za-z0-9])")

    def postprocessor(line):
        while re_han.search(line):
            line = re_han.sub("\\g<1>\\g<3>", line)
        return line

    return postprocessor


def get_detruecase_postprocessor():
    """
    get sacremoses detruecase processor
    >>> processor = get_detruecase_postprocessor()
    >>> text = "how are you ."
    >>> processor(text)
    'How are you .'
    """
    from sacremoses import MosesDetruecaser
    mtr = MosesDetruecaser()

    def processor(line):
        return mtr.detruecase(line, return_str=True)

    return processor


def get_mosesdetokenize_postprocessor(lang=None):
    """
    获取sacremoses Detokenizer
    >>> processor = get_mosesdetokenize_postprocessor(lang="en")
    >>> processor("This is a sentence .")
    'This is a sentence.'
    """
    from sacremoses import MosesDetokenizer
    if not lang:
        lang = global_config["translate_tgt_lang"]
    mdt = MosesDetokenizer(lang=lang)

    def processor(line):
        return mdt.detokenize(line.split(), return_str=True)

    return processor


def get_chinesepunc_postprocessor():
    """
    获取中文标点标准化后处理器。保证中文中的常见符号如，。；？（）为中文全角符号

    >>> processor = get_chinesepunc_postprocessor()
    >>> processor("你好啊!(我有1.5块钱给你好吗?)你;我:他")
    '你好啊！（我有1.5块钱给你好吗？）你；我：他'
    """
    punc_mapping = {
        ",": "，",
        ".": "。",
        "?": "？",
        ";": "；",
        "(": "（",
        ")": "）",
        ":": "：",
        "!": "！"
    }
    regx = re.compile('(?<![0-9A-Za-z])[{}](?![0-9A-Za-z])'.format(
        "".join(punc_mapping)))

    def sub_func(match_obj):
        return punc_mapping[match_obj.group(0)]

    def processor(line):
        return regx.sub(sub_func, line)

    return processor


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
