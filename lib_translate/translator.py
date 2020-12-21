"""
翻译方法
method: translate
input type: List[List[str]]
output type: List[List[str]]
"""
from itertools import chain
from config import global_config

# 获取当前模块有用的配置
translate_method = global_config["translate_method"]
translate_model = global_config["translate_model"]
translate_model_device = global_config["translate_model_device"]

# 使用opennmt训练的翻译模型
if translate_method == "opennmt":
    import ctranslate2
    if ":" in translate_model_device:
        translate_model_device, device_index = translate_model_device.split(":")
    else:
        device_index = "0"
    translator = ctranslate2.Translator(translate_model,
                                        device=translate_model_device,
                                        device_index=int(device_index))

    def translate(tokens):
        model_output = translator.translate_batch(tokens)
        output_tokens = [item[0]["tokens"] for item in model_output]
        return output_tokens

elif translate_method == "fairseq":
    from fairseq.models.transformer import TransformerModel
    translator = TransformerModel.from_pretrained(
        translate_model,
        checkpoint_file='checkpoint_best.pt',
        data_name_or_path=translate_model,  # 指定存储词表的文件
        beam=3
    )
    translator.to(translate_model_device)
    translator.eval()

    def translate(tokens):
        input_sents = [" ".join(item) for item in tokens]
        model_output = translator.translate(input_sents)
        output_tokens = [[i for i in item.split(" ") if i != "<unk>"] for item in model_output]
        return output_tokens
else:
    raise AttributeError("Unsupported translation method: {}".format(translate_method))

__all__ = ["translate"]
