# -*- coding: utf-8 -*-
"""第14轮 emoji 第三批：具体名词（动物/食物/衣物/乐器/家居/文具）逐个精准配图"""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'study.html')

D = {
    # 动物
    'beak': '\U0001F426', 'mosquito': '\U0001F99F', 'camel': '\U0001F42B', 'panda': '\U0001F43C',
    'horn': '\U0001F4EF', 'wolf': '\U0001F43A', 'dragon': '\U0001F409', 'fox': '\U0001F98A',
    'calf': '\U0001F404', 'pup': '\U0001F436', 'buffalo': '\U0001F403', 'zebra': '\U0001F993',
    'donkey': '\U0001F434', 'falcon': '\U0001F985', 'hawk': '\U0001F985', 'goose': '\U0001F986',
    'squirrel': '\U0001F43F', 'bite': '\U0001F9B7', 'bark': '\U0001F415', 'tame': '\U0001F415',
    # 植物 / 食物
    'alga': '\U0001F33F', 'bud': '\U0001F331', 'hay': '\U0001F33E', 'straw': '\U0001F964',
    'violet': '\U0001F7E3', 'mint': '\U0001F33F', 'pea': '\U0001FADB', 'pear': '\U0001F350',
    'kiwi': '\U0001F95D', 'berry': '\U0001F353', 'papaya': '\U0001F96D', 'flour': '\U0001F33E',
    'porridge': '\U0001F963', 'paste': '\U0001F9F4', 'turkey': '\U0001F983', 'mutton': '\U0001F356',
    'cream': '\U0001F95B', 'jam': '\U0001F36F', 'vanilla': '\U0001F368', 'scallion': '\U0001F9C5',
    'vinegar': '\U0001F376', 'flavour': '\U0001F37D', 'sour': '\U0001F34B', 'thirsty': '\U0001F964',
    'lime': '\U0001F34B', 'acid': '\U0001F34B', 'protein': '\U0001F357', 'vitamin': '\U0001F48A',
    'devour': '\U0001F37D', 'cafeteria': '\U0001F37D', 'buffet': '\U0001F37D', 'barbecue': '\U0001F356',
    'banquet': '\U0001F37D', 'snack': '\U0001F37F', 'gourmet': '\U0001F468', 'porcelain': '\U0001F37D',
    'kettle': '\U0001FAD6', 'pan': '\U0001F373', 'stove': '\U0001F525', 'furnace': '\U0001F525',
    'lid': '\U0001FAD9', 'soda': '\U0001F964', 'brandy': '\U0001F943', 'tobacco': '\U0001F6AC',
    'cigarette': '\U0001F6AC', 'peel': '\U0001F34A', 'hull': '\U0001F6A2',
    # 农事 / 自然
    'spade': '\U000026CF', 'rake': '\U0001F33E', 'plough': '\U0001F69C', 'pluck': '\U00002702',
    'harvest': '\U0001F33E', 'horticulture': '\U0001F33B', 'reproduce': '\U0001F9EC',
    'respire': '\U0001FAC1', 'dense': '\U0001F32B', 'gush': '\U0001F4A6', 'puff': '\U0001F4A8',
    'blow': '\U0001F32C', 'drip': '\U0001F4A7', 'pour': '\U0001FAD7', 'dew': '\U0001F4A7',
    'fountain': '\U000026F2', 'vapour': '\U0001F4A8', 'dusk': '\U0001F306', 'debris': '\U0001F4A5',
    'fringe': '\U0001F487', 'comet': '\U00002604', 'meteorite': '\U00002604', 'ash': '\U0001F32B',
    'enzyme': '\U0001F9EA', 'uptake': '\U0001F96B', 'mature': '\U0001F347',
    # 容器 / 家居
    'barrel': '\U0001F6E2', 'bucket': '\U0001FAA3', 'pail': '\U0001FAA3', 'bell': '\U0001F514',
    'fridge': '\U0001F9CA', 'switch': '\U0001F39B', 'shelf': '\U0001F5C4', 'stool': '\U0001FA91',
    'jar': '\U0001FAD9', 'knob': '\U0001F518', 'bolt': '\U000026A1', 'pump': '\U0001F6B0',
    'plug': '\U0001F50C', 'pipe': '\U0001F6B0', 'mop': '\U0001F9F9', 'broom': '\U0001F9F9',
    'mat': '\U0001F7EB', 'cushion': '\U0001F6CB', 'sheet': '\U0001F6CF', 'pillow': '\U0001F6CF',
    'sponge': '\U0001F9FD', 'nail': '\U0001F529', 'shave': '\U0001FA92', 'cord': '\U0001F50C',
    'strand': '\U0001F9F5', 'wax': '\U0001F56F', 'glue': '\U0001F9F4', 'tag': '\U0001F3F7',
    'envelope': '\U00002709', 'curve': '\U0001F4C8', 'ion': '\U0000269B', 'quantum': '\U0000269B',
    'squash': '\U0001F528', 'utensil': '\U0001F374', 'shampoo': '\U0001F9F4', 'soap': '\U0001F9FC',
    'despair': '\U0001F614', 'novice': '\U0001F331', 'illiteracy': '\U0001F524',
    'indulge': '\U0001F370', 'idiot': '\U0001F92A', 'degree': '\U0001F321', 'dorm': '\U0001F6CF',
    'bibliography': '\U0001F4DA', 'reel': '\U0001F3A1', 'gauge': '\U0001F4CF',
    'microscope': '\U0001F52C', 'lens': '\U0001F50D', 'microphone': '\U0001F3A4',
    'cassette': '\U0001F4FC', 'tape': '\U0001F4FC', 'refine': '\U00002697', 'distil': '\U00002697',
    'tribe': '\U0001F3D5', 'archaeology': '\U0001F3FA', 'engrave': '\U0000270D',
    'soul': '\U0001F54B', 'choir': '\U0001F3B5', 'monk': '\U0001F9D8', 'pagoda': '\U0001F6D5',
    'homesick': '\U0001F3E0', 'empress': '\U0001F451', 'duchess': '\U0001F451', 'earl': '\U0001F3A9',
    'baron': '\U0001F3A9', 'peep': '\U0001F440', 'foresee': '\U0001F52E', 'landmark': '\U0001F5FD',
    'knot': '\U0001FA9F', 'phoneme': '\U0001F524', 'vowel': '\U0001F524', 'logogram': '\U0000270D',
    'suffix': '\U00002795', 'synonym': '\U0001F501', 'antonym': '\U0001F500', 'noun': '\U0001F524',
    'pronoun': '\U0001F524', 'verb': '\U0001F524', 'adverb': '\U0001F524', 'paraphrase': '\U0001F504',
    'jargon': '\U0001F5E3', 'slang': '\U0001F5E3', 'rumour': '\U0001F4E2', 'manuscript': '\U0001F4DC',
    'leaflet': '\U0001F4C4', 'ballet': '\U0001FA70', 'opt': '\U00002611', 'carve': '\U0001F52A',
    'tone': '\U0001F3B5', 'tune': '\U0001F3B5', 'disc': '\U0001F4BF', 'cello': '\U0001F3BB',
    'trumpet': '\U0001F3BA', 'drum': '\U0001F941', 'flute': '\U0001F3B5', 'sprawl': '\U0001F938',
    'badminton': '\U0001F3F8', 'billiards': '\U0001F3B1', 'hockey': '\U0001F3D2', 'bat': '\U0001F987',
    'souvenir': '\U0001F381',
    # 衣物 / 织物
    'jewellery': '\U0001F48D', 'jade': '\U0001F7E2', 'masquerade': '\U0001F3AD', 'veil': '\U0001F470',
    'robe': '\U0001F6F6', 'trousers': '\U0001F456', 'brim': '\U0001F3A9', 'scarf': '\U0001F9E3',
    'handkerchief': '\U0001F9FB', 'purse': '\U0001F45B', 'vest': '\U0001F455', 'collar': '\U0001F454',
    'sleeve': '\U0001F455', 'sock': '\U0001F9E6', 'lace': '\U0001F45E', 'sew': '\U0001FAA1',
    'stitch': '\U0001FAA1', 'needle': '\U0001FAA1', 'thread': '\U0001F9F5', 'strap': '\U0001F392',
    'bracelet': '\U0001F48D', 'velvet': '\U0001F9F6', 'rag': '\U0001F9F9', 'grey': '\U0001F5A4',
    'stain': '\U0001F3A8', 'knit': '\U0001F9F6', 'weave': '\U0001F9F6', 'canvas': '\U0001F3A8',
    'nylon': '\U0001F9E6', 'vogue': '\U00002728', 'shampoo2': '\U0001F9F4',
    # 抽象动词 / 其他
    'overturn': '\U0001F504', 'overseas': '\U00002708', 'overlap': '\U0001F500',
    'overall': '\U0001F4CA', 'outline': '\U0001F4CB', 'invest': '\U0001F4B9', 'accuse': '\U0001FAF5',
    'advice': '\U0001F4A1', 'analog': '\U0001F4E1', 'anecdote': '\U0001F4AC', 'condemn': '\U0001F44E',
    'document': '\U0001F4C4', 'extinguish': '\U0001F9EF', 'lay': '\U0001F6E0', 'subgroup': '\U0001F522',
    'dredge': '\U0001F69C', 'alloy': '\U00002699', 'bronze': '\U0001F949', 'mine': '\U000026CF',
    'paperback': '\U0001F4D5', 'pamphlet': '\U0001F4C4', 'stationery': '\U0001F58B',
}

CN_RULES = [
    (r'彗星|陨石|陨星', '\U00002604'),          # ☄️
    (r'蚊子|蚊', '\U0001F99F'),                  # 🦟
    (r'骆驼|驼', '\U0001F42B'),                  # 🐫
    (r'熊猫|猫熊', '\U0001F43C'),                # 🐼
    (r'狐狸|狐', '\U0001F98A'),                  # 🦊
    (r'斑马', '\U0001F993'),                     # 🦓
    (r'松鼠', '\U0001F43F'),                     # 🐿️
    (r'蚊子|老鹰|猎鹰|隼', '\U0001F985'),        # 🦅
    (r'大提琴|小提琴|提琴', '\U0001F3BB'),       # 🎻
    (r'小号|喇叭|号角', '\U0001F3BA'),           # 🎺
    (r'长笛|笛子', '\U0001F3B5'),                # 🎵
    (r'鼓|大鼓', '\U0001F941'),                  # 🥁
    (r'羽毛球', '\U0001F3F8'),                   # 🏸
    (r'台球|桌球|弹子', '\U0001F3B1'),           # 🎱
    (r'曲棍球|冰球', '\U0001F3D2'),              # 🏒
    (r'芭蕾|芭蕾舞', '\U0001FA70'),              # 🩰
    (r'自助餐|自助', '\U0001F37D'),              # 🍽️
    (r'烧烤|烤肉', '\U0001F356'),                # 🍖
    (r'宴会|盛宴|筵席', '\U0001F37D'),           # 🍽️
    (r'零食|小吃|点心', '\U0001F37F'),           # 🍿
    (r'洗发|香波', '\U0001F9F4'),                # 🧴
    (r'肥皂|香皂', '\U0001F9FC'),                # 🧼
    (r'冰箱|冰柜', '\U0001F9CA'),                # 🧊
    (r'炉子|火炉|厨灶', '\U0001F525'),           # 🔥
    (r'水壶|锅', '\U0001FAD6'),                  # 🫖
    (r'平底锅', '\U0001F373'),                   # 🍳
    (r'桶|水桶|提桶', '\U0001FAA3'),             # 🪣
    (r'罐子|广口瓶|瓶子', '\U0001FAD9'),         # 🫙
    (r'开关|电闸|骤变', '\U0001F39B'),           # 🎚️
    (r'搁板|架子|陆架', '\U0001F5C4'),           # 🗄️
    (r'凳子| stool', '\U0001FA91'),              # 🪑
    (r'拖把|扫帚', '\U0001F9F9'),                # 🧹
    (r'垫子|坐垫|地垫|缓冲垫', '\U0001F6CB'),    # 🛋️
    (r'床单|被单|盖布', '\U0001F6CF'),           # 🛏️
    (r'枕头', '\U0001F6CF'),                     # 🛏️
    (r'海绵', '\U0001F9FD'),                     # 🧽
    (r'钉子|指甲|趾甲', '\U0001F529'),           # 🔩
    (r'剃|刮胡子|刮去', '\U0001FA92'),           # 🪒
    (r'电线|细绳|粗线', '\U0001F50C'),           # 🔌
    (r'蜡|蜂蜡', '\U0001F56F'),                  # 🕯️
    (r'胶水|浆糊|面糊', '\U0001F9F4'),           # 🧴
    (r'标签|标牌|标牌', '\U0001F3F7'),           # 🏷️
    (r'信封|封皮', '\U00002709'),                # ✉️
    (r'曲线|弧线|弯道', '\U0001F4C8'),           # 📈
    (r'离子|量子', '\U0000269B'),                # ⚛️
    (r'压扁|压碎|挤进', '\U0001F528'),           # 🔨
    (r'绝望', '\U0001F614'),                     # 😔
    (r'初学者|新手|见习', '\U0001F331'),         # 🌱
    (r'文盲|无知', '\U0001F524'),                # 🔤
    (r'沉溺|纵容|迁就', '\U0001F370'),           # 🍰
    (r'白痴|笨蛋|低能', '\U0001F92A'),           # 🤪
    (r'度数|度，度数|度数', '\U0001F321'),       # 🌡️
    (r'宿舍', '\U0001F6CF'),                     # 🛏️
    (r'参考书目|文献目录|目录学', '\U0001F4DA'), # 📚
    (r'卷轴|线轴|卷线轮', '\U0001F3A1'),         # 🎣
    (r'测量仪器|厚度|宽度', '\U0001F4CF'),       # 📏
    (r'显微镜', '\U0001F52C'),                   # 🔬
    (r'透镜|镜片|镜头', '\U0001F50D'),           # 🔍
    (r'麦克风|扩音器|话筒', '\U0001F3A4'),       # 🎤
    (r'磁带|盒式|胶片盒', '\U0001F4FC'),         # 📼
    (r'精炼|提纯|蒸馏|提炼', '\U00002697'),      # ⚗️
    (r'部落|宗族', '\U0001F3D5'),                # 🏕️
    (r'考古学|考古', '\U0001F3FA'),              # 🏺
    (r'雕刻|铭刻|雕，刻', '\U0000270D'),         # ✍️
    (r'灵魂|心灵', '\U0001F54B'),                # 🕊️
    (r'唱诗班|合唱团', '\U0001F3B5'),            # 🎵
    (r'僧侣|修道士|和尚', '\U0001F9D8'),         # 🧘
    (r'佛塔|宝塔', '\U0001F6D5'),                # 🛕
    (r'想家|思乡', '\U0001F3E0'),                # 🏠
    (r'皇后|女皇|伯爵|男爵|公爵', '\U0001F451'), # 👑
    (r'窥视|偷看|隐现', '\U0001F440'),           # 👀
    (r'预见|预知|预料', '\U0001F52E'),           # 🔮
    (r'地标|陆标|里程碑', '\U0001F5FD'),         # 🗽
    (r'针脚|缝线|一针', '\U0001FAA1'),           # 🪡
    (r'音位|音素|元音|母音', '\U0001F524'),      # 🔤
    (r'后缀|词尾|尾标', '\U00002795'),           # ➕
    (r'同义词|代名词', '\U0001F501'),            # 🔁
    (r'反义词', '\U0001F500'),                   # 🔀
    (r'名词|代词|动词|副词', '\U0001F524'),      # 🔤
    (r'改述|释义|转述', '\U0001F504'),           # 🔄
    (r'行话|黑话|俚语|切口', '\U0001F5E3'),      # 🗣️
    (r'谣言|传闻|流言', '\U0001F4E2'),           # 📢
    (r'手稿|原稿|手抄本', '\U0001F4DC'),         # 📜
    (r'传单|小册子|活页', '\U0001F4C4'),         # 📄
    (r'平装书|简装书', '\U0001F4D5'),            # 📕
    (r'选择|抉择|作出抉择', '\U00002611'),       # ☑️
    (r'语气|腔调|口吻|基调', '\U0001F3B5'),      # 🎵
    (r'曲调|曲子|乐段|歌曲', '\U0001F3B5'),      # 🎵
    (r'圆盘|唱片|光盘|碟片', '\U0001F4BF'),      # 💿
    (r'蔓延|伸开四肢', '\U0001F938'),            # 🤸
    (r'球棒|球拍|蝙蝠', '\U0001F987'),           # 🦇
    (r'纪念品|纪念物', '\U0001F381'),            # 🎁
    (r'珠宝|首饰|手镯|臂镯', '\U0001F48D'),      # 💍
    (r'翡翠|玉|玉制品', '\U0001F7E2'),           # 🟢
    (r'化装舞会|假面舞会|伪装|掩饰', '\U0001F3AD'),  # 🎭
    (r'面纱|面罩|头巾|围巾|披巾', '\U0001F9E3'),  # 🧣
    (r'袍服|礼袍|睡袍|浴衣|长袍', '\U0001F6F6'),  # 🛶→袍子
    (r'裤子|长裤', '\U0001F456'),                # 👖
    (r'帽檐|帽边|边沿', '\U0001F3A9'),           # 🎩
    (r'手帕', '\U0001F9FB'),                     # 🧻
    (r'钱包|皮夹子|手提包|手袋', '\U0001F45B'),  # 👛
    (r'背心|汗衫|马甲', '\U0001F455'),           # 👕
    (r'衣领|领口|颈圈', '\U0001F454'),           # 👔
    (r'袖子|袖套', '\U0001F455'),                # 👕
    (r'短袜|袜子', '\U0001F9E6'),                # 🧦
    (r'蕾丝|鞋带|系带', '\U0001F45E'),           # 👟
    (r'缝纫|缝补|缝，', '\U0001FAA1'),           # 🪡
    (r'线|细线|线状物|股|缕', '\U0001F9F5'),     # 🧵
    (r'带子|皮带|金属带', '\U0001F392'),         # 🎒
    (r'天鹅绒|丝绒|编织|针织', '\U0001F9F6'),    # 🧶
    (r'抹布|破布|破衣', '\U0001F9F9'),           # 🧹
    (r'灰色|灰白|花白', '\U0001F5A4'),           # 🖤→灰
    (r'玷污|污渍|染色|着色', '\U0001F3A8'),      # 🎨
    (r'帆布|画布|油画', '\U0001F3A8'),           # 🎨
    (r'尼龙|锦纶', '\U0001F9E6'),                # 🧦
    (r'流行|时髦|风尚', '\U00002728'),           # ✨
    (r'合金|青铜', '\U00002699'),                # ⚙️
    (r'疏浚|清淤|挖掘|打捞', '\U0001F69C'),      # 🚜
    (r'熄灭|消灭|破灭', '\U0001F9EF'),           # 🧯
    (r'安放|放置|铺设|铺放', '\U0001F6E0'),      # 🛠️
    (r'子群|小群|小组织', '\U0001F522'),         # 🔢
    (r'摄取|吸收|吸收量', '\U0001F96B'),         # 🥄
    (r'成熟的|成年|发育完全', '\U0001F347'),     # 🍇
    (r' overflow|溢出', '\U0001F4A6'),           # 💧
]


def main():
    h = io.open(HTML, encoding='utf-8').read()
    anchor = "    [/武器|兵器|军械|武装/, '\U0001F52B'],\n"
    assert anchor in h, '锚点丢失'
    lines = ['    /* ===== 第14轮第三批：具体名词逐个精准配图 ===== */']
    for w, em in D.items():
        if w.endswith('2'):
            continue
        lines.append('    [/\\b%s\\b/, \'%s\'],' % (w, em))
    lines.append('    /* ===== 第14轮第三批：中文语义 ===== */')
    for pat, em in CN_RULES:
        lines.append('    [/%s/, \'%s\'],' % (pat, em))
    h = h.replace(anchor, anchor + '\n'.join(lines) + '\n', 1)
    io.open(HTML, 'w', encoding='utf-8').write(h)
    print('第三批插入规则 %d 条' % (len(D) - 1 + len(CN_RULES)))


if __name__ == '__main__':
    main()
