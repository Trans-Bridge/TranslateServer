from config import global_config

# 获取当前模块有用的配置
translate_method = global_config["translate_method"]
translate_model = global_config["translate_model"]

# 使用opennmt训练的翻译模型
if translate_method == "opennmt":
    import ctranslate2
    translator = ctranslate2.Translator(translate_model)
    translate = lambda tokens: translator.translate_batch([tokens])[0][0]["tokens"]

else:
    raise AttributeError("Unsupported translation method: {}".format(translate_method))

__all__ = ["translate"]