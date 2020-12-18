"""
对输入文本的专业术语进行保护，目前仅支持一句话中对一个术语进行保护
>>> src_word, tgt_word = "hello world", "你好世界"
>>> add_words([[src_word, tgt_word]])
>>> src_word in show_words(return_dict=True)
True
>>> sent, term = mask_term("hello world!")
>>> de_mask_term(sent, term)
'你好世界!'
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


class DFAFilter():
    """
    使用dfa算法构建的term filter
    >>> keywords = ["hello world", "I'm", "hello"]
    >>> dfa_filter = DFAFilter(keywords)
    >>> dfa_filter.filter("Hello world. I'm fine thank you.")
    ['Hello world', "I'm"]
    """

    def __init__(self, keywords):
        self.keyword_chains = {}
        self.delimit = '\x00'

        self.keywords = keywords
        for word in keywords:
            if isinstance(word, str):
                self.add(word.strip())

    def add(self, keyword):
        """
        向过滤器中添加词表
        """
        chars = keyword.strip().lower()
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
        message = message.lower()
        sensitive_words = []
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
                start = word_end - 1
            start += 1

        return sensitive_words


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
        mapping[item.src_word] = item.tgt_word
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
        mapping[src] = tgt
        reverse_mapping[tgt] = src
    vocab = {
        "{}-{}".format(*langs): mapping,
        "{}-{}".format(*reversed(langs)): reverse_mapping
    }
    return vocab.get("{}-{}".format(SRC_LANG, TGT_LANG))

if DICT_FILE:
    MAPPING = read_dict_excel(DICT_FILE)
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
    terms = TERM_FILTER.filter(sent)
    if len(terms) != 1 or PROTECTION_SYMBOL in sent:
        return sent, ""

    term = terms[0]
    sent = sent.replace(term, PROTECTION_SYMBOL)

    return sent, term


RE_DEMULTY = re.compile("[{}]+".format("".join(set(PROTECTION_SYMBOL))))


def de_mask_term(sent, term):
    """
    对句子进行去保护
    """
    return RE_DEMULTY.sub(MAPPING[term], sent)


def add_words(words):
    """添加词典"""
    for src_word, tgt_word in words:
        SESSION.merge(Vocab(src_word=src_word, tgt_word=tgt_word))
        MAPPING[src_word] = tgt_word
        TERM_FILTER.add(src_word)
    SESSION.commit()


def delete_words(words):
    """
    从词典中删除
    """
    raise NotImplementedError("Method delete_words are not implemented yet.")


def show_words(return_dict=False):
    """
    返回当前词典中的全部数据
    """
    if return_dict:
        return MAPPING
    else:
        return [[key, value] for key, value in MAPPING.items()]
