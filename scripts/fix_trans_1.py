# -*- coding: utf-8 -*-
"""第14轮：修复被污染的中文译文（第 1 批，120 条）"""
import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"C:\Users\admin\WorkBuddy\2026-08-24-00-30-20\zheshao-study"
P = ROOT + r"\ielts\ielts_bank.json"
bank = json.load(io.open(P, encoding="utf-8"))
idx = {it["word"]: it for it in bank}

# key = "word|例句序号(0起)" ，value = 新中文译文
T = {
 "tertiary|2": "我们在高等教育（乃至大学教育）中也有类似的体系。",
 "diagnose|2": "这些超声检查申请与产科护理无关，而是为了诊断患者的疾病。",
 "concurrent|2": "该法庭与前南斯拉夫各国法院对战争罪拥有并行管辖权。",
 "contaminate|2": "反对者称水力压裂法会污染饮用水源，但业内强烈否认这一结论。",
 "metadata|2": "每一张照片，你都可以添加说明文字、带地理标签的元数据或完整简介来描述当时的情况。",
 "ratify|2": "国会拒绝批准的这项协议，本将取消或大幅削减美国对哥伦比亚大部分出口商品的关税。",
 "access|0": "访问权限有限。",
 "commence|2": "我们随时可以签署一份适当的保密协议，并立即启动尽职调查。",
 "overturn|2": "2010 年 4 月，最高法院支持了 2007 年联邦法院撤销对其赦免的裁决。",
 "overwhelm|1": "这些表现极为抢眼，盖过了 4.75% 前置销售佣金对投资者回报的拖累。",
 "renovate|2": "他们计划翻修彭布罗克街上围绕中央庭院的三栋建筑，名为罗切斯特大厦。",
 "restrict|0": "进入受到限制。",
 "revolve|2": "这些说法都围绕着一个观点：弗朗西斯对教皇之位并无合法权利。",
 "longitude|1": "接到犯罪报案时，现场会被标上经度和纬度。",
 "latitude|2": "这可能把这种冰柱带出理想的纬度带，但也会限制它们的形成。",
 "mishap|1": "为求自保，消费品生产商在包装上贴满了针对各种可能意外的警示。",
 "tornado|2": "“我觉得这是我第一次从龙卷风面前退避，”他补充道。",
 "monsoon|2": "地震、台风和季风雨每年都造成破坏，而且不只是在玉山国家公园。",
 "fume|1": "美国公民自由联盟也许会大为光火，但《权利法案》的起草者们可以安息了。",
 "aggravate|2": "这里许多人认为萨科齐是个专断且制造分裂的人物，会加剧法国的社会裂痕。",
 "erode|1": "第三个影响是削弱加州自诩拥有全美最高技能劳动力的说法。",
 "oceania|2": "美国并没有濒临变成大洋洲，甚至也不是新加坡。",
 "meteorology|2": "罗伯特·麦克莱伦·沃森（邓弗里斯，卡斯尔道格拉斯）——表彰其为邓弗里斯-加洛韦地区气象学所作的贡献。",
 "arid|2": "这是为了防止干旱的州把五大湖当成自己的水库。",
 "frigid|2": "这种严寒状态是该仪器探测器采集最微弱红外源所必需的。",
 "downpour|0": "约克郡水务公司表示，上周古尔发生的洪水是由一场“罕见暴雨”造成的。",
 "desolate|2": "他还是《荒凉天使：杰克·凯鲁亚克、垮掉的一代与美国》一书的作者。",
 "lunar|2": "农历新年是中国文化中最重要的节日，今年在 2 月 10 日。",
 "vapour|2": "氢气能量密度高，且燃烧清洁，只留下水蒸气。",
 "gush|1": "据悉，压裂井的喷出量可达普通直井初始流量的 100 倍。",
 "petroleum|2": "在他研究覆盖的公司中，赫斯和西方石油对油价最为敏感。",
 "eco-friendly|0": "随后客人在环保的 Whichaway 营地舒舒服服住下，该营地完全依靠太阳能和风能供电。",
 "fungus|2": "唯一的幸存者是一种名为白麝香霉的真菌，它通过释放气体杀死了其他真菌。",
 "rainforest|2": "没有什么比站在古老雨林的瀑布下、蝴蝶在身边飞舞更美妙的了。",
 "forestry|2": "州林业官员称，新墨西哥州的另一处大火已蔓延至约 1 平方英里。",
 "counterbalance|2": "反对者则主张，需要政府管理来制衡大公司的权力。",
 "perish|2": "在日本小店铺争夺稀缺货架的无情竞争中，大多数商品几乎在瞬间就被淘汰。",
 "demolish|0": "一场大火之后，消防人员将部分拆除曼彻斯特市中心的一栋废弃建筑。",
 "infringe|1": "有两人或多或少反对这类限制，称其侵犯言论自由。",
 "ecologist|2": "生态学家 ED SCHOFIELD 先生：你知道瓦尔登森林有多少英亩遭到了破坏吗？",
 "botanist|0": "金融风险管理使用的是苏格兰植物学家罗伯特·布朗在 1827 年发现的一个模型。",
 "reptile|2": "她标志性的“蛇形袖口”酷似爬行动物的鳞片，指涉的是美国东南部原住民信仰中的一位神祇。",
 "herbivore|2": "一到河岸，食草动物的队伍就犹豫地停下，因为它们心知尼罗鳄正潜伏等待。",
 "swarm|1": "每次得分后后撤并调整状态，比挥舞着手臂一窝蜂乱冲要容易。",
 "descendant|2": "然而在芬兰森林深处，有一座直接的传承之作：阿尔瓦·阿尔托的玛丽亚别墅。",
 "subgroup|2": "据麦克纳马拉说，企业还可以用单一镜像来管理整个子组。",
 "hybridise|1": "这两个物种虽能共存，但最终会杂交，而拥有浓艳蓝色的本土种就会被取代。",
 "spawn|2": "糟糕的监管始终是黑市及其所滋生犯罪行为的根源。",
 "fin|2": "讽刺的是，鱼翅本身并无味道——它的软骨倒是耐嚼。",
 "bristle|2": "当地的野生物种有山杨食蚜蝇、暗边丽尺蛾和钝叶刺苔。",
 "mosquito|2": "仅仅是掀开蚊帐钻进去，就花光了我所有的力气。",
 "penguin|2": "他的新书《下一个一亿：2050 年的美国》于今年 2 月由企鹅出版社出版。",
 "camel|2": "骆驼奶，至少我尝的这一种，略带一点烟熏味。",
 "cub|1": "就在那个角落里，一只小狮子躲在一只白色高加索牧羊犬身后坐着。",
 "pup|2": "乘皮划艇漂流是观察水獭妈妈带着幼崽的最佳方式之一。",
 "falcon|2": "附近有一家隼类医院，这些猛禽的主人会把它们送来治疗。",
 "sparrow|1": "她端坐在座位上，像麻雀一样胆怯，环顾着同行的乘客。",
 "hibernation|2": "其中两次行程安排在六月，那时熊刚结束冬眠，正忙着大吃特吃。",
 "captive|1": "网络全天候在线，随时都有固定的受众。",
 "propulsion|1": "钓上一条当地的大海鲢或梭鱼，无疑会增添一股出乎意料的强劲推进力。",
 "specimen|1": "你附近的慈善机构很可能正在筹办一场设计师秀，并且需要一个自愿登台的展示者。",
 "ion|2": "赫兹的电动自行车有两个造型时髦的型号，由锂离子电池和近乎静音的电机驱动。",
 "refraction|2": "波浪折射：波浪进入浅水时，其推进方向发生改变的过程。",
 "novice|2": "任何一个经济学新手都知道，债务一旦被减记，就等于违约。",
 "literate|2": "西方世界最后一个识字的人终于读完了《达·芬奇密码》。",
 "impetus|1": "他们初步的成功，不出所料地为建立其他新州的要求注入了新的动力。",
 "headmaster|2": "艾尔斯伯里刑事法院获悉，他曾在法纳姆罗亚尔的卡尔迪科特预备学校任教，后任校长。",
 "matriculation|2": "在过去四年里，几乎每一名成员都通过了毕业会考。",
 "reel|1": "当然，有时砸重金签下一位大牌自由球员是划算的。",
 "polytechnic|1": "从美国回来后，他于 2011 年在香港理工大学获得博士学位。",
 "utilise|2": "卡尔达斯在剑桥研究所工作，他们利用基因组工具研究乳腺癌中的 RNA。",
 "appliance|1": "这项业务现在开始变得像其他任何一种高价家电一样了。",
 "accessory|1": "与其穿圆领 T 恤，不如选一件线条利落的浅色配饰。",
 "browser|2": "Flash Cookie 与浏览器 Cookie 所用的浏览器设置并不相同。",
 "microcomputer|0": "好些年前，最流行的微型计算机编程语言叫做 Basic。",
 "high-definition|1": "宏碁表示，这款上网本配备高清屏幕和杜比音效软件，特别适合观看视频。",
 "pinpoint|2": "监控该警报的人将能利用它精确定位飞机的新位置。",
 "stumble|1": "摄影师与旅行者得靠一点机缘巧合偶然相遇。",
 "ethical|2": "答案在于“道德旅行者”组织评选十佳国家时所采用的方式。",
 "aboriginal|2": "但除了原住民历史，悉尼也在强调其原住居民的当下与未来。",
 "inhabitant|2": "不要错过纪录片《库萨西：从孤儿到国王》，它讲述的是这片营地最著名的居民的故事。",
 "excavate|1": "该州没有发掘剑桥这处遗址的计划，这使得巴茨这样的研究显得重要。",
 "engrave|1": "在汽车音响、手机、光盘换片机、外接扬声器等昂贵配件上刻字。",
 "empress|1": "米尔福德港务局将因“海洋女皇”号事故面临新的法律诉讼。",
 "peep|2": "土耳其新任总参谋长伊希克·科沙内尔几乎没有出过声。",
 "idiom|2": "最早的录音采用布鲁斯风格，明确面向非裔美国人“种族唱片”市场。",
 "prefix|2": "在一场仪式上，伍顿巴西特正式更名，冠以“皇家”前缀。",
 "suffix|1": "环绕太阳以外恒星运行的行星，仅以恒星名称加一个后缀字母来命名。",
 "adjective|2": "他那充满威胁性沉默的简练风格，催生了“品特式”这个形容词。",
 "paraphrase|0": "其一，你必须把每一个词都释义出来，翻译成通俗易懂的英语。",
 "illuminate|2": "根据我的经验，这类概念先行的舞台处理几乎从未真正阐释出作品本身。",
 "brainstorm|2": "诺德比偶尔会和《洋葱报》的作者们碰面，为版面框和宣传文案集思广益。",
 "cipher|1": "这已不是第一次有生命悬系于一份密码的强度之上了。",
 "proverb|2": "他甚至引用了一句中国古谚，讲要为对手架一座“金桥”。",
 "disseminate|2": "只有野生鸟类能携带这种疾病而不发病，从而将其传播到远方。",
 "carve|1": "我们在每块石头上刷一个编号，然后把编号刻在石头上。",
 "improvise|1": "但当突发状况迫使克里斯托弗与员工接触时，这个冒名顶替者不得不临场发挥。",
 "sprawl|0": "努加尔人的传统土地横跨澳大利亚西南部大片区域，涵盖了珀斯不断向外扩张的城区。",
 "utensil|1": "得知那件器具并非他发现的，他似乎一点也不气馁。",
 "razor|1": "他们那间青绿色、谷仓般的品酒室四周环绕着陡峭的山丘和刃状的沙漠植物。",
 "pamphlet|2": "如果他把那部分删掉，他的《圣经》就只会是一本小册子。",
 "memorandum|1": "支持单方申请、请求准许送达“约翰·多伊”传票的备忘录。",
 "stationery|2": "甚至还有一个明细科目，记录销售和市场部门在文具上花了多少钱。",
 "shear|1": "在树林背后，山谷两侧的岩壁陡然直插蓝天。",
 "linen|1": "和其他城市一样，奥兰多也见证了 Linen-N-Things 和电路城等大型全国连锁店的倒闭。",
 "jewel|2": "这座有十个房间的博物馆里，藏有镶宝石的金柄手枪和设有暗格的汽车。",
 "embroider|2": "这种认知差异使他们能够制作并润饰对那个世界的外在呈现，换言之，就是创造艺术。",
 "hairdressing|2": "一些美发沙龙和女装店因为雇用了男性而受到威胁。",
 "pigment|2": "导致蓝眼睛的基因突变会降低 OCA2 基因的表达，从而减少色素浓度。",
 "clothe|1": "我们相信，我们的产品能改善农业，从而帮助养活全世界并供给穿衣所需。",
 "clasp|1": "我们得订购一整块新主板，哪怕只是为了上面连着的那个卡扣。",
 "brim|1": "一有空，她就去附近的弗格森湖钓鲶鱼和蓝鳃太阳鱼。",
}

# 原句把目标词用在人名/品牌名里，一并重写英文 + 中文
R = {
 "bough|1": ("A gentle wind set every bough of the old oak creaking.",
             "一阵微风把老橡树的每根粗枝吹得吱呀作响。"),
 "thorn|2": ("She pulled the thorn out of her finger with a pair of tweezers.",
             "她用镊子把扎进手指的刺拔了出来。"),
 "catalyst|1": ("The new highway acted as a catalyst for economic growth in the region.",
                "这条新公路成为该地区经济增长的催化剂。"),
 "notorious|2": ("The district is notorious for its high rate of violent crime.",
                "该地区因暴力犯罪率高而臭名昭著。"),
 "fresher|2": ("The hall organised a welcome party for all the freshers arriving this September.",
               "学院为今年九月入学的所有大一新生组织了一场迎新派对。"),
 "preposition|2": ("In English, a preposition usually comes before a noun or pronoun.",
                   "在英语中，介词通常位于名词或代词之前。"),
 "dredge|1": ("They plan to dredge the harbour so that larger ships can enter.",
              "他们计划疏浚港口，以便更大的船只能够进入。"),
 "slipper|1": ("She slipped her feet into a pair of warm slippers before going downstairs.",
               "她把脚套进一双保暖拖鞋，然后才下楼。"),
 "radish|2": ("She sliced a few radishes and added them to the salad.",
              "她把几根小萝卜切成片，加进了沙拉里。"),
 "weld|1": ("It takes real skill to weld two pieces of steel together cleanly.",
            "把两块钢干净利落地焊接在一起是需要真功夫的。"),
 "signpost|2": ("Follow the signposts to the nearest village; the road bends sharply ahead.",
                "沿着路标走就能到最近的村庄，前面道路急转弯。"),
 "pistol|2": ("The police found a loaded pistol hidden under the driver's seat.",
              "警方在驾驶座下发现了一把上了膛的手枪。"),
 "whirl|1": ("The leaves began to whirl in the wind as the storm approached.",
             "暴风雨逼近时，树叶开始在风中打转。"),
 "recollect|2": ("I cannot recollect the exact date, but it was sometime in early spring.",
                 "我记不起确切日期了，但应该是早春的某个时候。"),
}

n1 = n2 = 0
for k, cn in T.items():
    w, i = k.rsplit("|", 1)
    i = int(i)
    it = idx.get(w)
    if not it:
        print("!! 找不到词:", w); continue
    exs = it.get("examples") or []
    if len(exs) > i:
        exs[i]["cn"] = cn
        n1 += 1
    else:
        print("!! 例句序号越界:", k)

for k, (en, cn) in R.items():
    w, i = k.rsplit("|", 1)
    i = int(i)
    it = idx.get(w)
    if not it:
        print("!! 找不到词:", w); continue
    exs = it.get("examples") or []
    if len(exs) > i:
        exs[i]["en"] = en
        exs[i]["cn"] = cn
        n2 += 1
    else:
        print("!! 例句序号越界:", k)

print("补译 %d 条，重写 %d 条" % (n1, n2))
json.dump(bank, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("✅ 已写回，总词数 %d" % len(bank))
