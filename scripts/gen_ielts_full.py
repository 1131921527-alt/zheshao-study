# -*- coding: utf-8 -*-
# 雅思单词完整版 · 扩展生成器（泽少）
# 把 100 个新词写进 ielts-vocab-full.html，并给发音按钮加浏览器 TTS 兜底（新词没预录音频也能读）。
# 词表常驻本脚本：日后加词只改 NEW_WORDS 重跑即可。乱序逻辑(shuffleWords)已内置于页面，每次打开自动乱序。
import io, re

SRC = r"E:\workbuddyFIle\腾讯龙虾的成品\学习资源\雅思词汇\html\ielts-vocab-full.html"
DST = r"E:\workbuddyFIle\腾讯龙虾的成品\zheshao-study\ielts\full.html"

# [word, ipa, pos_cn, 记忆法, 用法提示, 例句(en), 例句(cn)]
NEW_WORDS = [
["acknowledge","/əkˈnɒlɪdʒ/","v. 承认","a+know+ledge：知道(ledge)就‘承认’","常用于 acknowledge that...","She acknowledged that she was wrong.","她承认自己错了。"],
["adequate","/ˈædɪkwət/","adj. 足够的","ad+eat：能吃下就‘够’了","反义词 inadequate","The room has adequate lighting.","房间采光充足。"],
["allocate","/ˈæləkeɪt/","v. 分配","al+locate(放置)：把资源‘放’到各处","allocate funds/time to","We allocated more time to revision.","我们给复习分配了更多时间。"],
["ambiguous","/æmˈbɪɡjuəs/","adj. 模糊的","ambi(两)+iguous：两种意思→含糊","反义 clear/unambiguous","His reply was ambiguous.","他的回答含糊其辞。"],
["anticipate","/ænˈtɪsɪpeɪt/","v. 预期","anti(前)+cip(拿)：提前拿→预料","= expect，更正式","We anticipate a rise in costs.","我们预计成本会上升。"],
["apparent","/əˈpærənt/","adj. 明显的","ap+parent(明显的)：一眼看出","it is apparent that...","It is apparent that he lied.","显然他说了谎。"],
["arbitrary","/ˈɑːbɪtrəri/","adj. 武断的","arbit(判断)+ary：凭自己判断→随意","反义 reasonable","The decision seemed arbitrary.","这个决定显得武断。"],
["articulate","/ɑːˈtɪkjuleɪt/","v. 清晰表达","article(文章)+ate：把想法写成/说出‘条理’","形容词发音变 /ɑːˈtɪkjələt/","She articulated her ideas well.","她把想法表达得很清楚。"],
["assess","/əˈses/","v. 评估","as(加强)+sess(坐)：坐下来细看→评定","assess the impact/risk","We must assess the risk.","我们必须评估风险。"],
["assume","/əˈsjuːm/","v. 假定","as+sume(拿)：先‘拿’一个前提","assume (that)...","I assume he is honest.","我假定他是诚实的。"],
["attribute","/əˈtrɪbjuːt/","v. 归因于","at+tribute(赋予)：把结果‘归’给原因","attribute A to B","He attributed his success to luck.","他把成功归因于运气。"],
["bias","/ˈbaɪəs/","n. 偏见","bias 音似‘偏好’","cognitive bias 认知偏差","The report shows a clear bias.","这份报告有明显的偏见。"],
["coincide","/ˌkəʊɪnˈsaɪd/","v. 同时发生","co(共同)+incide(落下)：一起落下→巧合","coincide with","The holiday coincides with my birthday.","假期正好碰上我生日。"],
["compensate","/ˈkɒmpenseɪt/","v. 补偿","com+pens(钱)+ate：用钱补","compensate for","Nothing can compensate for lost time.","什么也补偿不了逝去的时间。"],
["compile","/kəmˈpaɪl/","v. 编纂","com+pile(堆)：堆到一起→汇编","compile a list/report","They compiled a vocabulary list.","他们编了一份词汇表。"],
["comprehend","/ˌkɒmprɪˈhend/","v. 理解","com+prehend(抓)：全抓住→懂","= understand，较正式","I cannot comprehend this theory.","我无法理解这个理论。"],
["conceive","/kənˈsiːv/","v. 构想","con+ceive(拿)：心里‘拿’出主意","conceive of / an idea","He conceived a new plan.","他构想出一个新计划。"],
["concurrent","/kənˈkʌrənt/","adj. 同时的","con+current(流)：一起流→并发","concurrent events","Two concurrent meetings clashed.","两个同时的会议冲突了。"],
["consolidate","/kənˈsɒlɪdeɪt/","v. 巩固","con+solid(固)+ate：变 solid","consolidate one's power","The company consolidated its lead.","公司巩固了领先地位。"],
["constitute","/ˈkɒnstɪtjuːt/","v. 构成","con+stitute(站)：站在一起组成","constitute a threat/majority","Women constitute half the team.","女性占团队一半。"],
["constrain","/kənˈstreɪn/","v. 限制","con+strain(拉紧)：拉住→约束","constrained by budget","We are constrained by time.","我们受时间限制。"],
["contemplate","/ˈkɒntəmpleɪt/","v. 沉思","con+temple(庙)：庙里冥想","contemplate doing","He contemplated quitting.","他考虑过辞职。"],
["contribute","/kənˈtrɪbjuːt/","v. 贡献","con+tribute(给)：一起给","contribute to","Exercise contributes to health.","运动有助于健康。"],
["crucial","/ˈkruːʃl/","adj. 关键的","cruc(十字)+ial：十字路口→决定性","crucial for/to","Sleep is crucial for memory.","睡眠对记忆至关重要。"],
["cultivate","/ˈkʌltɪveɪt/","v. 培养","cult(耕)+ivate：耕耘→培养","cultivate a habit/Relationship","Cultivate the habit of reading.","培养阅读习惯。"],
["demonstrate","/ˈdemənstreɪt/","v. 证明","de+monstr(展示)+ate：展示出来","demonstrate that...","The study demonstrates the link.","研究证明了其中的关联。"],
["denote","/dɪˈnəʊt/","v. 表示","de+note(记号)：用记号‘指’","denote A as B","A red flag denotes danger.","红旗表示危险。"],
["derive","/dɪˈraɪv/","v. 源自","de+rive(河)：从河里引出","derive from","Many words derive from Latin.","许多词源自拉丁语。"],
["diminish","/dɪˈmɪnɪʃ/","v. 减少","di+min(小)+ish：变小","diminish in value","His influence diminished.","他的影响力下降了。"],
["disperse","/dɪˈspɜːs/","v. 分散","dis+perse(撒)：撒开→驱散","disperse the crowd","Police dispersed the crowd.","警察驱散了人群。"],
["distinct","/dɪˈstɪŋkt/","adj. 明显的","di+stinct(刺)：扎眼→清晰","distinct from","The two ideas are distinct.","这两个想法明显不同。"],
["distribute","/dɪˈstrɪbjuːt/","v. 分发","dis+tribute(给)：分开给","distribute among","They distributed food to victims.","他们向灾民分发食物。"],
["diverse","/daɪˈvɜːs/","adj. 多样的","di+verse(转)：转向各方→多元","culturally diverse","The city is culturally diverse.","这座城市文化多元。"],
["dominate","/ˈdɒmɪneɪt/","v. 主导","domin(统治)+ate","dominate the market","The brand dominates the market.","该品牌主导市场。"],
["eliminate","/ɪˈlɪmɪneɪt/","v. 消除","e(出)+limin(门槛)+ate：踢出门","eliminate errors","We must eliminate errors.","我们必须消除错误。"],
["emphasize","/ˈemfəsaɪz/","v. 强调","em+phase(阶段)+ize：突出","emphasize the need to","He emphasized the need for care.","他强调需要谨慎。"],
["enhance","/ɪnˈhɑːns/","v. 提升","en+hance(高)：变高→增强","enhance performance","Music enhances concentration.","音乐提升专注力。"],
["erosion","/ɪˈrəʊʒn/","n. 侵蚀","e(出)+ros(咬)+ion：咬掉","soil/coast erosion","Erosion damaged the coast.","侵蚀破坏了海岸。"],
["establish","/ɪˈstæblɪʃ/","v. 建立","e+stable(稳)+ish：立稳","establish a system","They established a new rule.","他们确立了新规则。"],
["evaluate","/ɪˈvæljueɪt/","v. 评价","e+value(价值)+ate：估价值","evaluate the effect","We evaluated the results.","我们评估了结果。"],
["evident","/ˈevɪdənt/","adj. 明显的","e+vid(看)+ent：看得见的","self-evident","The benefit is evident.","好处是显而易见的。"],
["exceed","/ɪkˈsiːd/","v. 超过","ex(出)+ceed(走)：走过头","exceed the limit","Costs exceeded the budget.","成本超出了预算。"],
["exclude","/ɪkˈskluːd/","v. 排除","ex+clude(关)：关在外面","exclude from","Children are excluded.","儿童被排除在外。"],
["explicit","/ɪkˈsplɪsɪt/","adj. 明确的","ex+plic(折)+it：摊开说→清楚","explicit instruction","He gave explicit instructions.","他给了明确的指示。"],
["extract","/ɪkˈstrækt/","v. 提取","ex+tract(拉)：拉出来","extract data/information","We extracted the key points.","我们提取了要点。"],
["facilitate","/fəˈsɪlɪteɪt/","v. 促进","facil(易)+ate：让事变易","facilitate communication","The app facilitates learning.","这款应用促进学习。"],
["feasible","/ˈfiːzəbl/","adj. 可行的","feas(做)+ible：能做的","it is feasible to","The plan is feasible.","这个计划可行。"],
["formulate","/ˈfɔːmjuleɪt/","v. 制定","form(形)+ulate：定形→阐述","formulate a policy","They formulated a strategy.","他们制定了战略。"],
["fundamental","/ˌfʌndəˈmentl/","adj. 基本的","fund(基)+mental：地基的","fundamental difference","Trust is fundamental.","信任是根本。"],
["generate","/ˈdʒenəreɪt/","v. 产生","gener(生)+ate：生出","generate income/ideas","Solar panels generate power.","太阳能板发电。"],
["genuine","/ˈdʒenjuɪn/","adj. 真正的","genu(生)+ine：原生→真","genuine interest","She showed genuine concern.","她表现出真正的关心。"],
["hierarchy","/ˈhaɪərɑːki/","n. 等级","hier(圣)+archy(统治)：等级制","social hierarchy","There is a clear hierarchy.","有明显的等级结构。"],
["hypothesis","/haɪˈpɒθəsɪs/","n. 假设","hypo(下)+thesis(论点)：待证论点","test a hypothesis","The hypothesis was proved.","该假设被证实了。"],
["identify","/aɪˈdentɪfaɪ/","v. 识别","ident(相同)+ify：认出","identify the cause","We identified the problem.","我们找出了问题。"],
["illustrate","/ˈɪləstreɪt/","v. 说明","il+lustr(光)+ate：照亮→阐明","illustrate with an example","Let me illustrate with a case.","我用一个案例说明。"],
["imply","/ɪmˈplaɪ/","v. 暗示","im(入)+ply(折)：折进去→暗含","易混 imply(暗示) vs infer(推断)","Her tone implied doubt.","她的语气暗示了怀疑。"],
["incentive","/ɪnˈsentɪv/","n. 激励","in+cent(唱)+ive：让人行动的刺激","financial incentive","Tax cuts are an incentive.","减税是一种激励。"],
["incorporate","/ɪnˈkɔːpəreɪt/","v. 纳入","in+corpor(体)+ate：并入一体","incorporate into","We incorporated feedback.","我们采纳了反馈。"],
["indicate","/ˈɪndɪkeɪt/","v. 表明","in+dic(说)+ate：指出","indicate that...","Data indicates a trend.","数据表明了一种趋势。"],
["inherent","/ɪnˈhɪərənt/","adj. 固有的","in+her(黏)+ent：黏在里→天生","inherent risk","Every plan has inherent risk.","每个计划都有固有风险。"],
["innovate","/ˈɪnəveɪt/","v. 创新","in+nov(新)+ate：弄新","innovate in","Firms must innovate to survive.","企业必须创新才能生存。"],
["integral","/ˈɪntɪɡrəl/","adj. 不可或缺的","integr(整)+al：整体一部分","integral part of","Trust is integral to team.","信任是团队不可或缺的部分。"],
["interpret","/ɪnˈtɜːprɪt/","v. 解读","inter(间)+pret(说)：在中间说→阐释","interpret the data","How do you interpret this?","你如何解读这个？"],
["intervene","/ˌɪntəˈviːn/","v. 干预","inter(间)+vene(来)：来到中间","intervene in","The UN intervened.","联合国进行了干预。"],
["invoke","/ɪnˈvəʊk/","v. 援引","in+vok(呼)+e：呼求","invoke a law/rule","They invoked an old law.","他们援引了一条旧法。"],
["isolation","/ˌaɪsəˈleɪʃn/","n. 孤立","isol(岛)+ation：像岛一样","in isolation","He lived in isolation.","他离群索居。"],
["legitimate","/lɪˈdʒɪtɪmət/","adj. 合法的","leg(法)+itimate：合法律的","a legitimate concern","That is a legitimate worry.","那是个合理的担忧。"],
["maintain","/meɪnˈteɪn/","v. 维持","main(手)+tain(握)：握牢","maintain order/contact","We must maintain contact.","我们必须保持联系。"],
["manipulate","/məˈnɪpjuleɪt/","v. 操纵","mani(手)+pulate：用手摆布","manipulate data","He manipulated the figures.","他篡改了数据。"],
["mediate","/ˈmiːdieɪt/","v. 调解","medi(中)+ate：在中间","mediate between","They mediated the dispute.","他们调解了争端。"],
["minimize","/ˈmɪnɪmaɪz/","v. 最小化","mini(小)+ize：弄到最小","minimize risk","We minimized the risk.","我们把风险降到最低。"],
["mutual","/ˈmjuːtʃuəl/","adj. 相互的","mutu(交换)+al：互换的","mutual benefit","We have mutual respect.","我们相互尊重。"],
["neglect","/nɪˈɡlekt/","v. 忽视","neg(不)+lect(选)：不选→忽略","neglect one's duty","He neglected his health.","他忽视了健康。"],
["notion","/ˈnəʊʃn/","n. 概念","not(知)+ion：知道的东西→观念","the notion that...","The notion is outdated.","这个观念过时了。"],
["objective","/əbˈdʒektɪv/","adj. 客观的","object(对象)+ive：看对象→客观","stay objective","Journalists should be objective.","记者应当客观。"],
["obtain","/əbˈteɪn/","v. 获得","ob+tain(拿)：拿到","obtain a degree","She obtained a degree.","她获得了学位。"],
["obvious","/ˈɒbviəs/","adj. 明显的","ob+vi(路)+ous：挡路的→显然","it is obvious that","The answer is obvious.","答案很明显。"],
["occupy","/ˈɒkjupaɪ/","v. 占据","oc+cupy(抓)：抓住→占领","occupy one's mind","The task occupied him.","这项任务占满了他的心思。"],
["perceive","/pəˈsiːv/","v. 感知","per(全)+ceive(拿)：全抓住→察觉","perceive as","She is perceived as strict.","她被认为很严厉。"],
["precise","/prɪˈsaɪs/","adj. 精确的","pre(前)+cise(切)：切得准","to be precise","Give a precise figure.","给个精确的数字。"],
["presume","/prɪˈzjuːm/","v. 推测","pre(前)+sume(拿)：先拿结论","presume that...","I presume you agree.","我推测你同意。"],
["prevalent","/ˈprevələnt/","adj. 普遍的","pre+val(强)+ent：占上风→流行","prevalent among","This view is prevalent.","这种观点很普遍。"],
["promote","/prəˈməʊt/","v. 促进","pro(前)+mote(动)：向前推","promote growth","The policy promotes growth.","政策促进增长。"],
["propose","/prəˈpəʊz/","v. 提议","pro(前)+pose(放)：摆出方案","propose a plan","He proposed a solution.","他提出了一个方案。"],
["prospective","/prəˈspektɪv/","adj. 预期的","pro+spect(看)+ive：向前看的","prospective student","A prospective buyer came.","一位潜在买家来了。"],
["radical","/ˈrædɪkl/","adj. 激进的","radic(根)+al：连根拔→彻底","radical change","The reform is radical.","改革很彻底。"],
["random","/ˈrændəm/","adj. 随机的","random 音似‘乱动’","at random","Pick a card at random.","随机抽一张牌。"],
["rational","/ˈræʃnəl/","adj. 理性的","ratio(比)+nal：讲比例的→合理","a rational choice","Make a rational decision.","做个理性的决定。"],
["react","/riˈækt/","v. 反应","re(回)+act(动)：回动→反应","react to","How did he react?","他有何反应？"],
["recover","/rɪˈkʌvə/","v. 恢复","re(再)+cover(盖)：重新盖好→复原","recover from","He recovered quickly.","他恢复得很快。"],
["reflect","/rɪˈflekt/","v. 反映","re(回)+flect(折)：折回→反映","reflect on","The book reflects society.","这本书反映了社会。"],
["regulate","/ˈreɡjuleɪt/","v. 监管","reg(规)+ulate：用规则管","regulate the market","The state regulates banks.","国家监管银行。"],
["reinforce","/ˌriːɪnˈfɔːs/","v. 加强","re+in+force：再加力","reinforce a habit","Praise reinforces learning.","表扬强化学习。"],
["reluctant","/rɪˈlʌktənt/","adj. 不情愿的","re(反)+luct(挣扎)+ant：挣扎不愿","be reluctant to","He was reluctant to go.","他不情愿去。"],
["reveal","/rɪˈviːl/","v. 揭示","re(再)+veal(面纱)：掀开","reveal the truth","The data revealed a trend.","数据揭示了趋势。"],
["sustain","/səˈsteɪn/","v. 维持","sus(下)+tain(握)：从下托住","sustain growth","The economy sustained growth.","经济保持了增长。"],
["irrespective","/ˌɪrɪˈspektɪv/","adj. 不顾的","ir(不)+respect(看)+ive：不看","irrespective of","Open to all, irrespective of age.","对所有人开放，不论年龄。"],
["simultaneous","/ˌsɪmlˈteɪniəs/","adj. 同时的","simul(同)+taneous：同一时刻","simultaneous translation","同声传译是 simultaneous。","同声传译即同步翻译。"],
["straightforward","/ˌstreɪtˈfɔːwəd/","adj. 简单的","straight+forward：直往前→直白","a straightforward task","The task is straightforward.","任务很简单。"],
["undergo","/ˌʌndəˈɡəʊ/","v. 经历","under+go：在下面走→经受","undergo changes","The city underwent reform.","城市经历了改革。"]
]

MARKER = "<!-- NEW100 injected -->"

def card(w, idx):
    word, ipa, pos, story, tip, en, cn = w
    g = "gradient-%d" % ((idx % 6) + 1)
    return (
'<div class="word-card">\n'
'    <div class="emoji-box %s"><span class="emoji">📚</span></div>\n'
'    <div class="w-head">\n'
'      <div class="w-word">%s</div>\n'
'      <div class="w-ipa">%s</div>\n'
'      <div class="w-pos">%s</div>\n'
'    </div>\n'
'    <div class="word-row">\n'
'      <button class="pron-btn" onclick="playWord(\'%s\',1)">🇬🇧 英音</button>\n'
'      <button class="pron-btn" onclick="playWord(\'%s\',2)">🇺🇸 美音</button>\n'
'    </div>\n'
'    <div class="story-box"><div class="lbl">💡 记忆故事</div>%s</div>\n'
'    <div class="tip-box"><div class="lbl">📝 用法提示</div>%s</div>\n'
'    <div class="sent-section"><div class="sent-title">📝 例句</div><div class="ex-item">\n'
'      <div class="ex-en">%s</div>\n'
'      <div class="ex-cn">%s</div>\n'
'      <button class="ex-tts" data-sent="%s" onclick="playSentence(this.dataset.sent)">🔊 播放</button>\n'
'    </div></div>\n'
'  </div>' % (g, word, ipa, pos, word, word, story, tip, en, cn, en)
    )

def main():
    html = io.open(SRC, encoding="utf-8").read()

    # 1) 注入 100 词（幂等）
    if MARKER not in html:
        cards = "".join(card(w, i) for i, w in enumerate(NEW_WORDS))
        anchor = "</div>\n<div class=\"foot\">"
        assert anchor in html, "wrap-close anchor not found"
        html = html.replace(anchor, cards + "\n</div>\n<div class=\"foot\">" + MARKER + "\n", 1)
        # 更新词数
        html = re.sub(r"共 \d+ 词", "共 %d 词" % (89 + len(NEW_WORDS)), html, count=1)
        # 发音说明更新（新词用浏览器朗读）
        html = html.replace("英式/美式/例句均为真人神经网络发音 · 离线可用",
                            "英式/美式为真人发音 · 新词与例句支持浏览器朗读")
        print("已注入 %d 个新词" % len(NEW_WORDS))
    else:
        print("已注入过，跳过（幂等）")

    # 2) 加 TTS 兜底（幂等）
    if "function tts(" not in html:
        old_pw = ("function playWord(word, type){\n"
                  "  var f = 'audio/' + word.toLowerCase() + (type === 1 ? '_uk.mp3' : '_us.mp3');\n"
                  "  var a = new Audio(f);\n"
                  "  a.play().catch(function(){});\n"
                  "}")
        new_pw = ("function tts(text, lang){\n"
                  "  try{ if(!window.speechSynthesis) return; var u=new SpeechSynthesisUtterance(text); u.lang=lang||'en-US'; u.rate=0.95; window.speechSynthesis.cancel(); window.speechSynthesis.speak(u); }catch(e){}\n"
                  "}\n"
                  "function playWord(word, type){\n"
                  "  var f = 'audio/' + word.toLowerCase() + (type === 1 ? '_uk.mp3' : '_us.mp3');\n"
                  "  var a = new Audio(f);\n"
                  "  a.play().catch(function(){ tts(word, type===1?'en-GB':'en-US'); });\n"
                  "}")
        assert old_pw in html, "playWord block not found"
        html = html.replace(old_pw, new_pw, 1)

        old_ps = ("function playSentence(text){\n"
                  "  var key = text.replace(/<[^>]+>/g,'').trim().toLowerCase().substring(0,50);\n"
                  "  var f = _sentMap[key];\n"
                  "  if(!f) return;\n"
                  "  var a = new Audio(f);\n"
                  "  a.play().catch(function(){});\n"
                  "}")
        new_ps = ("function playSentence(text){\n"
                  "  var key = text.replace(/<[^>]+>/g,'').trim().toLowerCase().substring(0,50);\n"
                  "  var f = _sentMap[key];\n"
                  "  if(f){ var a=new Audio(f); a.play().catch(function(){}); return; }\n"
                  "  tts(text, 'en-US');\n"
                  "}")
        assert old_ps in html, "playSentence block not found"
        html = html.replace(old_ps, new_ps, 1)
        print("已加 TTS 兜底")
    else:
        print("TTS 已存在，跳过")

    io.open(SRC, "w", encoding="utf-8").write(html)
    # 同步到部署目录
    io.open(DST, "w", encoding="utf-8").write(html)
    print("已写回源文件并同步到部署目录 zheshao-study/ielts/full.html")

if __name__ == "__main__":
    main()
