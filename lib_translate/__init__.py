from .tokenizer import *
from .translator import *
from .preprocessor import *
from .postprocessor import *


def translate_all_in_one(text):
    text = processor(text)
    tok = tokenize(text)
    model_output = translate(tok)
    result = detokenize(model_output)
    result = postprocessor(result)
    return result
