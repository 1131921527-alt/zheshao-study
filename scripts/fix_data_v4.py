# -*- coding: utf-8 -*-
"""第14轮数据修复 v4：替换 6 个「例句不含目标词」的词（含连字符词 retrieve/skill/carry-on/well-being/lay-off/up-to-date）"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, 'ielts', 'ielts_bank.json')

NEW_EX = {
    'retrieve': [
        ('You can retrieve the deleted file from the recycle bin.', '你可以从回收站找回被删除的文件。'),
        ('The system allows users to retrieve data within seconds.', '该系统允许用户几秒钟内检索数据。'),
        ('He retrieved his wallet from the lost property office.', '他从失物招领处取回了钱包。')],
    'skill': [
        ('Reading is a skill that improves with daily practice.', '阅读是一种靠每日练习提高的技能。'),
        ('The course helps students develop practical skills.', '这门课帮助学生培养实用技能。'),
        ('Her technical skills made her the strongest candidate.', '她的技术技能使她成为最有竞争力的候选人。')],
    'carry-on': [
        ('Each passenger may take one carry-on bag onto the plane.', '每位乘客可携带一件随身行李登机。'),
        ('The airline limits carry-on luggage to seven kilograms.', '该航空公司将随身行李限制在七公斤以内。'),
        ('Liquids in your carry-on must be under 100 millilitres.', '随身行李中的液体每瓶不得超一百毫升。')],
    'well-being': [
        ('Regular exercise improves both physical and mental well-being.', '规律运动能改善身心健康。'),
        ('The policy aims to promote the well-being of elderly citizens.', '该政策旨在提升老年公民的福祉。'),
        ('Poor sleep can seriously affect your well-being.', '睡眠不足会严重影响你的健康。')],
    'lay-off': [
        ('The factory announced a lay-off of two hundred workers.', '这家工厂宣布裁员两百人。'),
        ('Many families were affected by the recent lay-offs.', '许多家庭受到最近裁员的影响。'),
        ('A lay-off can also be a chance to retrain for a new career.', '裁员也可能是为新的职业重新受训的机会。')],
    'up-to-date': [
        ('Make sure your information is up-to-date before the meeting.', '开会前请确保你的信息是最新的。'),
        ('The guide gives up-to-date advice on visa applications.', '这份指南提供关于签证申请的最新建议。'),
        ('Hospitals need up-to-date equipment to treat patients.', '医院需要最新的设备来治疗病人。')],
}


def main():
    bank = json.load(io.open(BANK, encoding='utf-8'))
    n = 0
    for x in bank:
        if x['word'] in NEW_EX:
            x['examples'] = [{'en': a, 'cn': b} for a, b in NEW_EX[x['word']]]
            exs = x['examples']
            x['en'], x['cn'] = exs[0]['en'], exs[0]['cn']
            n += 1
    with io.open(BANK, 'w', encoding='utf-8') as f:
        json.dump(bank, f, ensure_ascii=False, indent=1)
    print('替换例句 %d 词' % n)


if __name__ == '__main__':
    main()
