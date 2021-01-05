"""
对模型的长句进行分割（根据配置的最长句长限制）
method: sent_splitter
input type: str
output type: List[str]
"""
from config import global_config

# 获取当前模块有用的配置
max_sent_len = global_config.get("max_sent_len", 100)
src_lang = global_config.get("translate_src_lang")

if src_lang == "zh":
    from pyltp import SentenceSplitter

    def sent_splitter(text):
        def sent_len(x):
            # 因为在预处理时会分字，所以在计算句长时把空格去掉。
            return len(x.replace(" ", ""))
        if sent_len(text) > max_sent_len:
            sents = SentenceSplitter.split(text)
            #  long_sents = list(filter(lambda x: sent_len(x) > max_sent_len, sents))
            #  if long_sents:
            #      raise AttributeError(
            #          "Please enter text less than {} chars in chinese.".format(max_sent_len))
        else:
            sents = [text]
        return sents

elif src_lang == "en":
    import nltk

    def sent_splitter(text):
        def sent_len(x): 
            # 这里以词数计算英文句长
            return len(nltk.word_tokenize(x))
        if sent_len(text) > max_sent_len:
            sents = nltk.sent_tokenize(text)
           #   long_sents = list(filter(lambda x: sent_len(x) > max_sent_len, sents))
            #  if long_sents:
            #      raise AttributeError(
           #           "Please enter text less than {} chars in chinese.".format(max_sent_len))
        else:
            sents = [text]
        return sents

else:
    raise AttributeError(
        "Unsupported src_lang for sentence splitter: {}".format(src_lang))


def sent_joiner(sents):
    return " ".join(sents)


__all__ = ["sent_splitter", "sent_joiner"]
