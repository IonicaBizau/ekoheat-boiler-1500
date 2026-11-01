#!/usr/bin/env python3
"""Generate minimal clock-screen patch for the exact analyzed v1.73 image."""
import hashlib, json, struct, subprocess, zlib
from pathlib import Path
SOURCE = Path("DTX9003 v1.73/DTX9003.uc3")
ROOT = Path("analysis/patched/v1.73")
OUTPUT = ROOT / "DTX9003_no_idle_clock.uc3"
EXPECTED = "e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a"
DELTA = 0x80007fe7
ADDRESS = 0x8000ba8e
OFFSET = ADDRESS - DELTA

def sha(b): return hashlib.sha256(b).hexdigest()

def main():
    original = SOURCE.read_bytes()
    if sha(original) != EXPECTED:
        raise SystemExit("Source SHA-256 mismatch; no output written")
    if struct.unpack_from(">I", original, 21)[0] != zlib.crc32(original[25:]):
        raise SystemExit("Source CRC mismatch; no output written")
    assert original[OFFSET-4:OFFSET+4] == bytes.fromhex("fef902f23008b208")
    assert struct.unpack_from(">I", original, 0x8000bd7c-DELTA)[0] == 0x2336
    patched = bytearray(original)
    patched[OFFSET:OFFSET+2] = bytes.fromhex("3648")
    struct.pack_into(">I", patched, 21, zlib.crc32(patched[25:]))
    changes = [i for i,(a,b) in enumerate(zip(original,patched)) if a != b]
    assert len(patched) == len(original)
    assert [i for i in changes if i >= 25] == [OFFSET, OFFSET+1]
    assert all(i in range(21,25) or i in (OFFSET, OFFSET+1) for i in changes)
    assert struct.unpack_from(">I", patched, 21)[0] == zlib.crc32(patched[25:])
    ROOT.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(patched)
    assert OUTPUT.read_bytes() == patched
    assert SOURCE.read_bytes() == original
    manifest = dict(source=str(SOURCE), output=str(OUTPUT),
        source_sha256=sha(original), output_sha256=sha(patched), size=len(patched),
        original_crc32=f"0x{zlib.crc32(original[25:]):08X}",
        patched_crc32=f"0x{zlib.crc32(patched[25:]):08X}",
        patches=[dict(address=hex(ADDRESS), file_offset=hex(OFFSET), before="3008", after="3648",
            purpose="MOV R8,0 -> MOV R8,100 at inactivity-expiry brightness request")],
        changed_byte_offsets=[hex(i) for i in changes],
        verification=dict(status="PASS", payload_bytes_changed=2, source_unchanged=True,
            crc32_valid=True, size_unchanged=True, hardware_execution=False))
    OUTPUT.with_suffix(".json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))

if __name__ == "__main__": main()
