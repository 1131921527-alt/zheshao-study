#!/usr/bin/env python3
"""
移除所有 liveClockBar 注入页面中的底部闪动光带 (.lc-bar)
- 删除 CSS 行：#liveClockBar .lc-bar{...}
- 删除 HTML 元素：<i class="lc-bar" id="lcBar"></i>
- 删除 JS 中 lcBar 相关的变量和宽度更新逻辑
"""
import os, re, glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def remove_lc_bar_from_file(filepath):
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    if 'lc-bar' not in content and 'lcBar' not in content:
        return 'no_lc_bar'

    original = content

    # 1. 删除 CSS 行：#liveClockBar .lc-bar{...}
    # 这一行在一行内，可能有不同的压缩格式
    content = re.sub(r'#liveClockBar\s+\.lc-bar\{[^}]*\}\s*\n?', '', content)
    content = re.sub(r'#liveClockBar\s+\.lc-bar\{[^}]*\}', '', content)

    # 2. 删除 HTML 元素：<i class="lc-bar" id="lcBar"></i>
    content = re.sub(r'<i\s+class="lc-bar"\s+id="lcBar"></i>\s*\n?', '', content)
    content = re.sub(r'<i\s+class="lc-bar"\s+id="lcBar"></i>', '', content)

    # 3. 删除 JS 变量声明中的 b=document.getElementById('lcBar')
    # 原始格式：var h=...,m=...,s=...,b=document.getElementById('lcBar');
    # 替换为：var h=...,m=...,s=document.getElementById('lcS');
    content = re.sub(
        r",b=document\.getElementById\('lcBar'\)",
        "",
        content
    )

    # 4. 删除 JS 行：if(b)b.style.width=(d.getSeconds()/60*100)+'%';
    content = re.sub(r"\s*if\(b\)b\.style\.width=\(d\.getSeconds\(\)/60\*100\)\+'%';\s*\n?", "\n", content)
    content = re.sub(r"if\(b\)b\.style\.width=\(d\.getSeconds\(\)/60\*100\)\+'%';", "", content)

    # 5. 清理可能产生的多余空白行
    content = re.sub(r'\n\n\n+', '\n\n', content)

    if content == original:
        return 'no_change'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return 'ok'


def update_build_py():
    build_py = os.path.join(BASE_DIR, 'build.py')
    if not os.path.exists(build_py):
        return 'build_py_not_found'

    with open(build_py, encoding='utf-8') as f:
        content = f.read()

    if 'lc-bar' not in content and 'lcBar' not in content:
        return 'no_lc_bar_in_build_py'

    original = content

    # 删除 CSS 模板中的 .lc-bar 行
    content = re.sub(r'#liveClockBar\s+\.lc-bar\{[^}]*\}\s*\n?', '\n', content)

    # 删除 HTML 模板中的 <i class="lc-bar" id="lcBar"></i>
    content = re.sub(r'<i\s+class="lc-bar"\s+id="lcBar"></i>\s*\n?', '\n', content)

    # 删除 JS 变量声明中的 b=document.getElementById('lcBar')
    content = re.sub(
        r",b=document\.getElementById\('lcBar'\)",
        "",
        content
    )

    # 删除 JS 行：if(b)b.style.width=(d.getSeconds()/60*100)+'%';
    content = re.sub(r"\s*if\(b\)b\.style\.width=\(d\.getSeconds\(\)/60\*100\)\+'%';\s*\n?", "\n", content)

    # 清理空行
    content = re.sub(r'\n\n\n+', '\n\n', content)

    if content == original:
        return 'no_change'

    with open(build_py, 'w', encoding='utf-8') as f:
        f.write(content)

    return 'ok'


def main():
    # 找所有包含 liveClockBar 的 html 文件
    files = []
    for root, dirs, fnames in os.walk(BASE_DIR):
        # 跳过 .git 和 node_modules 等
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'node_modules')]
        for fn in fnames:
            if fn.endswith('.html'):
                files.append(os.path.join(root, fn))

    target_files = []
    for f in files:
        try:
            with open(f, encoding='utf-8') as fh:
                content = fh.read()
            if 'liveClockBar' in content:
                target_files.append(f)
        except:
            pass

    print(f'找到 {len(target_files)} 个包含 liveClockBar 的 HTML 文件')

    stats = {'ok': 0, 'no_change': 0, 'no_lc_bar': 0}
    for f in sorted(target_files):
        result = remove_lc_bar_from_file(f)
        stats[result] = stats.get(result, 0) + 1

    print(f'HTML 处理结果：')
    for k, v in stats.items():
        print(f'  {k}: {v}')

    # 更新 build.py 模板
    build_result = update_build_py()
    print(f'\nbuild.py 模板更新：{build_result}')


if __name__ == '__main__':
    main()
