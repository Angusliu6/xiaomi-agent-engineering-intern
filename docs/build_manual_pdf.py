"""Generate a readable Chinese PDF handbook from Markdown source chapters."""
from pathlib import Path
from html import escape
import mistune
from weasyprint import HTML
root=Path(__file__).resolve().parents[1]
order=[('LEARNING_PATH.md','01 学习路线与验收'),('KNOWLEDGE_MAP.md','02 知识图谱'),('COURSE_NOTES.md','03 课程资料与掌握深度'),('QUESTION_BANK.md','04 复习口试与实验'),('PROJECT_SPEC.md','05 项目技术实施'),('BASELINE_REPORT.md','06 首次实验报告'),('OPERATIONS.md','07 运行与调试'),('INTERVIEW_GUIDE.md','08 简历与面试'),('HR_REVIEW.md','09 HR 审查与下一步')]
markdown=mistune.create_markdown(plugins=['table','strikethrough'])
parts=[]
for name,title in order:
    md=(root/'docs'/name).read_text(encoding='utf-8')
    parts.append(f'<section class="chapter"><div class="eyebrow">TRACE-QA / FIELD MANUAL</div><h2 class="chapter-title">{escape(title)}</h2>{markdown(md)}</section>')
html=f'''<!doctype html><html lang="zh"><head><meta charset="utf-8"><style>
@page {{ size:A4; margin: 20mm 17mm 19mm 17mm; @bottom-right {{content: 'TRACE-QA  /  ' counter(page); color:#75879e; font-size:9px;}}}}
body{{font-family:'Noto Sans CJK SC',sans-serif;color:#1b2940;font-size:10.2pt;line-height:1.65;}}
.cover{{height:220mm;display:flex;flex-direction:column;justify-content:center;background:#0e2038;color:white;margin:-20mm -17mm -19mm -17mm;padding:26mm;box-sizing:border-box;page-break-after:always}}
.kicker,.eyebrow{{color:#286baa;font-size:10pt;letter-spacing:2px;font-weight:bold}}.cover .kicker{{color:#efca84}}
.cover h1{{font-size:38pt;line-height:1.2;letter-spacing:-.4pt;color:#70b7ff;margin:16mm 0 4mm}}
.cover p{{font-size:15pt;color:#d5deea}}.cover .tagline{{font-size:11pt;color:#efca84;margin-top:17mm}}
.chapter{{page-break-before:always}}.chapter-title{{font-size:21pt;color:#14548b;border-bottom:2px solid #e1b76e;padding-bottom:3mm}}
h1{{font-size:16pt;color:#16395b;page-break-after:avoid}}h2{{font-size:14pt;color:#1d4d79;page-break-after:avoid}}h3{{font-size:12pt;color:#155f88;page-break-after:avoid}}
p,li{{orphans:2;widows:2}} ul,ol{{padding-left:6mm}} li{{margin-bottom:1.7mm}}a{{color:#1b62ad;overflow-wrap:anywhere}}
table{{border-collapse:collapse;width:100%;font-size:8.3pt;margin:5mm 0;table-layout:fixed;}}
th{{background:#e8f0f8;color:#173858;font-weight:700}}td,th{{border:1px solid #cbd5e1;padding:2.2mm;vertical-align:top;overflow-wrap:anywhere;}}
tr{{break-inside:avoid}}blockquote{{border-left:3px solid #e8bc76;background:#f3f6f9;padding:1mm 5mm;color:#2b3d4e}}
pre{{white-space:pre-wrap;background:#13263b;color:#eff6ff;padding:4mm;border-radius:2mm;font-family:'Noto Sans Mono CJK SC',monospace;font-size:8pt;overflow-wrap:anywhere;}}
code{{font-family:'Noto Sans Mono CJK SC',monospace;font-size:.88em;background:#edf2f8;padding:0 1px}}
pre code{{color:white;background:transparent}}
</style></head><body><div class="cover"><div class="kicker">ENGINEERING FIELD MANUAL · A09799</div><h1>TRACE–QA</h1><p>Agent Engineering 学习路线与科研项目完整说明书</p><div class="tagline">课程 · 知识图谱 · 口试 · 工程实施 · 评测 · HR 审查</div><p style="font-size:10pt;margin-top:20mm">2026-11 · 独立学习工程项目 · 明确区分已完成与待验证功能</p></div>{''.join(parts)}</body></html>'''
out=root/'docs'/'TRACE-QA-完整学习与项目说明书.pdf'
HTML(string=html,base_url=str(root)).write_pdf(out)
print(out, out.stat().st_size)
