from .tokenizer import *
from .translator import *
from .preprocessor import processor


def translate_all_in_one(text):
    text = processor(text)
    tok = tokenize(text)
    model_output = translate(tok)
    result = detokenize(model_output)
    return result
