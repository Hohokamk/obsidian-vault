from pypdf import PdfReader
r=PdfReader('qianzhan.pdf')
print('pages',len(r.pages))
parts=[]
for i,p in enumerate(r.pages):
    parts.append(f"\n===== PAGE {i+1} =====\n"+(p.extract_text() or ''))
open('qianzhan.txt','w',encoding='utf-8').write(''.join(parts))
print('chars',sum(len(x) for x in parts))
