#!/usr/bin/env python3
"""Read-only firmware metadata, strings, entropy, and exact pointer searches."""
import argparse, collections, hashlib, json, math, re, struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('firmware',nargs='?',default='Ecoheat_v1.72/DTX9003.uc3');p.add_argument('--out',default='analysis/evidence');a=p.parse_args()
b=Path(a.firmware).read_bytes();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
strings=[{'offset':hex(m.start()),'text':m.group().decode('latin1')} for m in re.finditer(rb'[\x20-\x7e]{5,}',b)]
(out/'strings.json').write_text(json.dumps(strings,indent=2))
meta={'file':a.firmware,'size':len(b),'sha256':hashlib.sha256(b).hexdigest(),'header_hex':b[:29].hex(),'entropy_4096':[]}
for i in range(0,len(b),4096):
 c=collections.Counter(b[i:i+4096]);n=sum(c.values());meta['entropy_4096'].append([hex(i),-sum(v/n*math.log2(v/n) for v in c.values())])
(out/'metadata.json').write_text(json.dumps(meta,indent=2))
print(json.dumps({k:v for k,v in meta.items() if k!='entropy_4096'},indent=2))
for s in strings:
 if any(x in s['text'].lower() for x in ['ash plate','ashplate','watchdog','timertask']):print(s)
