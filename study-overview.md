# 百词斩式学习台 · 完成情况

## 做了什么
把 `zheshao-study` 现有学习内容整理成了一个「百词斩式」学习工作台，已部署到 GitHub Pages（commit `1fc3f3d`）。

**核心交付文件**：
- `study.html` — 单一文件的学习台主页面（深色主题、移动端优先），仿百词斩卡片刷词交互。
- `assets/ai_cards.json` — 从 `ai-  news/*.html` 抽取整理的 38 张 AI 动态卡片（tag/标题/摘要/影响/应用/来源/日期）。
- `assets/knowledge_cards.json` — 从 `knowledge/articles/*.html` 抽取的 35 张知识卡片（标题/分类/摘要/链接）。
- `scripts/extract_ai_cards.py`、`scripts/extract_knowledge.py` — 可重复的抽取脚本。

## 三个学习模块（刷词卡）
1. **英语·雅思词汇**：调用线上 `ielts/ielts_bank.json`（1151 词），卡片右侧喇叭播放美音 `ielts/audio/{word}_us.mp3`；正反面翻转 + 「认识/不认识」分流。
2. **AI 动态**：38 篇 AI 资讯卡，含影响解读与落地应用。
3. **知识卡片**：35 篇历史/文化/地理/心理/运动健康等概念卡。

## 交互细节（仿百词斩）
- 首页三套卡组进度条 + 经验值 chip + 「开始学习」入口。
- 卡片 3D rotateY 翻转、已知/未掌握分流、未掌握自动进待复习队列。
- 结果页出正确率，进度存 `localStorage`（前缀 `wb_study_`），支持导出/导入 JSON 备份。
- 首页 `index.html` 顶部加了「百词斩式学习台」渐变 banner 入口。

## 部署
- 学习台在线地址（任意设备浏览器打开）：**https://1131921527-alt.github.io/zheshao-study/study.html**
- 首页入口：**https://1131921527-alt.github.io/zheshao-study/**

## 注意事项 / 待跟进
- ⚠️ 本地工作区 `index.html` 当前是未提交的「V3.0 学习中心」草稿（与已部署的带 banner 版本不同）。如需把本地镜像也对齐，说一声「同步本地 index.html」我来处理。
- 临时目录 `E:\workbuddyFIle\腾讯龙虾的成品\__zs_clone_tmp` 是恢复 git 时建的，可手动删除（非危险，但我不会主动删）。
- 英语学习量以线上 `ielts_bank.json` 实际 1151 词为准（本地 json 有 1170 条，线上部署版为 1151）。
