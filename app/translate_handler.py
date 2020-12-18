from .base_handler import _BaseHandler
from lib_translate import translate_all_in_one, add_words, delete_words, show_words


class TranslateHandler(_BaseHandler):
    def _get_result_dict(self, **kwargs):
        method = kwargs["method"]
        func = getattr(self, "_handle_{}".format(method))
        data = kwargs.get("data", None)
        return func(data)

    def _handle_translate(self, data):
        """处理translate方法的请求"""
        text = data["input"]
        translation = translate_all_in_one(text)
        return {
            "translation": translation
        }

    def _handle_add_words(self, data):
        """处理add_words方法的请求"""
        add_words(data["words"])

    def _handle_delete_words(self, data):
        """处理delete_words方法的请求"""
        delete_words(data["words"])

    def _handle_show_words(self, _):
        """处理show_words方法的请求"""
        return {
            "words": show_words()
        }


__all__ = ["TranslateHandler"]
