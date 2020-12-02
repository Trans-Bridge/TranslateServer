"""
分词方法
method: tokenize
input type: List[str]
output type: List[List[str]]

词合并方法
method: detokenize
input_type: List[List[str]]
output_type: List[str]
"""

from functools import partial
from config import global_config

# 获取当前模块有用的配置
tok_method = global_config["tok_method"]
tok_src_model = global_config["tok_src_model"]
tok_tgt_model = global_config["tok_tgt_model"]


def get_spm_tokenizer():
    import sentencepiece as spm
    src_tokenizer = spm.SentencePieceProcessor(model_file=tok_src_model)
    if tok_tgt_model == tok_src_model:
        tgt_tokenizer = src_tokenizer
    else:  
        tgt_tokenizer = spm.SentencePieceProcessor(model_file=tok_tgt_model)
    
    tokenize = partial(src_tokenizer.encode, out_type=str, alpha=0.1)
    detokenize = tgt_tokenizer.decode
    return tokenize, detokenize


# 基于 SentencePiece 的分词
if tok_method == "spm":
    tokenize, detokenize = get_spm_tokenizer()
else:
    raise AttributeError("Unsupported tok_method: {}".format(tok_method))


__all__ = ["tokenize", "detokenize"]