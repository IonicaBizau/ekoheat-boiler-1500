#!/usr/bin/env python3
"""Check derivative bytes, instruction semantics at boundaries, and unchanged regions."""
import hashlib,json,struct,zlib
from pathlib import Path
root=Path('analysis/patched');m=json.loads((root/'DTX9003_no_idle_clock_30s.json').read_text())
a=Path(m['source']).read_bytes();b=Path(m['output']).read_bytes()
assert hashlib.sha256(a).hexdigest()==m['source_sha256']
assert hashlib.sha256(b).hexdigest()==m['output_sha256']
assert len(a)==len(b)==m['size']
expected=bytearray(a)
for p in m['patches']:
 o=int(p['file_offset'],16);old=bytes.fromhex(p['before']);new=bytes.fromhex(p['after'])
 assert a[o:o+len(old)]==old
 expected[o:o+len(new)]=new
struct.pack_into('>I',expected,21,zlib.crc32(expected[25:]))
assert b==expected
assert struct.unpack_from('>I',b,21)[0]==zlib.crc32(b[25:])
delta=0x80007fe7;p=0x80010f26-delta;ins=b[p:p+8]
# Decode the replacement SUB R8,R8,simm16, CP.W R8,R9 and BRHS disp8.
assert ins[:2]==bytes.fromhex('f0c8') and ins[4:6]==bytes.fromhex('1238')
imm=struct.unpack('>h',ins[2:4])[0];branch=int.from_bytes(ins[6:8],'big')
assert imm==-300 and branch&0xf00f==0xc002
q=(branch>>4)&255;q=q-256 if q&128 else q
assert 0x80010f2c+2*q==0x80010f50
checks=0
for n in range(65536):
 threshold=n-imm
 for counter in {0,65535,max(0,min(65535,threshold-1)),min(65535,threshold),min(65535,threshold+1)}:
  # BRHS after CP R8,R9 skips error iff threshold >= counter.
  skip_error=((threshold-counter)&0xffffffff)<=threshold
  assert (not skip_error)==(counter>n+300)
  checks+=1
# MOV immediate and unchanged destination of idle-expiry store.
o=0x8000b964-delta
assert b[o:o+4]==bytes.fromhex('3648b208')
pointer=struct.unpack_from('>I',b,0x8000bc0c-delta)[0]
assert pointer==0x228a
# The same timer still decrements and expires; only its expiry brightness value changes.
assert a[0x8000b910-delta:o]==b[0x8000b910-delta:o]
# Failure check happens after the wait with a counter initially zero.
examples={}
for n in (0,100,1000):
 first_error=next(c for c in range(n+302) if c>n+300)
 assert first_error==n+301
 examples[str(n/10)]=dict(configured_seconds=n/10,nominal_failure_seconds=(first_error+1)/10)
result=dict(status='PASS',boundary_comparisons=checks,crc32=hex(zlib.crc32(b[25:])),
            opening_timeout_examples=examples,hardware_execution=False)
(root/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
