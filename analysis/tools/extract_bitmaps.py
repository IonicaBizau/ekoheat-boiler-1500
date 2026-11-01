#!/usr/bin/env python3
"""Extract renderer-confirmed little-endian RGB565 bitmaps, without altering firmware."""
import json,struct,zlib
from pathlib import Path
b=Path('DTX9003 v1.72/DTX9003.uc3').read_bytes();delta=0x80007fe7;table=0x8004f954
out=Path('analysis/assets');out.mkdir(exist_ok=True)
def png(path,w,h,pixels):
 def chunk(k,v):return struct.pack('>I',len(v))+k+v+struct.pack('>I',zlib.crc32(k+v))
 rows=b''.join(b'\0'+pixels[y*w*3:(y+1)*w*3] for y in range(h))
 path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b''))
assets=[]
for i in range(100):
 addr=struct.unpack_from('>I',b,table-delta+4*i)[0]
 if not 0x80039c80<=addr<table:break
 p=addr-delta;w,h=struct.unpack_from('<HH',b,p)
 if not(0<w<=320 and 0<h<=240):break
 n=4+2*w*h;raw=b[p:p+n];assert len(raw)==n
 rgb=bytearray()
 for (v,) in struct.iter_unpack('<H',raw[4:]):rgb+=bytes((((v>>11)&31)*255//31,((v>>5)&63)*255//63,(v&31)*255//31))
 file=f'bitmap-{i:02d}-{w}x{h}.png';png(out/file,w,h,rgb)
 assets.append(dict(index=i,address=hex(addr),file_offset=hex(p),width=w,height=h,length=n,preview=file))
 print(i,hex(addr),w,h)
(out/'bitmaps.json').write_text(json.dumps(assets,indent=2)+'\n')
# Contact sheet: unscaled pixels, numbered via HTML labels in the accompanying page.
W=640;H=((len(assets)+3)//4)*250;canvas=bytearray([180]*(W*H*3))
for item in assets:
 i=item['index'];p=int(item['file_offset'],16);w=item['width'];h=item['height'];x0=i%4*160;y0=i//4*250
 for y in range(h):
  for x in range(min(w,158)):
   v=struct.unpack_from('<H',b,p+4+2*(y*w+x))[0];j=((y0+y)*W+x0+x)*3
   canvas[j:j+3]=bytes((((v>>11)&31)*255//31,((v>>5)&63)*255//63,(v&31)*255//31))
png(out/'contact-sheet.png',W,H,canvas)
(out/'index.html').write_text('<!doctype html><title>Extracted firmware bitmaps</title><style>body{font:16px sans-serif;background:#bbb}figure{display:inline-block;vertical-align:top;padding:10px;border:1px solid #777}img{image-rendering:pixelated}</style>'+''.join(f'<figure><figcaption>#{a["index"]}: {a["width"]} × {a["height"]}, {a["address"]}</figcaption><img src="{a["preview"]}"></figure>' for a in assets))
