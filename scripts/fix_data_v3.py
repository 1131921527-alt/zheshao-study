# -*- coding: utf-8 -*-
"""
第14轮数据修复 v3：
  1) 修正拼错的单词：bais→bias / breif→brief / foreast→forecast / retrive→retrieve / supress→suppress
  2) 重写 31 个「例句是 There was silence. / They set it. 这类不含目标词的指代废句」
  3) short-day 的 pos 是英文 adjective，改中文并换例句
  4) 改名后重新去重（bias/brief/forecast/retrieve 词库里已有）
"""
import io
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, 'ielts', 'ielts_bank.json')

RENAME = {'bais': 'bias', 'breif': 'brief', 'foreast': 'forecast',
          'retrive': 'retrieve', 'supress': 'suppress'}

# 重写例句：每条都必须含目标词本身（或其直接屈折形式），中文为自然通顺的翻译
NEW_EX = {
    'ancient': [
        ('The ancient temple attracts thousands of visitors every year.', '这座古庙每年吸引成千上万的游客。'),
        ('Historians study ancient civilisations to understand how cities developed.', '历史学家研究古代文明，以了解城市是如何发展的。'),
        ('The ancient wall has survived several earthquakes.', '那道古老的城墙历经数次地震仍保存完好。')],
    'appropriate': [
        ('Jeans are not appropriate for a formal interview.', '牛仔裤不适合正式的面试场合。'),
        ('The teacher chose an appropriate example to explain the rule.', '老师选了一个恰当的例子来解释这条规则。'),
        ('Please use the appropriate form when you apply.', '申请时请填写相应的表格。')],
    'arise': [
        ('New opportunities arise whenever industries change.', '产业变革时总会出现新的机会。'),
        ('Problems may arise if the data is incomplete.', '如果数据不完整，可能会出现问题。'),
        ('Serious difficulties arose during the construction of the bridge.', '桥梁施工期间出现了严重的困难。')],
    'awkward': [
        ('There was an awkward silence after his rude remark.', '他那句无礼的话之后，是一阵尴尬的沉默。'),
        ('She felt awkward when she forgot her colleague name.', '忘了同事的名字让她感到尴尬。'),
        ('Both sides avoided the awkward question.', '双方都回避了那个尴尬的问题。')],
    'account': [
        ('He opened a bank account as soon as he arrived.', '他一到就开了一个银行账户。'),
        ('You need a valid ID to access your account.', '你需要有效身份证件才能进入你的账户。'),
        ('The account shows a balance of two thousand dollars.', '该账户显示余额为两千美元。')],
    'agenda': [
        ('The first item on the agenda is the budget review.', '议程的第一项是预算审查。'),
        ('They set the agenda for next week meeting.', '他们确定了下周会议的议程。'),
        ('Climate change is now high on the political agenda.', '气候变化如今在政治议程中占据重要位置。')],
    'alliance': [
        ('The two companies formed an alliance to share technology.', '两家公司结成联盟以共享技术。'),
        ('The alliance between the parties collapsed after the election.', '选举之后，各党派之间的联盟瓦解了。'),
        ('A strong alliance can reduce costs for both sides.', '牢固的联盟能为双方降低成本。')],
    'anecdote': [
        ('He told a funny anecdote about his first day at work.', '他讲了一件关于上班第一天的趣事。'),
        ('The lecture was enlivened by personal anecdotes.', '个人的轶事让这场讲座生动起来。'),
        ('Anecdotes are not reliable evidence in research.', '轶事在研究中并不是可靠的证据。')],
    'accusation': [
        ('He faced a serious accusation of bribery.', '他面临一项严重的贿赂指控。'),
        ('The company denied all accusations of pollution.', '该公司否认了所有关于污染的指控。'),
        ('She made the accusation without any proof.', '她在没有任何证据的情况下提出了指控。')],
    'acquit': [
        ('The jury acquitted him after a long trial.', '经过漫长的审判，陪审团宣判他无罪。'),
        ('She was acquitted of all charges last month.', '她上个月被宣判所有指控均不成立。'),
        ('The court acquitted the two men for lack of evidence.', '法庭因证据不足宣判那两名男子无罪。')],
    'characteristic': [
        ('Honesty is a characteristic she has always valued.', '诚实是她一直看重的品质。'),
        ('This plant has characteristic broad leaves.', '这种植物具有特有的宽叶。'),
        ('One characteristic of the region is its dry climate.', '该地区的一个特征是气候干燥。')],
    'commit': [
        ('He committed himself to finishing the project on time.', '他承诺按时完成这个项目。'),
        ('The government has committed more funds to education.', '政府已承诺向教育投入更多资金。'),
        ('Nobody wants to commit the same mistake twice.', '没有人愿意犯两次同样的错误。')],
    'compel': [
        ('Heavy snow compelled them to stay indoors.', '大雪迫使他们待在室内。'),
        ('The law compels companies to publish their data.', '法律强制公司公布自己的数据。'),
        ('He felt compelled to apologise for his behaviour.', '他觉得不得不为自己的行为道歉。')],
    'confer': [
        ('The university conferred an honorary degree on her.', '这所大学授予她一个荣誉学位。'),
        ('The committee conferred with experts before deciding.', '委员会在决定前与专家进行了商议。'),
        ('A title was conferred on him for his services.', '他因所作的贡献被授予一个头衔。')],
    'infer': [
        ('We can infer his intentions from his behaviour.', '我们可以从他的行为推断出他的意图。'),
        ('Scientists inferred the ancient climate from tree rings.', '科学家从树木年轮推断出古代的气候。'),
        ('What can we infer from these statistics?', '我们能从这些统计数据中推断出什么？')],
    'lag': [
        ('The economy lagged behind other countries for years.', '该国经济多年来落后于其他国家。'),
        ('There is a time lag between research and application.', '研究与应用之间存在时间差。'),
        ('Rural schools often lag in access to technology.', '农村学校在获取技术方面常常落后。')],
    'occur': [
        ('Earthquakes occur frequently in this region.', '这个地区地震频发。'),
        ('An idea occurred to me while I was reading.', '我读书的时候想到了一个主意。'),
        ('It never occurred to her that he might be lying.', '她从未想过他可能在撒谎。')],
    'overcome': [
        ('She overcame her fear of public speaking.', '她克服了对公开演讲的恐惧。'),
        ('Engineers overcame the technical problems one by one.', '工程师们逐一克服了技术难题。'),
        ('Many students overcome difficulties through persistence.', '许多学生靠坚持克服困难。')],
    'oversee': [
        ('An experienced manager will oversee the construction.', '一位经验丰富的经理将监督施工。'),
        ('He oversaw the work of twenty employees.', '他监督二十名员工的工作。'),
        ('The committee oversees the use of public funds.', '该委员会监督公共资金的使用。')],
    'permit': [
        ('The rules do not permit smoking in the building.', '规定不允许在楼内吸烟。'),
        ('You need a permit to park here.', '在这里停车需要许可证。'),
        ('Weather conditions permitted the plane to take off.', '天气条件允许飞机起飞。')],
    'rebel': [
        ('The rebels seized control of the capital.', '反叛者控制了首都。'),
        ('He rebelled against his parents strict rules.', '他反抗父母严格的规定。'),
        ('Many young people rebel against tradition.', '许多年轻人反抗传统。')],
    'transfer': [
        ('He transferred to the Beijing office last year.', '他去年调到了北京办事处。'),
        ('The data can be transferred in a few seconds.', '数据可以在几秒钟内完成传输。'),
        ('The transfer of technology boosted local industry.', '技术转让促进了当地工业的发展。')],
    'undertake': [
        ('He undertook the project despite the tight deadline.', '尽管期限很紧，他还是承担了那个项目。'),
        ('The team will undertake a survey next month.', '团队下个月将开展一项调查。'),
        ('Few companies are willing to undertake such risk.', '很少有公司愿意承担这样的风险。')],
    'uphold': [
        ('The court upheld the original decision.', '法院维持了原判。'),
        ('Leaders must uphold the values they preach.', '领导者必须维护他们所宣扬的价值观。'),
        ('The treaty upholds the rights of every member state.', '该条约维护每一个成员国的权利。')],
    'withdraw': [
        ('He withdrew some money from the account.', '他从账户里取了一些钱。'),
        ('The company withdrew its offer after the review.', '复审之后，该公司撤回了报价。'),
        ('She withdrew from the competition due to illness.', '她因病退出了比赛。')],
    'withhold': [
        ('They withheld the truth from the public.', '他们向公众隐瞒了真相。'),
        ('The bank may withhold part of your payment.', '银行可能会扣留你的一部分付款。'),
        ('He withheld his consent until the terms improved.', '在条款改善之前，他拒绝表示同意。')],
    'withstand': [
        ('The bridge withstood the storm without damage.', '那座桥经受住了暴风雨，毫发无损。'),
        ('This material can withstand very high temperatures.', '这种材料能承受很高的温度。'),
        ('Few plants can withstand such a long drought.', '很少有植物能经受住如此持久的干旱。')],
    'admit': [
        ('He admitted that he had made a mistake.', '他承认自己犯了一个错误。'),
        ('She admitted the error during the meeting.', '她在会上承认了这个失误。'),
        ('The museum admits visitors free of charge on Sundays.', '该博物馆周日免费接待参观者。')],
    'liquidation': [
        ('The firm went into liquidation after years of losses.', '连年亏损之后，该公司进入了清算程序。'),
        ('Creditors applied for the liquidation of the company.', '债权人申请对该公司进行清算。'),
        ('Liquidation may take more than a year to complete.', '清算可能需要一年多才能完成。')],
    'undergo': [
        ('The city has undergone great changes in ten years.', '这座城市十年间经历了巨大的变化。'),
        ('Patients must undergo a full medical examination.', '病人必须接受全面的体检。'),
        ('The old system underwent a complete reform.', '旧体制经历了一次彻底的改革。')],
    'debug': [
        ('Engineers spent two days debugging the new software.', '工程师花了两天调试这款新软件。'),
        ('It is easier to debug code in small sections.', '分小段调试代码会更容易。'),
        ('He debugged the app before releasing it.', '他在发布前对这款应用进行了调试。')],
    'short-day': [
        ('Short-day plants flower only when the nights grow long.', '短日照植物只有在夜变长时才会开花。'),
        ('The short-day variety is widely grown in northern regions.', '这种短日照品种在北方地区被广泛种植。'),
        ('Farmers select short-day crops for the autumn harvest.', '农民选择短日照作物用于秋季收割。')],
}

POS_FIX = {'short-day': 'adj. 短日照的（植物学）'}


def main():
    bank = json.load(io.open(BANK, encoding='utf-8'))
    stat = {'renamed': 0, 'examples': 0, 'pos': 0}

    # 1) 改错拼词
    for x in bank:
        w = x['word']
        if w in RENAME:
            x['word'] = RENAME[w]
            stat['renamed'] += 1
    # 2) 重写例句 / 修 pos
    for x in bank:
        w = x['word']
        if w in NEW_EX:
            x['examples'] = [{'en': a, 'cn': b} for a, b in NEW_EX[w]]
            stat['examples'] += 1
        if w in POS_FIX:
            x['pos'] = POS_FIX[w]
            stat['pos'] += 1

    # 3) 改名后去重（合并到已有词条）
    seen, deduped = {}, []
    dup = 0
    for x in bank:
        w = x['word']
        if w in seen:
            first = seen[w]
            dup += 1
            if len(x.get('pos') or '') > len(first.get('pos') or ''):
                first['pos'] = x['pos']
            have = {(e.get('en') or '').strip() for e in (first.get('examples') or [])}
            for e in (x.get('examples') or []):
                if (e.get('en') or '').strip() and (e.get('en') or '').strip() not in have:
                    have.add((e.get('en') or '').strip())
                    first.setdefault('examples', []).append(e)
            if len(x.get('ipa') or '') > len(first.get('ipa') or ''):
                first['ipa'] = x['ipa']
            continue
        seen[w] = x
        deduped.append(x)
    bank = deduped

    # 4) 同步 en/cn，裁剪 3 条
    for x in bank:
        exs = [e for e in (x.get('examples') or []) if (e.get('en') or '').strip()]
        x['examples'] = exs[:3]
        if exs:
            x['en'] = exs[0]['en']
            x['cn'] = exs[0].get('cn') or ''

    with io.open(BANK, 'w', encoding='utf-8') as f:
        json.dump(bank, f, ensure_ascii=False, indent=1)
    print('修正错拼词 %d 个 | 重写例句 %d 词 | 修 pos %d 个 | 改名后再去重 %d 条'
          % (stat['renamed'], stat['examples'], stat['pos'], dup))
    print('词库最终 %d 词' % len(bank))


if __name__ == '__main__':
    main()
