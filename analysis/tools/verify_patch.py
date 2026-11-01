#!/usr/bin/env python3
"""Check derivative bytes, instruction semantics at boundaries, and unchanged regions."""
import argparse,hashlib,json,struct,zlib
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--version', choices=('1.72','1.73'), default='1.72')
parser.add_argument('--update-dir', type=Path, help='Also compare the two files on a prepared USB drive with the verified build')
args=parser.parse_args()
version=args.version
custom_version = {'1.72': '1.72.42', '1.73': '2.73'}[version]
root=Path('analysis/patched')/('v'+custom_version)
opening, continuation, idle, pointer_address, destination, timer_start = {
 '1.72': (0x80010f26, 0x80010f50, 0x8000b964, 0x8000bc0c, 0x228a, 0x8000b910),
 '1.73': (0x8001136a, 0x80011394, 0x8000ba8e, 0x8000bd7c, 0x2336, 0x8000ba3a),
}[version]
m=json.loads((root/'DTX9003.json').read_text())
a=Path(m['source']).read_bytes();b=Path(m['output']).read_bytes()
assert hashlib.sha256(a).hexdigest()==m['source_sha256']
assert hashlib.sha256(b).hexdigest()==m['output_sha256']
assert len(a)==len(b)==m['size']
assert a[:5] == b[:5] == b'AVR32'
assert a[:21] == b[:21], 'Update wrapper changed outside the CRC32 field'
assert struct.unpack_from('>I',a,21)[0] == zlib.crc32(a[25:])
license_bytes=(root/'license.key').read_bytes()
assert license_bytes == Path(m['source']).with_name('license.key').read_bytes(), 'Supplied license differs from source'
if args.update_dir is not None:
 assert (args.update_dir/'DTX9003.uc3').read_bytes() == b, 'USB firmware differs from the verified build'
 assert (args.update_dir/'license.key').read_bytes() == license_bytes, 'USB license differs from the supplied license'
expected=bytearray(a)
for p in m['patches']:
 o=int(p['file_offset'],16);old=bytes.fromhex(p['before']);new=bytes.fromhex(p['after'])
 assert a[o:o+len(old)]==old
 expected[o:o+len(new)]=new
struct.pack_into('>I',expected,21,zlib.crc32(expected[25:]))
assert b==expected
assert struct.unpack_from('>I',b,21)[0]==zlib.crc32(b[25:])
delta=0x80007fe7;p=opening-delta;ins=b[p:p+8]
# Decode the replacement SUB R8,R8,simm16, CP.W R8,R9 and BRHS disp8.
assert ins[:2]==bytes.fromhex('f0c8') and ins[4:6]==bytes.fromhex('1238')
imm=struct.unpack('>h',ins[2:4])[0];branch=int.from_bytes(ins[6:8],'big')
assert imm==-300 and branch&0xf00f==0xc002
q=(branch>>4)&255;q=q-256 if q&128 else q
assert opening+6+2*q==continuation
checks=0
for n in range(65536):
 threshold=n-imm
 for counter in {0,65535,max(0,min(65535,threshold-1)),min(65535,threshold),min(65535,threshold+1)}:
  # BRHS after CP R8,R9 skips error iff threshold >= counter.
  skip_error=((threshold-counter)&0xffffffff)<=threshold
  assert (not skip_error)==(counter>n+300)
  checks+=1
# MOV immediate and unchanged destination of idle-expiry store.
o=idle-delta
assert b[o:o+4]==bytes.fromhex('3648b208')
pointer=struct.unpack_from('>I',b,pointer_address-delta)[0]
assert pointer==destination
# The same timer still decrements and expires; only its expiry brightness value changes.
assert a[timer_start-delta:o]==b[timer_start-delta:o]
# Check the actual Info label storage and the call's pointer/arguments.
version_offset={'1.72': 0xccc5, '1.73': 0xd149}[version]
assert a[version_offset:version_offset+16] == b'v%d.%02d  %s\0\0\0\0'
if version == '1.73':
 label = b'v2.73  Nov  1 2026'
 assert b[version_offset:version_offset+28] == (label+b'\0').ljust(28,b'\0')
 assert b'%' not in label  # No numeric/date arguments are consumed.
 assert b[0x80016776-delta:0x80016794-delta] == a[0x80016776-delta:0x80016794-delta]
 assert b[0x80016780-delta:0x80016784-delta] == bytes.fromhex('30181ad8')
 # Constant pool used by the Info label call: date, format, destination.
 assert b[0x800169b0-delta:0x800169bc-delta] == bytes.fromhex('80015140800151300000545c')
 assert a.count(bytes.fromhex('80015140')) == 1  # Only the now-unused date argument.
 assert label.endswith(b'Nov  1 2026')
 rendered=label.decode('ascii')
else:
 assert b[version_offset:version_offset+16] == b'v%d.%02d.42 %s\0\0'
 assert a[version_offset+16:version_offset+28] == b[version_offset+16:version_offset+28]
 fmt=b[version_offset:].split(b'\0',1)[0].decode('ascii')
 date=b[version_offset+16:].split(b'\0',1)[0].decode('ascii')
 rendered=fmt % (1,72,date)
 assert rendered == 'v'+custom_version+' '+date
assert len(rendered)+1 <= 0x21
assert m['firmware_version'] == custom_version
startup_attempts = 3
if version == '1.73':
 # Decode MOV R8,imm8, CP.B R9,R8, BRHI and its unchanged failure target.
 limit_offset = 0x80024440-delta
 limit_ins = b[limit_offset:limit_offset+10]
 assert limit_ins[2:] == bytes.fromhex('f0091800e08b0006')
 mov = int.from_bytes(limit_ins[:2], 'big')
 assert mov & 0xf00f == 0x3008
 limit = (mov >> 4) & 255
 assert limit == 4
 assert 0x80024446 + 2*int.from_bytes(limit_ins[8:10], 'big') == 0x80024452
 seed_offset = 0x8000ee0c-delta
 assert b[seed_offset:seed_offset+4] == bytes.fromhex('3058b288')
 seed = (int.from_bytes(b[seed_offset:seed_offset+2], 'big') >> 4) & 255
 assert seed == limit+1 == 5
 # No changes elsewhere in either routine, including charging, waits, and faults.
 for start, end, changed in [(0x80024100,0x80024a00,limit_offset),
                             (0x8000ed44,0x8000f598,seed_offset)]:
  original = bytearray(a[start-delta:end-delta])
  original[changed-(start-delta):changed-(start-delta)+2] = b[changed:changed+2]
  assert bytes(original) == b[start-delta:end-delta]
 count = 0
 timeouts = 0
 while True:
  count = (count+1) & 255
  timeouts += 1
  if count > limit:
   break
 assert count == timeouts == 5
 # The special path must still fail at its first timeout, with no retries.
 assert ((seed+1) & 255) > limit
 assert ((3+1) & 255) > 2  # original special-path behavior
 startup_attempts = timeouts
# Failure check happens after the wait with a counter initially zero.
examples={}
for n in (0,100,1000):
 first_error=next(c for c in range(n+302) if c>n+300)
 assert first_error==n+301
 examples[str(n/10)]=dict(configured_seconds=n/10,nominal_failure_seconds=(first_error+1)/10)
result=dict(status='PASS',firmware_version=custom_version,rendered_version=rendered,boundary_comparisons=checks,crc32=hex(zlib.crc32(b[25:])),
            opening_timeout_examples=examples,update_wrapper_preserved=True,supplied_license_matches_source=True,
            normal_startup_attempts=startup_attempts,
            bootloader_acceptance_verified=False,hardware_execution=False)
(root/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
