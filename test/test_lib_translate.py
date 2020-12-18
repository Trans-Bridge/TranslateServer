from lib_translate import translate_all_in_one
from config import global_config

src_lang = global_config.get("translate_src_lang")

if src_lang == "zh":
    # text = "习近平在贺电中指出，巴勒斯坦问题作为中东根源性问题，关乎地区和平稳定，关乎国际公平正义，关乎人类良知道义。实现巴勒斯坦与以色列比邻而居、和平共处，不仅是巴以人民世代梦想，也是地区各国人民和国际社会的殷切期望。国际社会应该坚持“两国方案”的正确方向，以联合国有关决议、“土地换和平”原则等国际共识为基础，努力推动中东和平进程。当前形势下，应该更多关注新冠肺炎疫情对巴勒斯坦造成的严峻挑战，帮助巴勒斯坦人民抗击疫情。"
    text = "坡度差"
elif src_lang == "en":
    text = "As in Q2 2020, the year-on-year traffic growth rate remained at a more normal level, around 50 percent, compared to the extraordinary peak in 2018 and the first part of 2019. The quarter-on-quarter growth for Q3 2020 was 10 percent. COVID-19 related restrictions, such as lockdowns and constraints on movement, continue to be reflected in people’s communication patterns. However, mobile traffic and mobility are gradually returning to normal levels. In many countries, mobile traffic is, to a certain extent, still geographically shifted from public and office locations to homes and remote work locations. Some countries have seen an increase in mobile broadband data traffic, while others have experienced a decline supported by Wi-Fi offload in homes with good fixed broadband connections. These traffic patterns could change again if new waves of COVID-19 occur."
else:
    raise AttributeError("Unsupported src_lang.")

translation = translate_all_in_one(text)
print(translation)
