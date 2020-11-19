from .tokenizer import *
from .translator import *


def translate_all_in_one(text):
    tok = tokenize(text)
    model_output = translate(tok)
    result = detokenize(model_output)
    return result
