# -*- coding: utf-8 -*-
"""
gen_ielts_plus100.py — 给雅思词表再加 100 个词（189 -> 289）。
第二批次：用独立 marker <!-- IELTS+100 --> 注入到 .wrap 末尾、</div><div class="foot"> 之前，
不触碰第一批（<!-- NEW100 injected -->），可重跑幂等。新词无预录音频，靠页面内置 TTS 兜底朗读。
"""
import io, re

SRC = r"E:\workbuddyFIle\腾讯龙虾的成品\学习资源\雅思词汇\html\ielts-vocab-full.html"
DST = r"E:\workbuddyFIle\腾讯龙虾的成品\zheshao-study\ielts\full.html"
MARKER = "<!-- IELTS+100 -->"

# [word, ipa, pos_cn, 记忆法, 用法提示, 例句(en), 例句(cn)]
WORDS2 = [
["seminar","/ˈsemɪnɑː(r)/","n. 研讨班","semi(半)+nar→半大不大的课→研讨班","大学里小规模的讨论课","We had a lively seminar on climate policy.","我们上了一节关于气候政策的生动研讨课。"],
["tutorial","/tjuːˈtɔːriəl/","n. 辅导课","tutor(导师)+ial→导师带的小课","一对一或小组辅导","The tutorial helped me understand the essay question.","辅导课帮我理解了论文题目。"],
["enroll","/ɪnˈrəʊl/","v. 注册入学","en(使)+roll(名单)→登上名单→注册","enroll in/at","She enrolled in a language course.","她注册了一门语言课程。"],
["assignment","/əˈsaɪnmənt/","n. 作业任务","assign(分配)+ment→分配下来的事→作业","常指课程作业","The assignment is due next Friday.","作业下周五截止。"],
["thesis","/ˈθiːsɪs/","n. 论文论点","the-sis→论文/论点","也指学位论文","His thesis argues that cities are overheating.","他的论文主张城市正在过热。"],
["campus","/ˈkæmpəs/","n. 校园","camp(营地)+us→我们的营地→校园","on campus","The new library is at the heart of campus.","新图书馆位于校园中心。"],
["graduate","/ˈɡrædʒuət/","n./v. 毕业生/毕业","grade(等级)+uate→达到等级→毕业","graduate from","She graduated with honours.","她以优异成绩毕业。"],
["undergraduate","/ˌʌndəˈɡrædʒuət/","n. 本科生","under(在…下)+graduate→还没毕业的→本科生","区别于 postgraduate","Undergraduate fees vary by country.","本科生学费因国家而异。"],
["bachelor","/ˈbætʃələ(r)/","n. 学士","bachelor→学士学位","bachelor's degree","He earned a bachelor's in economics.","他获得了经济学学士学位。"],
["faculty","/ˈfæklti/","n. 院系教职","fact(做)+ulty→做学问的群体→院系","指全体教员","The faculty supported the reform.","全体教员支持这项改革。"],
["mentor","/ˈmentɔː(r)/","n. 导师","门特→门特别正的老师→导师","经验上的引路人","A good mentor changes your career.","好导师改变你的职业生涯。"],
["dropout","/ˈdrɒpaʊt/","n. 辍学者","drop(掉)+out(出)→掉出去→辍学","school dropout","The dropout rate fell after reform.","改革后辍学率下降了。"],
["numeracy","/ˈnjuːmərəsi/","n. 计算能力","numer(数字)+acy→数字能力→计算力","与 literacy 对应","Basic numeracy is taught early.","基础计算能力很早就开始教。"],
["cohort","/ˈkəʊhɔːt/","n. 同期群体","co(一起)+hort→一起的一拨人→同期群","常用于研究分组","The 1990 cohort was tracked for 20 years.","1990年同期群被追踪了20年。"],
["consensus","/kənˈsensəs/","n. 共识","con(共同)+sens(感觉)→共同感觉→共识","reach a consensus","There is broad consensus on the goal.","在目标上已有广泛共识。"],
["norm","/nɔːm/","n. 规范","norm→标准规范","social norm","Smiling is the norm here.","微笑在这里是常态。"],
["ethnic","/ˈeθnɪk/","adj. 种族的","eth(民族)+nic→民族的","ethnic minority","The city is ethnically diverse.","这座城市种族多元。"],
["migrant","/ˈmaɪɡrənt/","n. 移民","migr(移动)+ant→移动的人→移民","与 immigrant 区分","Migrant workers send money home.","外来务工者往家里寄钱。"],
["refugee","/ˌrefjuˈdʒiː/","n. 难民","refug(避难)+ee→避难的人→难民","因迫害或战争逃离","The camp hosts 10,000 refugees.","难民营容纳了一万名难民。"],
["census","/ˈsensəs/","n. 人口普查","cens(评估)+us→清点人口","每十年一次","The census counts every resident.","人口普查统计每一位居民。"],
["demographic","/ˌdeməˈɡræfɪk/","adj./n. 人口统计的","demo(人民)+graphic(图)→人口图形","demographic change","Demographic ageing is accelerating.","人口老化正在加速。"],
["segregation","/ˌseɡrɪˈɡeɪʃn/","n. 隔离","se(分开)+greg(群)+ation→把群分开","racial segregation","School segregation was ruled illegal.","学校种族隔离被裁定为非法。"],
["inequality","/ˌɪnkwlˈɒləti/","n. 不平等","in(不)+equal(平等)+ity→不平等","income inequality","Inequality widens between regions.","地区间不平等在扩大。"],
["poverty","/ˈpɒvəti/","n. 贫困","破+verty→贫困","live in poverty","Poverty fell by a third in a decade.","十年间贫困率下降了三分之一。"],
["welfare","/ˈwelfeə(r)/","n. 福利","wel(好)+fare(过)→过得好→福利","welfare state","The welfare system needs reform.","福利体系需要改革。"],
["legislature","/ˈledʒɪsleɪtʃə(r)/","n. 立法机构","legis(法律)+lature→立法机关","与 executive/judiciary 并列","The legislature passed the bill.","立法机构通过了法案。"],
["parliament","/ˈpɑːləmənt/","n. 议会","parli(谈论)+ament→讨论国事的场所","member of parliament","Parliament debated the treaty.","议会辩论了该项条约。"],
["constitution","/ˌkɒnstɪˈtjuːʃn/","n. 宪法","con(共同)+stit(建立)+tion→共同建立的根本法","根本大法","The constitution protects free speech.","宪法保护言论自由。"],
["sanction","/ˈsæŋkʃn/","n./v. 制裁","sanct(批准/惩罚)+ion→制裁","经济制裁","The UN imposed sanctions.","联合国实施了制裁。"],
["treaty","/ˈtriːti/","n. 条约","treat(处理)+y→处理关系的文件","sign a treaty","The treaty took effect in 2020.","该条约于2020年生效。"],
["sovereignty","/ˈsɒvrənti/","n. 主权","sover(统治)+eignty→统治权→主权","national sovereignty","The island claims sovereignty.","该岛声称拥有主权。"],
["diplomat","/ˈdɪpləmæt/","n. 外交官","diploma(外交)+t→外交人员","外交","A diplomat negotiated the ceasefire.","一名外交官谈判了停火。"],
["ambassador","/æmˈbæsədə(r)/","n. 大使","ambassador→大使","ambassador to","She was appointed ambassador to France.","她被任命为驻法国大使。"],
["emissions","/iˈmɪʃnz/","n. 排放","e(出)+miss(送)+ions→送出物→排放","carbon emissions","Emissions must fall by 2030.","排放必须在2030年前下降。"],
["deforestation","/diːˌfɒrɪˈsteɪʃn/","n. 毁林","de(去)+forest(森林)+ation→去森林","反义词 reforestation","Deforestation accelerates warming.","毁林加速变暖。"],
["biodiversity","/ˌbaɪəʊdaɪˈvɜːsəti/","n. 生物多样性","bio(生命)+diversity(多样)→生物多样性","保护目标","Biodiversity is declining fast.","生物多样性正在快速下降。"],
["ecosystem","/ˈiːkəʊsɪstəm/","n. 生态系统","eco(生态)+system(系统)→生态系统","fragile ecosystem","The reef is a rich ecosystem.","该礁石是丰富的生态系统。"],
["conservation","/ˌkɒnsəˈveɪʃn/","n. 保护","con(共同)+serv(保持)+ation→共同保持","nature conservation","Conservation protects habitats.","保护守护栖息地。"],
["renewable","/rɪˈnjuːəbl/","adj. 可再生的","re(再)+new(新)+able→可再新","renewable energy","Solar is renewable and clean.","太阳能可再生且清洁。"],
["pollution","/pəˈluːʃn/","n. 污染","poll(弄脏)+ution→污染","air/water pollution","Pollution harms children most.","污染对儿童危害最大。"],
["greenhouse","/ˈɡriːnhaʊs/","n. 温室","green(绿)+house(屋)→温室","greenhouse gas","Greenhouse gases trap heat.","温室气体锁住热量。"],
["fossil","/ˈfɒsl/","n. 化石","fossil→化石燃料","fossil fuels","Fossil fuels dominate energy.","化石燃料主导能源。"],
["carbon","/ˈkɑːbən/","n. 碳","carbon→碳","carbon footprint","We must cut carbon emissions.","我们必须削减碳排放。"],
["recycle","/ˌriːˈsaɪkl/","v. 回收","re(再)+cycle(循环)→再循环","recycle waste","Cities should recycle more.","城市应当增加回收。"],
["habitat","/ˈhæbɪtæt/","n. 栖息地","habit(居住)+at→居住的地方","natural habitat","Logging destroys animal habitat.","伐木破坏了动物栖息地。"],
["extinction","/ɪkˈstɪŋkʃn/","n. 灭绝","ex(出)+stinct(熄灭)+ion→消失","face extinction","The species faces extinction.","该物种面临灭绝。"],
["landfill","/ˈlændfɪl/","n. 垃圾填埋场","land(地)+fill(填)→填地","垃圾处理方式","Landfill space is running out.","填埋场空间正在耗尽。"],
["ozone","/ˈəʊzəʊn/","n. 臭氧","臭氧","ozone layer","The ozone layer is recovering.","臭氧层正在恢复。"],
["drought","/draʊt/","n. 干旱","干+ought→干旱","severe drought","Drought ruined the harvest.","干旱毁掉了收成。"],
["algorithm","/ˈælɡərɪðəm/","n. 算法","algo(运算)+rithm→算法","推荐算法","The algorithm ranks the posts.","算法对帖子排序。"],
["automation","/ˌɔːtəˈmeɪʃn/","n. 自动化","auto(自动)+mation→自动化","与就业的关系","Automation replaces routine jobs.","自动化取代常规工作。"],
["bandwidth","/ˈbændwɪdθ/","n. 带宽","band(带)+width(宽)→带宽","网络速度","Low bandwidth slows the call.","低带宽拖慢通话。"],
["cyber","/ˈsaɪbə(r)/","adj. 网络的","cyber→网络/赛博","cyber attack","Cyber crime is rising fast.","网络犯罪快速上升。"],
["digital","/ˈdɪdʒɪtl/","adj. 数字的","digit(数字)+al→数字的","digital divide","The digital divide excludes many.","数字鸿沟把许多人排除在外。"],
["encrypt","/ɪnˈkrɪpt/","v. 加密","en(使)+crypt(隐藏)→加密","数据安全","Messages are encrypted end-to-end.","消息端到端加密。"],
["interface","/ˈɪntəfeɪs/","n. 界面","inter(之间)+face(面)→之间的面","user interface","The interface is intuitive.","界面很直观。"],
["network","/ˈnetwɜːk/","n. 网络","net(网)+work(工作)→网","social network","The network went down.","网络中断了。"],
["software","/ˈsɒftweə(r)/","n. 软件","soft(软)+ware(件)→软件","与 hardware 相对","The software crashed again.","软件又崩溃了。"],
["hardware","/ˈhɑːdweə(r)/","n. 硬件","hard(硬)+ware(件)→硬件","设备","The hardware needs upgrading.","硬件需要升级。"],
["database","/ˈdeɪtəbeɪs/","n. 数据库","data(数据)+base(库)→数据库","存储","The database was breached.","数据库遭到入侵。"],
["virtual","/ˈvɜːtʃuəl/","adj. 虚拟的","virt(虚)+ual→虚拟的","virtual reality","Classes moved to virtual space.","课程转到虚拟空间。"],
["simulate","/ˈsɪmjuleɪt/","v. 模拟","simil(像)+ate→模拟","仿真","The model simulates the climate.","模型模拟气候。"],
["gadget","/ˈɡædʒɪt/","n. 小装置","gadget→数码小玩意","数码小装置","This gadget tracks sleep.","这个小装置追踪睡眠。"],
["obsolete","/ˈɒbsəliːt/","adj. 过时的","ob(against)+sole(使用)+te→不再使用","反义词 current","The tech is now obsolete.","该技术现已过时。"],
["prototype","/ˈprəʊtətaɪp/","n. 原型","proto(第一)+type(型)→第一型","产品原型","We built a working prototype.","我们造出了可用的原型。"],
["cognition","/kɒɡˈnɪʃn/","n. 认知","cogn(知道)+ition→认知","与 emotion 相对","Sleep boosts cognition.","睡眠提升认知。"],
["perception","/pəˈsepʃn/","n. 感知","per(完全)+cept(拿)+ion→感知","public perception","Perception shapes behaviour.","感知塑造行为。"],
["instinct","/ˈɪnstɪŋkt/","n. 本能","in(内)+stinct(刺)→内在冲动→本能","by instinct","Survival is an instinct.","求生是本能。"],
["motive","/ˈməʊtɪv/","n. 动机","mot(动)+ive→推动的原因","hidden motive","What was his motive?","他的动机是什么？"],
["impulse","/ˈɪmpʌls/","n. 冲动","im(向)+puls(推)→冲动","on impulse","He bought it on impulse.","他一时冲动买了它。"],
["stimulus","/ˈstɪmjələs/","n. 刺激物","stim(刺)+ulus→刺激","复数 stimuli","Tax cuts are an economic stimulus.","减税是经济刺激。"],
["cognitive","/ˈkɒɡnətɪv/","adj. 认知的","cogn(知)+itive→认知的","cognitive skill","Games train cognitive skills.","游戏训练认知技能。"],
["unconscious","/ʌnˈkɒnʃəs/","adj. 无意识的","un(不)+conscious(意识)→无意识","unconscious bias","Much of bias is unconscious.","许多偏见是无意识的。"],
["intuition","/ˌɪntjuˈɪʃn/","n. 直觉","in(内)+tuit(保护)+ion→直觉","trust your intuition","Her intuition was right.","她的直觉是对的。"],
["irrational","/ɪˈræʃənl/","adj. 不理性的","ir(不)+rational(理性)→不理性","irrational fear","Panic is irrational.","恐慌是不理性的。"],
["prejudice","/ˈpredʒudɪs/","n. 偏见","pre(先)+jud(判断)+ice→偏见","与 bias 近义","Prejudice harms trust.","偏见损害信任。"],
["discriminate","/dɪˈskrɪmɪneɪt/","v. 歧视","dis(分开)+crimin(分)+ate→歧视","discriminate against","Law forbids discriminating by age.","法律禁止年龄歧视。"],
["attitude","/ˈætɪtjuːd/","n. 态度","attitude→态度","attitude toward","Attitude affects outcomes.","态度影响结果。"],
["mindset","/ˈmaɪndset/","n. 心态","mind(心)+set(定)→心态","growth mindset","A fixed mindset blocks growth.","固定型心态阻碍成长。"],
["revenue","/ˈrevənjuː/","n. 收入","re(回)+ven(来)+ue→收入","政府或企业收入","Tax revenue rose this year.","今年税收收入上升。"],
["deficit","/ˈdefɪsɪt/","n. 赤字","de(不足)+fic(做)+it→赤字","budget deficit","The deficit widened again.","赤字再次扩大。"],
["tariff","/ˈtærɪf/","n. 关税","tariff→关税","trade tariff","The tariff hit exporters.","关税打击了出口商。"],
["subsidy","/ˈsʌbsədi/","n. 补贴","sub(下)+sid(坐)+y→补贴","government subsidy","Farmers got a subsidy.","农民获得了补贴。"],
["monopoly","/məˈnɒpəli/","n. 垄断","mono(单一)+poly(卖)→垄断","break a monopoly","The firm held a monopoly.","该公司握有垄断。"],
["fiscal","/ˈfɪskl/","adj. 财政的","fisc(国库)+al→财政的","fiscal year","Fiscal policy tightened.","财政政策收紧了。"],
["monetary","/ˈmʌnɪtri/","adj. 货币的","monet(钱)+ary→货币的","monetary policy","The bank eased monetary policy.","央行放松了货币政策。"],
["export","/ˈekspɔːt/","n./v. 出口","ex(出)+port(运)→出口","反义词 import","The country exports oil.","该国出口石油。"],
["import","/ˈɪmpɔːt/","n./v. 进口","im(入)+port(运)→进口","import from","We import most food.","我们进口大部分食品。"],
["invest","/ɪnˈvest/","v. 投资","in(入)+vest(外衣)→投入","invest in","They invested in clean energy.","他们投资了清洁能源。"],
["capital","/ˈkæpɪtl/","n. 资本","capit(头)+al→资本","human capital","Education builds human capital.","教育积累人力资本。"],
["labor","/ˈleɪbə(r)/","n. 劳动","labor→劳动","labor market","Labor costs are rising.","劳动力成本在上升。"],
["consumer","/kənˈsjuːmə(r)/","n. 消费者","con(完全)+sum(取)+er→消费者","consumer demand","Consumer confidence fell.","消费者信心下降。"],
["merchant","/ˈmɜːtʃənt/","n. 商人","merchant→商人","古义或电商","The merchant sold spices.","那个商人卖香料。"],
["bankruptcy","/ˈbæŋkrʌptsi/","n. 破产","bank(银行)+rupt(断)+cy→破产","与 insolvency 近义","The chain faced bankruptcy.","该连锁店面临破产。"],
["entrepreneur","/ˌɒntrəprəˈnɜː(r)/","n. 企业家","entre(在…间)+prend(拿)+eur→企业家","创业者","The entrepreneur launched a startup.","这位企业家创办了初创公司。"],
["empirical","/ɪmˈpɪrɪkl/","adj. 实证的","em(在…中)+pir(经验)+ical→实证","empirical evidence","The claim lacks empirical support.","该主张缺乏实证支持。"],
["variable","/ˈveəriəbl/","n./adj. 变量/可变的","vari(变)+able→可变/变量","研究变量","We controlled for each variable.","我们控制了每个变量。"],
["correlate","/ˈkɒrəleɪt/","v. 相关","cor(共同)+relate(关联)→相关","correlate with","Screen time correlates with sleep loss.","屏幕时间与睡眠不足相关。"],
["analysis","/əˈnæləsɪs/","n. 分析","ana(再)+lys(松)+is→分析","复数 analyses","The analysis revealed a trend.","分析揭示了一个趋势。"],
["synthesis","/ˈsɪnθəsɪs/","n. 综合","syn(一起)+thesis(放)→综合","反义词 analysis","The essay needs synthesis.","这篇文章需要综合。"],
]

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
    if MARKER in html:
        print("[skip] 第二批已注入，跳过（幂等）")
        return
    # 过滤掉已存在的词，避免重复
    exist = set(re.findall(r'<div class="w-word">([^<]+)</div>', html))
    low = {w.lower() for w in exist}
    batch = [w for w in WORDS2 if w[0].lower() not in low]
    print("[info] 候选 %d，去重后注入 %d" % (len(WORDS2), len(batch)))
    cards = "".join(card(w, i) for i, w in enumerate(batch))
    anchor = "</div>\n<div class=\"foot\">"
    assert anchor in html, "foot anchor not found"
    html = html.replace(anchor, cards + "</div>\n<div class=\"foot\">" + MARKER + "\n", 1)
    # 更新词数：以实际 word-card 数量为准
    n = html.count('<div class="word-card">')
    html = re.sub(r"共 \d+ 词", "共 %d 词" % n, html, count=1)
    io.open(SRC, "w", encoding="utf-8").write(html)
    io.open(DST, "w", encoding="utf-8").write(html)
    print("[done] 注入 %d 词，当前共 %d 词；已同步源与部署" % (len(batch), n))

if __name__ == "__main__":
    main()
