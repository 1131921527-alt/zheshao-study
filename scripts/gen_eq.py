#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 5 篇「情商沟通」长文注入 zheshao-study/index.html
- 新增板块：💬 情商沟通（与认知偏差类「心理学」区分）
- 幂等：每个改动带 marker，重跑不重复注入
用法：python scripts/gen_eq.py
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # zheshao-study/
HTML = os.path.join(ROOT, "index.html")

ARTICLES = [
    {
        "slug": "eq-basics",
        "e": "💡",
        "t": "高情商的本质：让别人舒服，也不委屈自己",
        "m": "情商沟通 · 认知 · 高情商",
        "b": "高情商不是讨好，是清晰表达+共情，先接情绪再处理事，既利他又不损己。",
        "html": """<section class="screen" id="art-eq-basics">
  <article class="lesson"><a class="back" href="javascript:void(0)" onclick="goTab('s-know')">← 返回知识中心</a>
<header class="art-head">
  <div class="ah-meta">情商沟通 · 认知 · 高情商</div>
  <h1>高情商的本质：让别人舒服，也不委屈自己</h1>
</header>
<div class="body">

<p class="lead">很多人以为高情商就是「嘴甜、会来事、谁都不得罪」。错。那是讨好，不是情商。真正的高情商，是让关系顺、事情成，还不把自己熬干。</p>

<h2>一、先接情绪，再接事情</h2>
<p>人脑有个习惯：情绪没安顿，道理听不进。你一上来就讲方案，对方还在气头上，等于对牛弹琴。正确顺序是先接住情绪：同事搞砸了，先说一句「这事儿确实挺烦」，再去谈怎么补救。对方感觉「你懂我」，防御一降，事就好办了。</p>

<h2>二、共情 ≠ 认同</h2>
<p>最容易踩的坑，是把「我理解你生气」当成「你对」。共情只是说「我看见你的感受了」，不代表你站他那边。这句话厉害在哪？它不驳斥对方，却也不丢自己的立场。吵架时一句「我理解你急」，往往比十个道理都止战。</p>

<div class="callout"><span class="ct">💡 划重点</span>情绪优先原则：先处理心情，再处理事情。顺序错了，话再对也白搭。</div>

<h2>三、不委屈自己，才是真情商</h2>
<p>长期讨好的人，表面人缘好，内里在透支。你越不敢说「不」，别人越敢往你身上加活；你越憋，关系越失衡。高情商的人敢说「我也有难处」——这不是自私，是把关系拉回平等。能互相麻烦的关系，才长久。</p>

<h2>四、把「但是」换成「是的，而且」</h2>
<p>对话里「但是」像刹车，「是的，而且」像油门。对方说想法，你回「有道理，而且我补充一点……」，对方觉得被接住了，也更愿意听你的。这不是话术，是真心认可对方有合理之处。</p>

<div class="callout blue"><span class="ct">🧊 冷知识</span>心理学研究发现：决定一段关系质量的，往往不是「吵不吵架」，而是「吵完能不能修复」。高情商的人不是不冲突，是冲突后更快递台阶、把关系补回来。</div>

<div class="summary"><span class="st">📌 一句话收尾</span><ul>
<li>高情商=清晰表达+共情，是双赢，不是单方面讨好。</li>
<li>先接情绪再讲道理；共情是「看见感受」不是「同意你」。</li>
<li>敢说「不」、会补台阶，关系才可持续。</li>
</ul></div>

</div>
<div class="afoot">腾讯龙虾的成品 · 泽少学习助手<br>内容每日自动更新 · GitHub Pages 托管</div>
  </article>
</section>""",
    },
    {
        "slug": "eq-nvc",
        "e": "🗣️",
        "t": "非暴力沟通：把「你总是」换成「我感到」",
        "m": "情商沟通 · 沟通 · 非暴力沟通",
        "b": "非暴力沟通四步：观察-感受-需要-请求，把评判换成事实，把指责换成需求。",
        "html": """<section class="screen" id="art-eq-nvc">
  <article class="lesson"><a class="back" href="javascript:void(0)" onclick="goTab('s-know')">← 返回知识中心</a>
<header class="art-head">
  <div class="ah-meta">情商沟通 · 沟通 · 非暴力沟通</div>
  <h1>非暴力沟通：把「你总是」换成「我感到」</h1>
</header>
<div class="body">

<p class="lead">明明想好好说，一开口就吵？多半是你用了「你总是」「你从来不」——这话一出口，对方防御瞬间拉满。非暴力沟通（NVC）给你一套不炸场的说话公式。</p>

<h2>一、观察：说事实，别说评判</h2>
<p>「你迟到」是评判，「你这周迟到三次」是观察。评判让人想反驳，事实让人没法赖。开口前先问自己：我说的是眼睛看到的，还是我脑袋判的？</p>

<h2>二、感受：说情绪，别说指责</h2>
<p>「你气死我了」是指责，把锅甩给对方；「我很焦虑」是感受，把状态亮出来。说感受不是示弱，是给对方一个接住你的把手。人天生会回应「情绪」，不太会回应「罪名」。</p>

<div class="callout"><span class="ct">💡 划重点</span>NVC 四步：观察→感受→需要→请求。前两步降防御，后两步给方向。</div>

<h2>三、需要：挖出情绪底下的渴求</h2>
<p>生气往往不是因为那件事本身，是因为某个需要没被满足：被尊重、有安全感、被看见。说出需要，对方才知道「你到底要啥」，而不是在猜。</p>

<h2>四、请求：具体、可执行，别甩口号</h2>
<p>「你别这样」是口号，「下次能不能提前发个消息」是请求。请求要像点菜：清楚、可操作、给对方选择权。越具体，越容易被答应。</p>

<p>暴力版：「你总是玩手机，根本不关心我！」<br>NVC版：「这周晚饭后你看了三次手机（观察），我有点失落（感受），希望多点相处时间（需要），下次能不能先陪我聊十分钟？（请求）」——同样的意思，后者对方听得进去。</p>

<div class="callout blue"><span class="ct">🧊 冷知识</span>非暴力沟通创始人马歇尔·卢森堡，曾去中东、非洲的敌对社区调解，双方一开始都喊「他先停火」。他用 NVC 把「指责」翻成「需要」，居然让敌对话了下来。话的结构，真能改关系。</div>

<div class="summary"><span class="st">📌 一句话收尾</span><ul>
<li>把评判换成观察、把指责换成感受，防御立刻降一半。</li>
<li>说清需要+具体请求，对方才知道怎么对你。</li>
<li>NVC 不是绕弯子，是把「对抗」翻成「协作」。</li>
</ul></div>

</div>
<div class="afoot">腾讯龙虾的成品 · 泽少学习助手<br>内容每日自动更新 · GitHub Pages 托管</div>
  </article>
</section>""",
    },
    {
        "slug": "eq-upmanage",
        "e": "🧑‍💼",
        "t": "职场向上管理：让老板放心把事交给你",
        "m": "情商沟通 · 职场 · 向上管理",
        "b": "向上管理是管理信息差与预期：主动同步、带方案来、管理承诺、对齐目标。",
        "html": """<section class="screen" id="art-eq-upmanage">
  <article class="lesson"><a class="back" href="javascript:void(0)" onclick="goTab('s-know')">← 返回知识中心</a>
<header class="art-head">
  <div class="ah-meta">情商沟通 · 职场 · 向上管理</div>
  <h1>职场向上管理：让老板放心把事交给你</h1>
</header>
<div class="body">

<p class="lead">「向上管理」听着像拍马屁？其实它是管理两样东西：信息差和预期。老板怕的通常不是你笨，是「这事我完全不知道进展」的失控感。</p>

<h2>一、主动同步，别等他问</h2>
<p>进度不是藏到最后才说。里程碑到了发一句，卡住了早讲一声。信息差越小，老板越踏实，也越不会微观管理。周报、站会、甚至一条微信，都是把信息差抹平。</p>

<h2>二、带着方案来，别只甩问题</h2>
<p>「怎么办」是甩锅，「我遇到 X，建议 A 或 B，你倾向哪个」是协作。老板要的是决策输入，不是情绪垃圾桶。你带方案，他做选择，效率高，还显得你靠谱。</p>

<div class="callout"><span class="ct">💡 划重点</span>向上管理的核心就一句：降低他的失控感，增加他的掌控感。</div>

<h2>三、管理承诺，别为表现硬接</h2>
<p>接了做不到的任务，比不接更伤信任。聪明人只承诺「能交付的」，然后努力「超交付」。承诺保守、交付惊艳，口碑就立住了。反过来，次次放鸽子，再会说话也白搭。</p>

<h2>四、把你的事，挂上他的目标</h2>
<p>老板只在乎跟 KPI 挂钩的东西。汇报时别说「我做了啥」，说「这帮您达成了哪个目标」。你的事和他的目标绑一起，他自然上心、给资源。</p>

<div class="callout blue"><span class="ct">🧊 冷知识</span>谷歌的「亚里士多德计划」研究了180个团队，结论很反直觉：决定团队成败的不是谁聪明，而是「心理安全感」——成员敢说真话、不怕丢脸。向上管理做到位，本质就是跟老板建立起这种信任。</div>

<div class="summary"><span class="st">📌 一句话收尾</span><ul>
<li>向上管理=管信息差+管预期，不是拍马屁。</li>
<li>主动同步进度、带方案来、只承诺能交的。</li>
<li>把你的工作挂上老板的目标，资源自然来。</li>
</ul></div>

</div>
<div class="afoot">腾讯龙虾的成品 · 泽少学习助手<br>内容每日自动更新 · GitHub Pages 托管</div>
  </article>
</section>""",
    },
    {
        "slug": "eq-boundary",
        "e": "🚧",
        "t": "职场边界感：情绪劳动与体面拒绝",
        "m": "情商沟通 · 职场 · 边界感",
        "b": "边界不是冷漠，是保护关系；用『肯定+原因+替代』体面拒绝，减少情绪劳动透支。",
        "html": """<section class="screen" id="art-eq-boundary">
  <article class="lesson"><a class="back" href="javascript:void(0)" onclick="goTab('s-know')">← 返回知识中心</a>
<header class="art-head">
  <div class="ah-meta">情商沟通 · 职场 · 边界感</div>
  <h1>职场边界感：情绪劳动与体面拒绝</h1>
</header>
<div class="body">

<p class="lead">什么都答应的老好人，最后往往什么都做不好，还憋一肚子火。边界感不是冷漠，是让关系能跑长久的护栏。</p>

<h2>一、情绪劳动，是被忽视的消耗</h2>
<p>社会学家霍赫希尔德提出「情绪劳动」：空乘要微笑、客服要耐心、打工人要对老板情绪负责——这些「管理自己表情和情绪」的活，是额外消耗。你以为只是回个消息，其实在烧真实情绪。长期不还账，就倦怠。</p>

<h2>二、拒绝的公式：肯定+原因+替代</h2>
<p>别硬邦邦说「不行」。试试：「这需求挺重要（肯定），但我手上有 X 在赶（原因），能不能先排 Y，或者找 Z 帮忙（替代）？」——既守了边界，又给了对方台阶，关系没伤。</p>

<div class="callout"><span class="ct">💡 划重点</span>边界清晰的人，反而更被尊重。总是秒答应的人，请求常被当成「免费的」。</div>

<h2>三、课题分离：谁的事归谁</h2>
<p>阿德勒说「课题分离」：别人的情绪、别人的任务，是别人的事；你只需对自己的负责。同事焦虑是他的课题，你不必替他扛。分清「我的」和「他的」，内耗少一大半。</p>

<h2>四、下班后，适度断联</h2>
<p>7×24 在线不是敬业，是没边界。该回的回，不该秒回的不秒回。可持续的付出，比一时的「随叫随到」值钱。你先把自己照顾好，才有余力帮别人。</p>

<div class="callout blue"><span class="ct">🧊 冷知识</span>情绪劳动研究最早来自对空乘的观察：航空公司要求「始终微笑」，可真实情绪未必开心。这种「表情与内心不一致」的长期消耗，已被证实和职业倦怠高度相关。所以，累的时候允许不笑，是生理刚需。</div>

<div class="summary"><span class="st">📌 一句话收尾</span><ul>
<li>边界感保护关系，也保护你的情绪电量。</li>
<li>用「肯定+原因+替代」体面拒绝，不伤关系。</li>
<li>课题分离：别人的情绪，别全扛在自己肩上。</li>
</ul></div>

</div>
<div class="afoot">腾讯龙虾的成品 · 泽少学习助手<br>内容每日自动更新 · GitHub Pages 托管</div>
  </article>
</section>""",
    },
    {
        "slug": "eq-icebreak",
        "e": "🤝",
        "t": "闲聊与破冰：把尴尬变成关系的起点",
        "m": "情商沟通 · 沟通 · 破冰",
        "b": "闲聊是低风险试探，从环境切入、多听少说、适度自我暴露，弱关系往往最有用。",
        "html": """<section class="screen" id="art-eq-icebreak">
  <article class="lesson"><a class="back" href="javascript:void(0)" onclick="goTab('s-know')">← 返回知识中心</a>
<header class="art-head">
  <div class="ah-meta">情商沟通 · 沟通 · 破冰</div>
  <h1>闲聊与破冰：把尴尬变成关系的起点</h1>
</header>
<div class="body">

<p class="lead">一见面就冷场？你不是不会聊，是误会了闲聊。闲聊不是废话，是「低风险试探」——先确认「这人安全、好相处」，再往深了走。</p>

<h2>一、从环境切入，别一上来挖隐私</h2>
<p>「这家咖啡不错」「今天这雨真大」比「你结婚没」「一个月挣多少」安全一百倍。环境是中立第三方，谁都能接，不踩雷。破冰的秘诀：找眼前都能看见的东西下手。</p>

<h2>二、多问开放式，少说「我我我」</h2>
<p>人最喜欢聊自己。你多问「后来呢」「你怎么看」，少抢话，对方就觉得「这人真会聊」。其实你没说几句，全是他在讲——可印象分是你的。当好听众，是最便宜的高情商。</p>

<div class="callout"><span class="ct">💡 划重点</span>闲聊的目标不是「展示自己」，是「让对方舒服地打开」。</div>

<h2>三、适度自我暴露，拉近距离</h2>
<p>光问不说是审讯，适当露一点自己的小糗事，对方也会松。心理学叫「互惠式自我暴露」：你先交一点底，人家才敢交底。但别一上来倒苦水，循序渐进。</p>

<h2>四、得体收尾，留好印象就撤</h2>
<p>聊到快没话时，别硬撑。一句「今天聊挺开心，先忙去了」体面撤退，留个好结尾。关系像存钱，第一次见面存一笔正的，后面才好续。</p>

<div class="callout blue"><span class="ct">🧊 冷知识</span>社会学家格兰诺维特有个「弱关系理论」：帮你找到工作、机会的，常常不是铁哥们，而是那些「点头之交」「不太熟的人」。因为他们和你圈子不同，信息更互补。所以别小看闲聊——它可能是你最值钱的关系入口。</div>

<div class="summary"><span class="st">📌 一句话收尾</span><ul>
<li>闲聊是低风险试探，从环境切入最安全。</li>
<li>多听少说、适度自我暴露，对方觉得你「会聊」。</li>
<li>弱关系往往最有用，别小看每一次破冰。</li>
</ul></div>

</div>
<div class="afoot">腾讯龙虾的成品 · 泽少学习助手<br>内容每日自动更新 · GitHub Pages 托管</div>
  </article>
</section>""",
    },
]


def card(a):
    return ' {e:"%s",t:"%s",m:"%s",b:"%s"}' % (a["e"], a["t"], a["m"], a["b"])


def section_block(a):
    raw = a["html"]
    out = []
    for ln in raw.split("\n"):
        out.append(("    " + ln) if ln.strip() else ln)
    return "\n".join(out)


def eq_array_text():
    return "const EQ=[" + ",".join(card(a) for a in ARTICLES) + "];\n"


def main():
    with io.open(HTML, encoding="utf-8") as f:
        html = f.read()

    # 1) 5 篇文章 section，插在抽屉前
    if "<!-- EQ-SECTIONS -->" not in html:
        blocks = "\n".join(section_block(a) for a in ARTICLES)
        marker = "<!-- EQ-SECTIONS -->\n" + blocks + "\n"
        assert "    <!-- 抽屉 -->" in html, "drawer marker not found"
        html = html.replace("    <!-- 抽屉 -->", marker + "    <!-- 抽屉 -->", 1)
        print("[ok] sections injected")
    else:
        print("[skip] sections already present")

    # 2) EQ 数组，插在 const SLUG 前
    if "const EQ=[" not in html:
        html = html.replace("const SLUG={", eq_array_text() + "\nconst SLUG={", 1)
        print("[ok] EQ array injected")
    else:
        print("[skip] EQ array present")

    # 3) SLUG 增加 eq
    if ",eq:[" not in html:
        slugs = ",".join('"%s"' % a["slug"] for a in ARTICLES)
        html = re.sub(r'(poem:\[[^\]]*\])};', r'\1,eq:[' + slugs + r']};', html, count=1)
        print("[ok] SLUG.eq injected")
    else:
        print("[skip] SLUG.eq present")

    # 4) renderK maps 增加 eq:EQ
    if ",eq:EQ" not in html:
        html = html.replace("poem:POEM};", "poem:POEM,eq:EQ};", 1)
        print("[ok] renderK maps eq injected")
    else:
        print("[skip] renderK maps eq present")

    # 5) openArticle 字面量增加 eq:EQ
    if "poem:POEM,eq:EQ})" not in html and "eq:EQ})" not in html:
        html = html.replace("poem:POEM})", "poem:POEM,eq:EQ})", 1)
        print("[ok] openArticle eq injected")
    else:
        print("[skip] openArticle eq present")

    # 6) s-know 增加「情商沟通」折叠块（在 poem 后）
    if 'id="klist-eq"' not in html:
        eq_block = ('        <div class="section-title k-toggle" onclick="toggleK(\'eq\')">💬 情商沟通 <span class="more">展开/收起</span></div>\n'
                    '        <div class="klist hidden" id="klist-eq"></div>\n')
        html = html.replace(
            '        <div class="klist hidden" id="klist-poem"></div>',
            '        <div class="klist hidden" id="klist-poem"></div>\n' + eq_block, 1)
        print("[ok] s-know eq block injected")
    else:
        print("[skip] s-know eq block present")

    # 7) 顶栏 sub 增加 情商
    if "· 情商" not in html:
        html = html.replace("历史 · 地理 · 财经 · 心理 · 诗词",
                            "历史 · 地理 · 财经 · 心理 · 诗词 · 情商", 1)
        print("[ok] topbar sub updated")
    else:
        print("[skip] topbar sub present")

    # 8) 首页 qd 增加 情商
    if "诗词情商" not in html:
        html = html.replace("历史地理财经心理诗词", "历史地理财经心理诗词情商", 1)
        print("[ok] home qd updated")
    else:
        print("[skip] home qd present")

    with io.open(HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print("DONE ->", HTML)


if __name__ == "__main__":
    main()
