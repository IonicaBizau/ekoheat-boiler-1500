#!/usr/bin/env python3
import re,difflib,json
from pathlib import Path
old=Path('analysis/ghidra/decompiled');new=Path('analysis/v1.73/decompiled')
def body(p):
 s=p.read_text();s=s.split('[decomp]> print C\n')[-1].split('[decomp]> quit')[0]
 s=re.sub(r'/\*.*?\*/','',s,flags=re.S)
 return s.strip()
def norm(s):
 s=re.sub(r'FUN_[0-9a-f]+','FUNCTION',s)
 s=re.sub(r'0x800[0-9a-f]+','FUNCTION_ADDR',s)
 s=re.sub(r'RAM[0-9a-f]{8}','RAM_ADDR',s)
 return s
O=[(p,body(p)) for p in sorted(old.glob('*.txt')) if int(p.stem,16)<0x80026048]
N=[(p,body(p)) for p in sorted(new.glob('*.txt')) if int(p.stem,16)<0x80026a24]
results=[]
for p,s in O:
 scores=[]
 for q,t in N:
  r=difflib.SequenceMatcher(None,norm(s).splitlines(),norm(t).splitlines(),autojunk=False).ratio();scores.append((r,q,t))
 r,q,t=max(scores,key=lambda v:v[0]);results.append(dict(old=p.stem,new=q.stem,similarity=round(r,5),identical_normalized=norm(s)==norm(t)))
 if r<0.999:
  diff='\n'.join(difflib.unified_diff(norm(s).splitlines(),norm(t).splitlines(),fromfile=p.stem,tofile=q.stem,n=2))
  Path('analysis/v1.73/diffs').mkdir(exist_ok=True)
  Path(f'analysis/v1.73/diffs/{p.stem}-{q.stem}.diff').write_text(diff)
Path('analysis/v1.73/function-matches.json').write_text(json.dumps(results,indent=2))
for x in results:
 if not x['identical_normalized']:print(x)
