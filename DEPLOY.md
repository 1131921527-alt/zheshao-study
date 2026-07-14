# 喆少的学习任务 · 部署到 GitHub Pages

站点已在本机生成并初始化 git 仓库（分支 main，已提交），远程 origin 已指向 GitHub 仓库 `1131921527-alt/zheshao-study`。

当前沙箱环境无外网，无法自动推送。在**能联网的机器**上按下面三步即可上线。

## 1. 创建 GitHub 仓库（仅首次）
把 `<TOKEN>` 换成你自己的 GitHub Personal Access Token（要有 repo 权限）：

```bash
curl -X POST https://api.github.com/user/repos \
  -H "Authorization: token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name":"zheshao-study","public":true,"homepage":"https://1131921527-alt.github.io/zheshao-study/"}'
```

## 2. 推送（远程已配好，含 token）
在本仓库目录下执行：

```bash
git push -u origin main
```

## 3. 开启 GitHub Pages
```bash
curl -X POST https://api.github.com/repos/1131921527-alt/zheshao-study/pages \
  -H "Authorization: token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"source":{"branch":"main","path":"/"}}'
```

等待约 1 分钟，访问：**https://1131921527-alt.github.io/zheshao-study/**

## 每日更新（自动化跑完新内容后）
在本仓库目录执行：
```bash
python build.py
git add -A && git commit -m "daily update" && git push
```
`build.py` 会重新扫描 `腾讯龙虾的成品` 下各板块目录，自动归一化命名、生成首页与各板块历史列表页，所以历史会自动累积。

## 赞赏码（打赏）
把你的微信赞赏码图片命名为 `wechat.png`，放进 `assets/` 目录，首页打赏区块会自动显示。不填则显示占位提示。

## 目录结构
```
喆少的学习任务/
├── index.html            # 首页：4板块卡片 + 打赏
├── ai-news/              # AI动态播报（按日期，历史可看）
├── ai-knowledge/         # AI系统性学习（Day N）
├── ai-prompt/            # 提示词技巧（Day N）
├── ielts/                # 雅思单词（Day N + 完整版带音频）
├── assets/               # style.css + 赞赏码
└── build.py              # 站点生成器（重跑即同步）
```
