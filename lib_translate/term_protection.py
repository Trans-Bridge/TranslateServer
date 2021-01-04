"""
对输入文本的专业术语进行保护，目前仅支持一句话中对一个术语进行保护
>>> src_word, tgt_word = "Hello world", "你好世界"
>>> add_words([[src_word, tgt_word]])
>>> src_word.lower() in show_words(return_dict=True)
True
>>> add_words([["I'm", "我是"]])
>>> sent, term = mask_term("hello world! I'm.")
>>> de_mask_term(sent, term)
'你好世界! 我是.'
>>> delete_words(["I'm", "hello world"])
>>> src_word.lower() not in show_words(return_dict=True)
True
>>> mask_term("hello world! I'm.")
("hello world! I'm.", [])
"""
import re
import warnings
import pandas

from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import global_config

PROTECTION_SYMBOL = global_config["term_mask_symbol"]
DICT_FILE = global_config.get("term_protection_dict", None)
SRC_LANG = global_config["translate_src_lang"]
TGT_LANG = global_config["translate_tgt_lang"]
TERM_PROTECTION_DB = global_config["term_protection_db"]

__all__ = ["mask_term", "de_mask_term",
           "add_words", "delete_words", "show_words"]


def _transform_word(word):
    """
    对加入词表的词进行预处理
    """
    return word.strip().lower()


class DFAFilter():
    """
    使用dfa算法构建的term filter
    >>> keywords = ["hello world", "I'm", "hello"]
    >>> dfa_filter = DFAFilter(keywords)
    >>> terms, indexes = dfa_filter.filter("Hello world. I'm fine thank you.")
    >>> terms
    ['Hello world', "I'm"]
    >>> indexes
    [(0, 11), (13, 16)]
    """

    def __init__(self, keywords):
        self.keyword_chains = {}
        self.delimit = '\x00'

        self.keywords = keywords
        for word in keywords:
            if isinstance(word, str):
                self.add(word.strip())

    def remove(self, keyword):
        """
        移除过滤器中的词
        """
        if not keyword:
            return
        chars = _transform_word(keyword)
        level = self.keyword_chains
        prev_level = None
        prev_key = None
        for char in chars:
            if char not in level:
                return
            if self.delimit in level:
                prev_level = level
                prev_key = char
            level = level[char]
        if len(level) > 1:
            level.pop(self.delimit)
        else:
            prev_level.pop(prev_key)

    def add(self, keyword):
        """
        向过滤器中添加词表
        """
        chars = _transform_word(keyword)
        if not chars:
            return
        level = self.keyword_chains
        for i in range(0, len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def filter(self, message):
        """
        从文本中找出词表中的词
        """
        origin_message = message
        message = _transform_word(message)
        sensitive_words = []
        indexes = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            word_start, word_end = -1, -1
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit in level[char]:
                        word_start, word_end = start, start + step_ins
                    level = level[char]
                else:
                    break
            if word_end >= 0:
                sensitive_words.append(origin_message[word_start: word_end])
                indexes.append((word_start, word_end))
                start = word_end - 1
            start += 1

        return sensitive_words, indexes


Base = declarative_base()


class Vocab(Base):

    __tablename__ = "{}-{}".format(SRC_LANG, TGT_LANG)

    src_word = Column(String(64), primary_key=True)
    tgt_word = Column(String(64))


ENGIN = create_engine("sqlite:///{}".format(TERM_PROTECTION_DB))
SESSION = sessionmaker(bind=ENGIN)()
Base.metadata.create_all(ENGIN)


def read_dict_sqlite():
    """
    从sqlite数据库中读取需要保护的词典
    """
    mapping = {}
    for item in SESSION.query(Vocab):
        mapping[_transform_word(item.src_word)] = item.tgt_word
    return mapping


def read_dict_excel(term_file):
    """
    从原文和译文中获取需要保护的词典。
    格式规定：词典的第一行为列名，分别有源语言和目标语言的简称，中文：zh 英文：en
    后面每一行是对应语言需要保护的term
    """
    dataframe = pandas.read_excel(term_file)
    langs = dataframe.columns.tolist()

    mapping = {}
    reverse_mapping = {}
    for _, (src, tgt) in dataframe.iterrows():
        if isinstance(src, str) and isinstance(tgt, str):
            mapping[_transform_word(src)] = tgt
            reverse_mapping[_transform_word(tgt)] = src
    vocab = {
        "{}-{}".format(*langs): mapping,
        "{}-{}".format(*reversed(langs)): reverse_mapping
    }
    return vocab.get("{}-{}".format(SRC_LANG, TGT_LANG))


if DICT_FILE:
    try:
        MAPPING = read_dict_excel(DICT_FILE)
    except FileNotFoundError:
        MAPPING = {}
else:
    MAPPING = {}
if not MAPPING:
    warnings.warn(
        "Can't find mapping {}-{} from dict file for term protecting.".format(SRC_LANG, TGT_LANG))
MAPPING.update(read_dict_sqlite())

TERM_FILTER = DFAFilter(list(MAPPING.keys()))


def mask_term(sent):
    """
    给定一段平行语料，对其中的term进行保护操作
    """
    terms, indexes = TERM_FILTER.filter(sent)
    if PROTECTION_SYMBOL in sent:
        return sent, ""

    string_builder = ""
    prev = 0  # 记录上一个term的位置
    for i, (start, end) in enumerate(indexes):
        string_builder += sent[prev:start]
        string_builder += PROTECTION_SYMBOL + str(i)
        prev = end
    string_builder += sent[prev:]

    return string_builder, terms


RE_DEMULTY = re.compile(
    "([{} ]+)([0-9]+)".format("".join(set(PROTECTION_SYMBOL))))


def de_mask_term(sent, terms):
    """
    对句子进行去保护
    """
    string_builder = ""
    prev = 0  # 记录上一个term的位置
    for obj in RE_DEMULTY.finditer(sent):
        start, end = obj.span()
        string_builder += sent[prev:start]
        prev = end
        prefix, num = obj.groups()
        if not prefix.replace(" ", ""):
            # 如果提取的前缀中只有空格，则跳过
            continue
        num = int(num)
        if num >= len(terms):
            continue
        term = terms[num]
        string_builder += MAPPING[_transform_word(term)]

    string_builder += sent[prev:]

    return string_builder


def add_words(words):
    """添加词典"""
    for src_word, tgt_word in words:
        SESSION.merge(Vocab(src_word=src_word, tgt_word=tgt_word))
        MAPPING[_transform_word(src_word)] = tgt_word
        TERM_FILTER.add(src_word)
    SESSION.commit()


def delete_words(words):
    """
    从词典中删除
    """
    for word in words:
        MAPPING.pop(_transform_word(word), None)
        TERM_FILTER.remove(word)
        SESSION.query(Vocab).filter(Vocab.src_word == word).delete()
    SESSION.commit()


def show_words(return_dict=False):
    """
    返回当前词典中的全部数据
    """
    if return_dict:
        return MAPPING
    else:
        return [[key, value] for key, value in MAPPING.items()]
