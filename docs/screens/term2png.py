"""터미널 캡처(ANSI 이스케이프가 든 텍스트)를 PNG로 바꾼다.

사용: python3 term2png.py <입력.ansi> <출력.png> [창 제목]
필요: pip install ansi2html playwright && python3 -m playwright install chromium
      한글 글꼴: sudo apt-get install -y fonts-noto-cjk
"""
import html
import sys

from ansi2html import Ansi2HTMLConverter
from playwright.sync_api import sync_playwright

src, out = sys.argv[1], sys.argv[2]
title = sys.argv[3] if len(sys.argv) > 3 else ""
lines = open(src, encoding="utf-8", errors="replace").read().split("\n")
while lines and not lines[-1].strip():
    lines.pop()
while lines and not lines[0].strip():
    lines.pop(0)
body = Ansi2HTMLConverter(dark_bg=True, inline=True, scheme="xterm").convert("\n".join(lines), full=False)
page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
body {{ margin:0; background:#1e1f22; }}
.win {{ display:inline-block; background:#1e1f22; border-radius:8px; overflow:hidden; }}
.bar {{ background:#2b2d31; color:#b5b8bf; font:13px 'Noto Sans CJK KR',sans-serif; padding:7px 12px; }}
.dot {{ display:inline-block; width:11px; height:11px; border-radius:50%; margin-right:6px; vertical-align:-1px; }}
pre {{ margin:0; padding:14px 18px 16px; color:#e6e6e6; white-space:pre;
      font:14px/1.42 'DejaVu Sans Mono','Noto Sans Mono CJK KR','Noto Sans CJK KR',monospace; }}
</style></head><body><div class="win" id="w"><div class="bar">
<span class="dot" style="background:#ff5f57"></span><span class="dot" style="background:#febc2e"></span>
<span class="dot" style="background:#28c840"></span>&nbsp;{html.escape(title)}</div>
<pre>{body}</pre></div></body></html>"""
with sync_playwright() as p:
    browser = p.chromium.launch()
    pg = browser.new_page(device_scale_factor=2, viewport={"width": 1400, "height": 900})
    pg.set_content(page)
    pg.locator("#w").screenshot(path=out)
    browser.close()
print(out)
