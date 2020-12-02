from .base_handler import _BaseHandler
from lib_translate import translate_all_in_one


class TranslateHandler(_BaseHandler):
    def _get_result_dict(self, **kwargs):
        text = kwargs["input"]
        translation = translate_all_in_one(text)
        return {
            "translation": translation
        }


__all__ = ["TranslateHandler"]
