from .tokenizer import *
from .translator import *
from .preprocessor import *
from .postprocessor import *
from .sentence_split import *
from .term_protection import *


def translate_all_in_one(text):
    text, term = mask_term(text)

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

    if term:
        output = de_mask_term(output, term)

    return output
