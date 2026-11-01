#!/usr/bin/env python3
"""Create an offline derivative of one hash-identified firmware. Never writes input."""
import hashlib, json, struct, zlib
from pathlib import Path
SOURCE = Path('DTX9003 v1.72/DTX9003.uc3')
OUTPUT = Path('analysis/patched/DTX9003_no_idle_clock_30s.uc3')
EXPECTED_SHA256 = 'b5ab1b7380f2486c29cf6708954cdb5bbaa2d7798fd0103f845fa254da51a5e8'
DELTA = 0x80008000 - 25
PATCHES = [
    (0x8000b964, '3008', '3648', 'Idle expiry: MOV R8,0 -> MOV R8,100; retain active display brightness'),
    (0x80010f26, '29c81039e08a0013', 'f0c8fed41238c122',
     'Opening check: add 300 instead of 100; swap comparison and use unsigned short branch to same target'),
]
def sha(b): return hashlib.sha256(b).hexdigest()
def main():
    original = SOURCE.read_bytes()
    if sha(original) != EXPECTED_SHA256: raise SystemExit('Source hash mismatch; no output written')
    if zlib.crc32(original[25:]) != struct.unpack_from('>I', original,21)[0]:
        raise SystemExit('Original payload CRC mismatch')
    patched = bytearray(original); records=[]; allowed=set(range(21,25))
    for va, oldhex, newhex, purpose in PATCHES:
        offset=va-DELTA; old=bytes.fromhex(oldhex); new=bytes.fromhex(newhex)
        assert len(old)==len(new)
        assert original[offset:offset+len(old)]==old, hex(va)
        patched[offset:offset+len(new)]=new
        allowed.update(range(offset,offset+len(new)))
        records.append(dict(address=hex(va),file_offset=hex(offset),before=oldhex,after=newhex,purpose=purpose))
    crc=zlib.crc32(patched[25:]);struct.pack_into('>I',patched,21,crc)
    changed=[i for i,(a,b) in enumerate(zip(original,patched)) if a!=b]
    assert set(changed)<=allowed and len(patched)==len(original)
    assert struct.unpack_from('>I',patched,21)[0]==zlib.crc32(patched[25:])
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_bytes(patched)
    assert SOURCE.read_bytes()==original
    manifest=dict(source=str(SOURCE),output=str(OUTPUT),source_sha256=sha(original),output_sha256=sha(patched),
                  size=len(patched),original_crc32=hex(zlib.crc32(original[25:])),patched_crc32=hex(crc),
                  patches=records,changed_byte_offsets=[hex(x) for x in changed],
                  validation_scope='Static disassembly, checksum and bounded logical checks; no hardware execution or flashing')
    OUTPUT.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
