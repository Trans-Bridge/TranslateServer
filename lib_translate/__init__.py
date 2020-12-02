from .tokenizer import *
from .translator import *
from .preprocessor import *
from .postprocessor import *
from .sentence_split import *


def translate_all_in_one(text):

    exe_funcs = [
        processor,
        sent_splitter,
        tokenize,
        translate,
        detokenize,
        sent_joiner,
        postprocessor
    ]
    output = text
    for func in exe_funcs:
        output = func(output)

    return output
