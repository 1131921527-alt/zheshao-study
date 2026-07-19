# 每日雅思单词生成 · 执行记录

## 2026-07-18
- 运行 `scripts/gen_ielts_day.py`，生成 `ielts/day11.html`，15 词（全部带记忆故事）。
- `ielts/index.html` 列表与期数（共 12 期）已更新。
- 已 `git add -A && commit && push` 到 GitHub（commit cf580ad，main 分支）。
- 幂等正常：脚本按 next_number()+1 判定，无重复生成。

## 2026-07-19
- 运行 `scripts/gen_ielts_day.py`，生成 `ielts/day12.html`，15 词（全部带记忆故事）。
- `ielts/index.html` 列表与期数（共 13 期）已更新。
- 已 `git add -A && commit && push` 到 GitHub（commit c630664，main 分支）。
- 幂等正常：day12 不存在时正常生成，无重复。
