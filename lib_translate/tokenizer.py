from functools import partial
from config import global_config

# 获取当前模块有用的配置
tok_method = global_config["tok_method"]
tok_src_model = global_config["tok_src_model"]
tok_tgt_model = global_config["tok_tgt_model"]

# 基于 SentencePiece 的分词
if tok_method == "spm":
    import sentencepiece as spm
    src_tokenizer = spm.SentencePieceProcessor(model_file=tok_src_model)
    if tok_tgt_model == tok_src_model:
        tgt_tokenizer = src_tokenizer
    else:  
        tgt_tokenizer = spm.SentencePieceProcessor(model_file=tok_tgt_model)
    
    tokenize = partial(src_tokenizer.encode, out_type=str, enable_sampling=True, alpha=0.1)
    detokenize = tgt_tokenizer.decode

else:
    raise AttributeError("Unsupported tok_method: {}".format(tok_method))


__all__ = ["tokenize", "detokenize"]