import os, sys
from pypdf import PdfReader
src = r"D:\06_Software_Installed\Obsidian\Obsidian Vault\RM比赛\新规"
out = r"C:\Users\Hohokam\.codex\visualizations\2026\11\08\01a1ba18-1350-7bc2-93c5-c9e0d7fc5269\txt"
os.makedirs(out, exist_ok=True)
for f in os.listdir(src):
    if not f.lower().endswith('.pdf'): continue
    r = PdfReader(os.path.join(src, f))
    print(f, len(r.pages), flush=True)
    parts = []
    for i, p in enumerate(r.pages):
        try:
            t = p.extract_text() or ''
        except Exception as e:
            t = ''
        parts.append(f"\n===== PAGE {i+1} =====\n" + t)
    name = os.path.splitext(f)[0] + '.txt'
    with open(os.path.join(out, name), 'w', encoding='utf-8') as fp:
        fp.write(''.join(parts))
    print('WROTE', os.path.join(out, name), sum(len(x) for x in parts), flush=True)
