from .base_handler import _BaseHandler
from lib_translate import translate_all_in_one


class TranslateHandler(_BaseHandler):
    def _get_result_dict(self, **kwargs):
        text = kwargs["input"]
        if len(text) > 200 or len(text) < 10:
            raise AttributeError("请输入长度为10-100字符的文本。")
        translation = translate_all_in_one(text)
        return {
            "translation": translation
        }


__all__ = ["TranslateHandler"]
