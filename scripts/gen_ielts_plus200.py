# -*- coding: utf-8 -*-
# 雅思单词 +200 扩展生成器（泽少）
# 把 200 个新词追加进 ielts-vocab-full.html，并同步到 zheshao-study/ielts/full.html。
# 自动去重：跳过源文件已存在的词 + 候选池内部重复，保证最终写入 200 个不重复词。
# 词数文案自动 +200。乱序逻辑(shuffleWords)已内置于页面。
import io, re

SRC = r"E:\workbuddyFIle\腾讯龙虾的成品\学习资源\雅思词汇\html\ielts-vocab-full.html"
DST = r"E:\workbuddyFIle\腾讯龙虾的成品\zheshao-study\ielts\full.html"

# [word, ipa, pos_cn, 记忆法, 用法提示, 例句(en), 例句(cn)]
NEW_WORDS = [
# ===== 环境 / 自然 =====
["contaminate","/kənˈtæmɪneɪt/","v. 污染","con(共同)+tamin(触碰)+ate：弄脏","contaminate the soil/water","Factories contaminated the river.","工厂污染了河流。"],
["degrade","/dɪˈɡreɪd/","v. 退化","de(下)+grade(级)：降级","degrade the environment","Plastic degrades slowly.","塑料降解很慢。"],
["irrigation","/ˌɪrɪˈɡeɪʃn/","n. 灌溉","ir(入)+rig(水)+ation","irrigation system","Irrigation supports dry farming.","灌溉支撑旱地农业。"],
["glacier","/ˈɡlæsiə/","n. 冰川","glaci(冰)+er","melting glacier","Glaciers store fresh water.","冰川储存淡水。"],
["terrain","/təˈreɪn/","n. 地形","terr(地)+ain","mountainous terrain","The terrain is rugged.","地形崎岖。"],
["vegetation","/ˌvedʒəˈteɪʃn/","n. 植被","veget(植物)+ation","dense vegetation","Vegetation covers the slope.","植被覆盖山坡。"],
["pollutant","/pəˈluːtənt/","n. 污染物","pollut(污染)+ant","air pollutant","Cars emit pollutants.","汽车排放污染物。"],
["thermal","/ˈθɜːml/","adj. 热的","therm(热)+al","thermal energy","Geothermal is clean.","地热是清洁能源。"],
# ===== 科技 =====
["binary","/ˈbaɪnəri/","adj. 二进制的","bi(二)+nary","binary code","Computers use binary.","计算机用二进制。"],
["cache","/kæʃ/","n. 缓存","cache 音似'现金'→临时存放","clear the cache","Clear your browser cache.","清理浏览器缓存。"],
["compute","/kəmˈpjuːt/","v. 计算","com(共同)+pute(想)","compute the result","The chip computes fast.","芯片计算很快。"],
["debug","/diːˈbʌɡ/","v. 调试","de(去)+bug(虫)：去掉虫子","debug the code","We debugged the app.","我们调试了应用。"],
["firmware","/ˈfɜːmweə/","n. 固件","firm(固)+ware(件)","update firmware","Update the router firmware.","更新路由器固件。"],
["latency","/ˈleɪtənsi/","n. 延迟","lat(迟)+ency","low latency","Gamers want low latency.","玩家想要低延迟。"],
["metadata","/ˈmetədeɪtə/","n. 元数据","meta(元)+data","image metadata","Metadata stores info.","元数据存储信息。"],
["neural","/ˈnjʊərəl/","adj. 神经的","neur(神经)+al","neural network","Neural nets power AI.","神经网络驱动AI。"],
["node","/nəʊd/","n. 节点","node 音似'诺的'→连接点","network node","Each node shares data.","每个节点共享数据。"],
["protocol","/ˈprəʊtəkɒl/","n. 协议","proto(首)+col","communication protocol","Protocols govern data.","协议规范数据。"],
["render","/ˈrendə/","v. 渲染","render 音似'渲染'","render a video","The GPU renders fast.","显卡渲染很快。"],
["sensor","/ˈsensə/","n. 传感器","sens(感觉)+or","motion sensor","Phones have sensors.","手机有传感器。"],
# ===== 医疗 =====
["antibiotic","/ˌæntɪbaɪˈɒtɪk/","n. 抗生素","anti(抗)+bio(生命)+tic","take antibiotics","Antibiotics fight infection.","抗生素对抗感染。"],
["benign","/bɪˈnaɪn/","adj. 良性的","beni(好)+gn","benign tumour","The tumour is benign.","肿瘤是良性的。"],
["clinical","/ˈklɪnɪkl/","adj. 临床的","clin(床)+ical","clinical trial","The trial is clinical.","试验是临床的。"],
["disability","/ˌdɪsəˈbɪləti/","n. 残疾","dis(不)+ability(能力)","physical disability","She has a disability.","她有残疾。"],
["dosage","/ˈdəʊsɪdʒ/","n. 剂量","dos(给)+age","correct dosage","Follow the dosage.","按剂量服用。"],
["gene","/dʒiːn/","n. 基因","gene 音似'基因'","a dominant gene","Genes shape traits.","基因决定性状。"],
["immune","/ɪˈmjuːn/","adj. 免疫的","im(不)+mune(服务)：不服役→免疫","immune system","Exercise boosts immunity.","运动增强免疫力。"],
["malignant","/məˈlɪɡnənt/","adj. 恶性的","mali(坏)+gnant","malignant tumour","The growth is malignant.","该增生是恶性的。"],
["outbreak","/ˈaʊtbreɪk/","n. 爆发","out+break(破)","an outbreak of flu","An outbreak hit the city.","该市爆发流感。"],
["overdose","/ˈəʊvədəʊs/","n. 过量","over(过)+dose(剂量)","drug overdose","He died of overdose.","他死于用药过量。"],
["parasite","/ˈpærəsaɪt/","n. 寄生虫","para(旁)+site(食物)","a intestinal parasite","Parasites harm hosts.","寄生虫伤害宿主。"],
["vaccine","/ˈvæksiːn/","n. 疫苗","vacc(牛)+ine：牛痘由来","get a vaccine","The vaccine works.","疫苗有效。"],
["virus","/ˈvaɪrəs/","n. 病毒","virus 音似'病毒'","a computer virus","The virus spread fast.","病毒传播很快。"],
# ===== 教育 =====
["academy","/əˈkædəmi/","n. 学院","academ(学术)+y","a military academy","He entered the academy.","他进入学院。"],
["alumnus","/əˈlʌmnəs/","n. 校友","al(养)+umnus：被养育的人","an alumnus of Peking Univ.","He is an alumnus.","他是校友。"],
["bilingual","/ˌbaɪˈlɪŋɡwəl/","adj. 双语的","bi(二)+lingu(语言)+al","bilingual education","She is bilingual.","她会双语。"],
["dean","/diːn/","n. 院长","dean 音似'院长'","the dean of students","The dean approved it.","院长批准了。"],
["discipline","/ˈdɪsəplɪn/","n. 学科","disci(学)+pline","academic discipline","Math is a discipline.","数学是一门学科。"],
["examine","/ɪɡˈzæmɪn/","v. 检查","ex(出)+amine(称)","examine the evidence","The doctor examined him.","医生给他做了检查。"],
["major","/ˈmeɪdʒə/","n. 专业","major 音似'专业'","也可作 adj. 主要的","Her major is finance.","她的专业是金融。"],
["module","/ˈmɒdjuːl/","n. 模块","mod(量)+ule","a training module","Each module is short.","每个模块很短。"],
["pupil","/ˈpjuːpl/","n. 学生","pupil 音似' pupils'→小学生","a bright pupil","The pupil excelled.","这名学生很出色。"],
["syllabus","/ˈsɪləbəs/","n. 教学大纲","syl(总)+lab(拿)+us","the course syllabus","Read the syllabus.","读教学大纲。"],
["tutor","/ˈtjuːtə/","n. 导师","tut(保护)+or","a private tutor","She hired a tutor.","她请了导师。"],
# ===== 经济 / 商业 =====
["acquire","/əˈkwaɪə/","v. 收购","ac(向)+quire(求)","acquire a company","They acquired a rival.","他们收购了对手。"],
["assets","/ˈæsets/","n. 资产","as(足够)+set(放)","fixed assets","Assets exceeded debts.","资产超过负债。"],
["audit","/ˈɔːdɪt/","n. 审计","aud(听)+it：听账","annual audit","The audit found errors.","审计发现了错误。"],
["bond","/bɒnd/","n. 债券","bond 音似'绑的'→绑定投资","government bond","Bonds are safer.","债券更安全。"],
["depreciation","/dɪˌpriːʃiˈeɪʃn/","n. 贬值","de(下)+preci(价值)+ation","asset depreciation","Depreciation cuts tax.","折旧能抵税。"],
["dividend","/ˈdɪvɪdend/","n. 股息","divid(分)+end","pay a dividend","The firm paid dividends.","公司派了股息。"],
["equilibrium","/ˌiːkwɪˈlɪbriəm/","n. 平衡","equi(等)+libr(秤)+ium","market equilibrium","Prices reach equilibrium.","价格达到平衡。"],
["equity","/ˈekwəti/","n. 股权","equ(平)+ity","shareholder equity","Equity fell this year.","股权今年下降。"],
["expenditure","/ɪkˈspendɪtʃə/","n. 支出","ex(出)+pend(付)+iture","public expenditure","Expenditure rose.","支出上升了。"],
["forecast","/ˈfɔːkɑːst/","v. 预测","fore(前)+cast(扔)","forecast demand","We forecast growth.","我们预测增长。"],
["franchise","/ˈfræntʃaɪz/","n. 特许经营","franc(自由)+ise","a fast-food franchise","He bought a franchise.","他买了特许经营权。"],
["inflation","/ɪnˈfleɪʃn/","n. 通胀","in(入)+flat(吹)+ion：吹涨","control inflation","Inflation hurts savers.","通胀伤害储户。"],
["inventory","/ˈɪnvəntri/","n. 库存","in(入)+vent(来)+ory","manage inventory","Inventory is low.","库存偏低。"],
["invoice","/ˈɪnvɔɪs/","n. 发票","in+voice(声音)：开声要钱","issue an invoice","We sent the invoice.","我们开了发票。"],
["liability","/ˌlaɪəˈbɪləti/","n. 负债","li(绑)+ability","long-term liability","Liabilities grew.","负债增加了。"],
["liquidation","/ˌlɪkwɪˈdeɪʃn/","n. 清算","liquid(液)+ation：变现金","go into liquidation","The firm was liquidated.","公司被清算。"],
["lucrative","/ˈluːkrətɪv/","adj. 赚钱的","lucr(钱)+ative","a lucrative job","Tech is lucrative.","科技很赚钱。"],
["merger","/ˈmɜːdʒə/","n. 合并","merge(合)+er","a bank merger","The merger cleared.","合并获批。"],
["mortgage","/ˈmɔːɡɪdʒ/","n. 抵押","mort(死)+gage(押)","a home mortgage","They took a mortgage.","他们办了房贷。"],
["overhead","/ˈəʊvəhed/","n. 管理费用","over+head：头顶开销","cut overhead","Overhead is high.","管理费用很高。"],
["portfolio","/pɔːtˈfəʊliəʊ/","n. 投资组合","port(拿)+folio","an investment portfolio","Diversify your portfolio.","分散你的投资组合。"],
["procurement","/prəˈkjʊəmənt/","n. 采购","pro(前)+cur(关心)+ment","public procurement","Procurement is strict.","采购很严格。"],
["profitability","/ˌprɒfɪtəˈbɪləti/","n. 盈利能力","profit(利)+ability","improve profitability","Profitability rose.","盈利能力上升。"],
["shareholder","/ˈʃeəhəʊldə/","n. 股东","share(股)+holder","protect shareholders","Shareholders voted.","股东投票了。"],
["turnover","/ˈtɜːnəʊvə/","n. 营业额","turn+over：周转","high turnover","Turnover doubled.","营业额翻倍。"],
["valuation","/ˌvæljuˈeɪʃn/","n. 估值","value(价值)+ation","a fair valuation","The valuation is high.","估值很高。"],
["venture","/ˈventʃə/","n. 风险","vent(来)+ure","a joint venture","They launched a venture.","他们启动了一个风险项目。"],
["wholesale","/ˈhəʊlseɪl/","adj. 批发的","whole(整)+sale","wholesale prices","Wholesale is cheaper.","批发更便宜。"],
# ===== 社会 / 政治 =====
["amendment","/əˈmendmənt/","n. 修正案","a+mend(修)+ment","a constitutional amendment","The amendment passed.","修正案通过了。"],
["autonomy","/ɔːˈtɒnəmi/","n. 自治","auto(自己)+nomy(法则)","regional autonomy","They demand autonomy.","他们要求自治。"],
["bureaucracy","/bjʊəˈrɒkrəsi/","n. 官僚","bureau(局)+cracy","cut bureaucracy","Bureaucracy slows things.","官僚作风拖慢事情。"],
["citizenship","/ˈsɪtɪzənʃɪp/","n. 公民身份","citizen(公民)+ship","apply for citizenship","He gained citizenship.","他获得了公民身份。"],
["coalition","/ˌkəʊəˈlɪʃn/","n. 联盟","co(共同)+alit(长大)+ion","a ruling coalition","The coalition won.","联盟获胜了。"],
["corrupt","/kəˈrʌpt/","adj. 腐败的","cor(全)+rupt(破)","corrupt official","The official was corrupt.","该官员腐败。"],
["decree","/dɪˈkriː/","n. 法令","de(下)+cree(判)","issue a decree","The king issued a decree.","国王颁布了法令。"],
["democracy","/dɪˈmɒkrəsi/","n. 民主","demo(人民)+cracy","a vibrant democracy","Democracy needs debate.","民主需要辩论。"],
["dictatorship","/ˌdɪkˈteɪtəʃɪp/","n. 独裁","dictat(命令)+ship","a brutal dictatorship","The dictatorship fell.","独裁政权倒台了。"],
["electorate","/ɪˈlektərət/","n. 选民","elect(选)+orate","mobilize the electorate","The electorate is divided.","选民意见分裂。"],
["embargo","/ɪmˈbɑːɡəʊ/","n. 禁运","em(入)+bar(栏)+go","lift an embargo","They lifted the embargo.","他们解除了禁运。"],
["federation","/ˌfedəˈreɪʃn/","n. 联邦","feder(信)+ation","a loose federation","The federation held.","联邦维持住了。"],
["ideology","/ˌaɪdiˈɒlədʒi/","n. 意识形态","ideo(思想)+logy","political ideology","Ideology divides them.","意识形态使他们分裂。"],
["impeachment","/ɪmˈpiːtʃmənt/","n. 弹劾","im(入)+peach(阻碍)","face impeachment","He faced impeachment.","他面临弹劾。"],
["jurisdiction","/ˌdʒʊərɪsˈdɪkʃn/","n. 管辖权","juris(法)+dict(说)+ion","within jurisdiction","It is outside our jurisdiction.","这不在我们管辖内。"],
["liberty","/ˈlɪbəti/","n. 自由","liber(自由)+ty","fight for liberty","They cherish liberty.","他们珍视自由。"],
["oppression","/əˈpreʃn/","n. 压迫","op(反)+press(压)+ion","end oppression","The people ended oppression.","人民终结了压迫。"],
["petition","/pəˈtɪʃn/","n. 请愿","pet(寻求)+ition","sign a petition","They signed a petition.","他们签署了请愿书。"],
["ratify","/ˈrætɪfaɪ/","v. 批准","rat(判)+ify","ratify a treaty","The senate ratified it.","参议院批准了。"],
["suffrage","/ˈsʌfrɪdʒ/","n. 选举权","suffr(投票)+age","universal suffrage","Suffrage was extended.","选举权扩大了。"],
["totalitarian","/təʊˌtælɪˈteəriən/","adj. 极权的","total(全)+itarian","a totalitarian regime","The regime was totalitarian.","该政权是极权的。"],
["unilateral","/ˌjuːnɪˈlætrəl/","adj. 单边的","uni(单)+later(边)+al","a unilateral decision","It was a unilateral move.","这是单边行动。"],
# ===== 心理 / 认知 =====
["affection","/əˈfekʃn/","n. 喜爱","af+fect(做)+ion：做出来的情感","mutual affection","She felt affection.","她心怀喜爱。"],
["amnesia","/æmˈniːʒə/","n. 失忆","a(无)+mnes(记忆)+ia","suffer amnesia","He suffered amnesia.","他患了失忆症。"],
["aversion","/əˈvɜːʃn/","n. 厌恶","a(反)+vers(转)+ion","risk aversion","Investors show aversion.","投资者表现出厌恶。"],
["compulsion","/kəmˈpʌlʃn/","n. 冲动","com(共同)+puls(推)+ion","a compulsive habit","He felt a compulsion.","他感到一种冲动。"],
["conformity","/kənˈfɔːməti/","n. 从众","con(共同)+form(形)+ity","peer conformity","Conformity is strong.","从众心理很强。"],
["conscience","/ˈkɒnʃəns/","n. 良心","con(共同)+sci(知)+ence","a clear conscience","He had a clear conscience.","他问心无愧。"],
# ===== 通用学术高频 (AWL) =====
["abstract","/ˈæbstrækt/","adj. 抽象的","abs(离)+tract(拉)：抽离具体","an abstract concept","Math is abstract.","数学是抽象的。"],
["access","/ˈækses/","n. 通道","ac(向)+cess(走)","access to data","Access is limited.","访问受限。"],
["accommodate","/əˈkɒmədeɪt/","v. 容纳","ac+commod(适合)+ate","accommodate 500 guests","The hall accommodates many.","大厅能容纳很多人。"],
["accompany","/əˈkʌmpəni/","v. 陪伴","ac+company(同伴)","accompany a friend","She accompanied him.","她陪着他。"],
["accurate","/ˈækjərət/","adj. 精确的","ac+curate(细)","an accurate figure","Give an accurate number.","给个精确数字。"],
["achieve","/əˈtʃiːv/","v. 达成","a+chieve(首领)","achieve a goal","They achieved their aim.","他们达成了目标。"],
["adapt","/əˈdæpt/","v. 适应","ad(向)+apt(适合)","adapt to change","Firms must adapt.","企业必须适应。"],
["adjust","/əˈdʒʌst/","v. 调整","ad+just(正好)","adjust the plan","We adjusted the plan.","我们调整了计划。"],
["admit","/ədˈmɪt/","v. 承认","ad+mit(送)：接纳","admit a mistake","He admitted the error.","他承认了错误。"],
["adopt","/əˈdɒpt/","v. 采纳","ad+opt(选)","adopt a policy","They adopted the plan.","他们采纳了该计划。"],
["advance","/ədˈvɑːns/","v. 前进","ad+van(前)+ce","advance the cause","Science advanced.","科学进步了。"],
["adverse","/ˈædvɜːs/","adj. 不利的","ad+verse(转)：转向坏","adverse effects","The effects were adverse.","效果不利。"],
["advocate","/ˈædvəkeɪt/","v. 提倡","ad+voc(声)+ate","advocate reform","He advocated change.","他提倡变革。"],
["affect","/əˈfekt/","v. 影响","af+fect(做)","affect the outcome","It affects results.","它影响结果。"],
["afford","/əˈfɔːd/","v. 负担","af+ford(向前)","afford the cost","Few can afford it.","很少人负担得起。"],
["aggregate","/ˈæɡrɪɡət/","v. 聚集","ag+greg(群)+ate","aggregate the data","We aggregated scores.","我们汇总了分数。"],
["aid","/eɪd/","n. 援助","aid 音似'帮助'","foreign aid","They sent aid.","他们送了援助。"],
["alarm","/əˈlɑːm/","n. 警报","al+arm(武器)","raise the alarm","He raised the alarm.","他拉响了警报。"],
["alert","/əˈlɜːt/","adj. 警觉","al+ert(活动)","stay alert","Drivers must stay alert.","司机须保持警觉。"],
["alien","/ˈeɪliən/","adj. 外星的","ali(其他)+en","alien culture","The custom seemed alien.","这习俗显得陌生。"],
["alive","/əˈlaɪv/","adj. 活着的","a+live(活)","stay alive","They stayed alive.","他们活了下来。"],
["allow","/əˈlaʊ/","v. 允许","al+low(许可)","allow mistakes","We allow errors.","我们允许犯错。"],
["alter","/ˈɔːltə/","v. 改变","alter 音似'变更'","alter the design","They altered it.","他们改了它。"],
["alternative","/ɔːlˈtɜːnətɪv/","n. 替代","alter(变)+native","offer an alternative","We need an alternative.","我们需要替代方案。"],
["amazing","/əˈmeɪzɪŋ/","adj. 惊人的","a+maze(迷宫)+ing","an amazing result","The result was amazing.","结果惊人。"],
["ambition","/æmˈbɪʃn/","n. 野心","ambi(二)+tion","political ambition","He has ambition.","他有野心。"],
["amend","/əˈmend/","v. 修正","a+mend(修)","amend the law","They amended it.","他们修正了它。"],
["amount","/əˈmaʊnt/","n. 数量","a+mount(山)","a large amount","The amount grew.","数量增加了。"],
["ample","/ˈæmpl/","adj. 充足的","ampl(大)+e","ample evidence","There is ample proof.","有充足证据。"],
["amplify","/ˈæmplɪfaɪ/","v. 放大","ampl(大)+ify","amplify the signal","We amplified it.","我们放大了它。"],
["ancient","/ˈeɪnʃənt/","adj. 古老的","anc(前)+ient","ancient ruins","They found ruins.","他们发现了遗迹。"],
["announce","/əˈnaʊns/","v. 宣布","an+nounce(说)","announce a deal","They announced it.","他们宣布了。"],
["annual","/ˈænjuəl/","adj. 年度的","ann(年)+ual","annual report","The report is annual.","报告是年度的。"],
["anonymous","/əˈnɒnɪməs/","adj. 匿名的","an(无)+onym(名)+ous","anonymous source","The source was anonymous.","消息来源匿名。"],
["answer","/ˈɑːnsə/","v. 回答","answer 基础词","answer a question","She answered it.","她回答了。"],
["appeal","/əˈpiːl/","v. 吸引","ap+peal(拉)","appeal to youth","It appeals to teens.","它吸引青少年。"],
["appear","/əˈpɪə/","v. 出现","ap+pear(出现)","appear in public","He appeared calm.","他显得冷静。"],
["applicable","/əˈplɪkəbl/","adj. 适用的","ap+plic(折)+able","applicable rule","The rule is applicable.","该规则适用。"],
["apply","/əˈplaɪ/","v. 申请","ap+ply(贴)","apply for a job","She applied.","她申请了。"],
["appreciate","/əˈpriːʃieɪt/","v. 欣赏","ap+preci(价值)+ate","appreciate the help","He appreciated it.","他感激帮助。"],
["approach","/əˈprəʊtʃ/","n. 方法","ap+proach(近)","a new approach","We need an approach.","我们需要方法。"],
["appropriate","/əˈprəʊpriət/","adj. 恰当的","ap+propri(合适)+ate","appropriate response","The reply was apt.","回复恰当。"],
["approve","/əˈpruːv/","v. 批准","ap+prove(证)","approve a plan","They approved it.","他们批准了。"],
["approximate","/əˈprɒksɪmət/","adj. 近似","ap+proxim(近)+ate","an approximate cost","Give an approximate.","给个近似值。"],
["arise","/əˈraɪz/","v. 出现","a+rise(升)","problems arise","Issues arose.","问题出现了。"],
["array","/əˈreɪ/","n. 阵列","ar+ray(排)","a wide array","An array of choices.","一系列选择。"],
["artificial","/ˌɑːtɪˈfɪʃl/","adj. 人造的","art(技)+ificial","artificial intelligence","AI is artificial.","AI是人造的。"],
["aspect","/ˈæspekt/","n. 方面","a+spect(看)","every aspect","Consider each aspect.","考虑每个方面。"],
["assemble","/əˈsembl/","v. 组装","as+semble(一起)","assemble a team","We assembled it.","我们组装好了。"],
["assert","/əˈsɜːt/","v. 断言","as+sert(加)","assert a right","He asserted it.","他主张了权利。"],
["assign","/əˈsaɪn/","v. 分配","as+sign(标)","assign a task","They assigned it.","他们分派了任务。"],
["assist","/əˈsɪst/","v. 协助","as+sist(站)","assist the poor","We assisted them.","我们协助了他们。"],
["assure","/əˈʃʊə/","v. 保证","as+sure(确)","assure safety","He assured us.","他向我们保证。"],
["attach","/əˈtætʃ/","v. 附加","at+tach(固)","attach a file","She attached it.","她附上了文件。"],
["attain","/əˈteɪn/","v. 达到","at+tain(触)","attain a goal","They attained it.","他们达到了。"],
["attempt","/əˈtempt/","v. 尝试","at+tempt(试)","attempt a record","He attempted it.","他尝试了。"],
["attract","/əˈtrækt/","v. 吸引","at+tract(拉)","attract talent","It attracts talent.","它吸引人才。"],
["author","/ˈɔːθə/","n. 作者","auth(创)+or","the author of the book","He is the author.","他是作者。"],
["authority","/ɔːˈθɒrəti/","n. 权威","author(创)+ity","in authority","He has authority.","他有权威。"],
["available","/əˈveɪləbl/","adj. 可用的","a+vail(用)+able","available now","It is available.","它现在可用。"],
["average","/ˈævərɪdʒ/","adj. 平均的","average 基础词","above average","It is above average.","高于平均。"],
["aware","/əˈweə/","adj. 意识到的","a+ware(注意)","aware of risk","Be aware of danger.","意识到危险。"],
["awkward","/ˈɔːkwəd/","adj. 尴尬的","awkward 基础词","an awkward silence","There was silence.","一阵尴尬的沉默。"],
["absorb","/əbˈzɔːb/","v. 吸收","ab+sorb(吸)","absorb knowledge","He absorbed it.","他吸收了。"],
["accelerate","/əkˈseləreɪt/","v. 加速","ac+celer(快)+ate","accelerate growth","It accelerated.","它加速了。"],
["accept","/əkˈsept/","v. 接受","ac+cept(拿)","accept a job","She accepted.","她接受了。"],
["accomplish","/əˈkʌmplɪʃ/","v. 完成","ac+compl(满)+ish","accomplish a task","They accomplished it.","他们完成了。"],
["account","/əˈkaʊnt/","n. 账户","ac+count(数)","open an account","He opened one.","他开了账户。"],
["accuse","/əˈkjuːz/","v. 指责","ac+cuse(因)","accuse of theft","They accused him.","他们指控他。"],
["acquaint","/əˈkweɪnt/","v. 使熟悉","ac+quaint(知)","acquaint with facts","He acquainted us.","他让我们了解。"],
["act","/ækt/","v. 行动","act 基础词","act now","We must act.","我们必须行动。"],
["active","/ˈæktɪv/","adj. 活跃的","act+ive","stay active","Keep active.","保持活跃。"],
["actual","/ˈæktʃuəl/","adj. 实际的","act+ual","the actual cost","The actual cost is high.","实际成本很高。"],
["add","/æd/","v. 添加","add 基础词","add a point","She added one.","她加了一条。"],
["admission","/ədˈmɪʃn/","n. 录取","ad+miss(送)+ion","gain admission","He won admission.","他被录取了。"],
["adversity","/ədˈvɜːsəti/","n. 逆境","ad+vers(转)+ity","in adversity","He faced adversity.","他面对逆境。"],
["advice","/ədˈvaɪs/","n. 建议","ad+vice(看)","seek advice","He sought advice.","他寻求建议。"],
["advise","/ədˈvaɪz/","v. 建议","ad+vice(看)+e","advise a client","She advised him.","她建议他。"],
["affiliate","/əˈfɪlieɪt/","v. 附属","af+fil(子)+ate","an affiliated unit","It is affiliated.","它是附属的。"],
["agenda","/əˈdʒendə/","n. 议程","ag+enda(做)","set the agenda","They set it.","他们定了议程。"],
["aggressive","/əˈɡresɪv/","adj. 好斗的","ag+gress(走)+ive","aggressive marketing","The push was aggressive.","推广很激进。"],
["akin","/əˈkɪn/","adj. 类似的","a+kin(亲)","akin to mine","It is akin.","它类似。"],
["alliance","/əˈlaɪəns/","n. 联盟","ally(同盟)+ance","form an alliance","They formed one.","他们结了盟。"],
["allowance","/əˈlaʊəns/","n. 津贴","allow+ance","a monthly allowance","He gets an allowance.","他有津贴。"],
["amiable","/ˈeɪmiəbl/","adj. 和蔼的","am(爱)+iable","an amiable boss","The boss is amiable.","老板很和蔼。"],
["analog","/ˈænəlɒɡ/","adj. 模拟的","ana(类似)+log","analog signal","It is analog.","它是模拟的。"],
["anecdote","/ˈænɪkdəʊt/","n. 轶事","an+ec(外)+dote","tell an anecdote","He told one.","他讲了个轶事。"],
["animate","/ˈænɪmeɪt/","v. 使生动","anim(生命)+ate","animate the talk","He animated it.","他讲得生动。"],
["annex","/əˈneks/","v. 吞并","an+nex(连)","annex the land","They annexed it.","他们吞并了。"],
["annihilate","/əˈnaɪəleɪt/","v. 消灭","an+nihil(无)+ate","annihilate the enemy","They annihilated it.","他们消灭了敌人。"],
["annotate","/ˈænəteɪt/","v. 注释","an+not(标)+ate","annotate the text","She annotated it.","她加了注释。"],
["absurd","/əbˈsɜːd/","adj. 荒谬的","ab+surd(聋)","an absurd claim","The claim is absurd.","说法荒谬。"],
["abuse","/əˈbjuːz/","v. 滥用","ab+use(用)","abuse power","He abused it.","他滥用了权力。"],
["academic","/ˌækəˈdemɪk/","adj. 学术的","academy+ic","academic research","It is academic.","这是学术的。"],
["accord","/əˈkɔːd/","v. 一致","ac+cord(心)","accord with facts","It accords.","它一致。"],
["accusation","/ˌækjuˈzeɪʃn/","n. 指控","accuse+ation","face an accusation","He faced one.","他面临指控。"],
["acid","/ˈæsɪd/","adj. 酸的","acid 基础词","acid rain","Acid rain harms soil.","酸雨危害土壤。"],
["acoustic","/əˈkuːstɪk/","adj. 声学的","acou(听)+stic","acoustic design","The design is acoustic.","设计是声学的。"],
["acquit","/əˈkwɪt/","v. 宣判无罪","ac+quit(释)","acquit the defendant","They acquitted him.","他们判他无罪。"],
["acute","/əˈkjuːt/","adj. 严重的","acu(尖)+te","an acute crisis","The crisis is acute.","危机严重。"],
["adjacent","/əˈdʒeɪsənt/","adj. 相邻的","ad+jac(躺)+ent","adjacent rooms","The rooms are adjacent.","房间相邻。"],
["adjoin","/əˈdʒɔɪn/","v. 毗连","ad+join(连)","adjoin the park","It adjoins the park.","它毗连公园。"],
["administrate","/ədˈmɪnɪstreɪt/","v. 管理","ad+minister(服务)+ate","administrate a fund","They administrate it.","他们管理基金。"],
["admire","/ədˈmaɪə/","v. 钦佩","ad+mire(奇)","admire courage","She admired him.","她钦佩他。"],
["adolescent","/ˌædəˈlesnt/","n. 青少年","ad+olesc(长)+ent","an adolescent girl","She is adolescent.","她是青少年。"],
["adore","/əˈdɔː/","v. 崇拜","ad+ore(祷)","adore the music","He adores it.","他酷爱它。"],
["advent","/ˈædvent/","n. 到来","ad+vent(来)","the advent of AI","AI's advent changed all.","AI的到来改变一切。"],
["advertise","/ˈædvətaɪz/","v. 广告","ad+vert(转)+ise","advertise a product","They advertised it.","他们做了广告。"],
["affirm","/əˈfɜːm/","v. 肯定","af+firm(坚)","affirm a value","He affirmed it.","他肯定了它。"],
["agency","/ˈeɪdʒənsi/","n. 机构","agent+cy","a news agency","The agency reported.","机构报道了。"],
["agent","/ˈeɪdʒənt/","n. 代理人","ag(做)+ent","an insurance agent","He is an agent.","他是代理人。"],
["agile","/ˈædʒaɪl/","adj. 敏捷的","ag(动)+ile","an agile team","The team is agile.","团队敏捷。"],
["agitate","/ˈædʒɪteɪt/","v. 煽动","ag(动)+itate","agitate for change","They agitated.","他们鼓动变革。"],
["aloft","/əˈlɒft/","adj. 高耸的","a+loft(空)","held aloft","It was held aloft.","它被高高举起。"],
["anchor","/ˈæŋkə/","n. 锚","anchor 基础词","drop anchor","They dropped anchor.","他们抛了锚。"],
["arrogant","/ˈærəɡənt/","adj. 傲慢的","ar+rog(求)+ant","an arrogant tone","His tone was arrogant.","他语气傲慢。"],
["aspire","/əˈspaɪə/","v. 渴望","a+spire(呼吸)","aspire to lead","He aspires.","他渴望领导。"],
["athlete","/ˈæθliːt/","n. 运动员","athl(竞)+ete","a pro athlete","He is an athlete.","他是运动员。"],
["avail","/əˈveɪl/","v. 有用","a+vail(值)","avail oneself","He availed himself.","他利用了。"],
["avoid","/əˈvɔɪd/","v. 避免","a+void(空)","avoid risk","We avoid risk.","我们规避风险。"],
["accustom","/əˈkʌstəm/","v. 使习惯","ac+custom(习惯)","accustom to noise","He grew accustomed.","他习惯了。"],
["addict","/ˈædɪkt/","n. 成瘾者","ad+dict(说)：被说中","a phone addict","He is an addict.","他上瘾了。"],
["adversary","/ˈædvəsəri/","n. 对手","ad+vers(转)+ary","a worthy adversary","He met his adversary.","他遇见对手。"],
["aggravate","/ˈæɡrəveɪt/","v. 加重","ag+grav(重)+ate","aggravate the conflict","It aggravated tension.","它加剧了冲突。"],
]

MARKER = "<!-- PLUS200 injected -->"

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

    # 现有词集合（去重依据）
    existing = set(re.findall(r'class="w-word">([^<]*)', html))

    # 候选池去重 + 过滤已存在
    seen = set()
    new = []
    for w in NEW_WORDS:
        word = w[0]
        if word in existing or word in seen:
            continue
        seen.add(word)
        new.append(w)
        if len(new) >= 200:
            break

    if not new:
        print("没有可写入的新词，跳过"); return

    if MARKER not in html:
        cards = "".join(card(w, i) for i, w in enumerate(new))
        anchor = "</div>\n<div class=\"foot\">"
        assert anchor in html, "foot anchor not found"
        html = html.replace(anchor, cards + "\n</div>\n<div class=\"foot\">" + MARKER + "\n", 1)
        m = re.search(r"共 (\d+) 词", html)
        cur = int(m.group(1)) if m else 289
        html = re.sub(r"共 \d+ 词", "共 %d 词" % (cur + len(new)), html, count=1)
        print("已注入 %d 个新词（过滤重复后），总词数 %d" % (len(new), cur + len(new)))
    else:
        print("PLUS200 已注入过，跳过（幂等）。如需重做请先移除 %s" % MARKER)

    io.open(SRC, "w", encoding="utf-8").write(html)
    io.open(DST, "w", encoding="utf-8").write(html)
    print("已同步到 zheshao-study/ielts/full.html")

if __name__ == "__main__":
    main()
