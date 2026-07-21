# zheshao-study 项目长期记忆

## 仓库真身路径
- 真实仓库（部署到 GitHub Pages）：`E:\workbuddyFIle\腾讯龙虾的成品\03-学习网站\zheshao-study\`
- 旧路径 `E:\workbuddyFIle\腾讯龙虾的成品\zheshao-study\`（无 `03-学习网站`）是已废弃副本，**不要碰**。
- GitHub Pages：`https://1131921527-alt.github.io/zheshao-study/`，main 分支自动构建。

## ⚠️ build.py 使用铁律
- `build.py` 的 `OUT` 已改回上面的真身路径。
- **源目录 `腾讯龙虾的成品\AI动态播报` / `AI学习卡片` / `雅思词汇` 当前已不存在** → build.py 现在跑了会生成 0 期并清空列表页/归档页。**源目录恢复前绝对不要跑 build.py。**
- 改布局/内容优先直接改线上仓库文件，再 git commit + push。

## 全站布局约定（2026-07-21 统一）
- 全站统一成"手机排版"：桌面端所有页面收成 **540px 手机壳**居中（深色页背景 + 圆角金边 + 阴影）。
- 列表页/归档页靠 `assets/style.css` 的 `@media(min-width:600px)` 把 `.wrap` 收成手机壳。
- 内容页（ai-news/ai-knowledge/ai-prompt/ielts 各 html）靠注入的 `FRAME_CSS`（`zsframe` 标记，用 `body:not(:has(.app/.wrap/.lesson))` 把 body 收成手机壳）。
- 知识长文在首页 SPA 的 `.lesson` 内（已在 `.app` 手机壳中），无需单独处理。
- 写 UTF-8 文件用 Node 不用 Python（Python 写中文会出孤立续字节导致 JS 崩）。

## 知识类目三处同步（改内容必看）
- 每篇内容三处必须同步：`const XXX` 数据数组 + `SLUG.xxx` 顺序 + `<article id="art-...">` 长文区块。数组顺序须与 SLUG 一致，否则点卡片开错文章。
