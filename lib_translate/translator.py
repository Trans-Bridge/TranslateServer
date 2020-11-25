from config import global_config

# 获取当前模块有用的配置
translate_method = global_config["translate_method"]
translate_model = global_config["translate_model"]

# 使用opennmt训练的翻译模型
if translate_method == "opennmt":
    import ctranslate2
    translator = ctranslate2.Translator(translate_model)

    def translate(tokens):
        return translator.translate_batch([tokens])[0][0]["tokens"]

elif translate_method == "fairseq":
    from fairseq.models.transformer import TransformerModel
    translator = TransformerModel.from_pretrained(
        translate_model,
        checkpoint_file='checkpoint_best.pt',
        data_name_or_path=translate_model  # 指定存储词表的文件
    )
    # translate = lambda tokens: translator.translate(" ".join(tokens)).split(" ")  # fairseq接受字符串类型输入，输出字符串类型

    def translate(tokens):
        return translator.translate(" ".join(tokens)).split(" ")
else:
    raise AttributeError("Unsupported translation method: {}".format(translate_method))

__all__ = ["translate"]

