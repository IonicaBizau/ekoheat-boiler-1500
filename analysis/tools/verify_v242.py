#!/usr/bin/env python3
"""Independently verify the minimal v2.42 patch and optional two-file update copy.

Run from the repository root. Expectations are fixed here, not imported from the
generator or accepted from its manifest. Checks remain enabled under python -O.
"""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

SOURCE = Path('DTX9003 v1.73/DTX9003.uc3')
ROOT = Path('analysis/patched/v2.42')
SOURCE_SHA256 = 'e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a'
LICENSE_SHA256 = '8075e4bc145fadd645f7edfe2ec00c0b644b5a6edef3349531d5ff4cc155c3b5'
DELTA = 0x80007fe7


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(update_dir=None, strict_package=False):
    original = SOURCE.read_bytes()
    patched = (ROOT / 'DTX9003.uc3').read_bytes()
    license_bytes = (ROOT / 'license.key').read_bytes()
    require(sha(original) == SOURCE_SHA256, 'Wrong original v1.73 source')
    require(len(original) == len(patched) == 453229, 'Image size changed')
    require(original[:5] == b'AVR32' and original[:21] == patched[:21], 'Wrapper changed')
    for data in (original, patched):
        require(struct.unpack_from('>I', data, 21)[0] == zlib.crc32(data[25:]), 'Payload CRC32 mismatch')
    require(license_bytes == SOURCE.with_name('license.key').read_bytes() == bytes.fromhex('341c'),
            'License differs from original v1.73')
    require(sha(license_bytes) == LICENSE_SHA256, 'Wrong license hash')

    # Reconstruct only the two approved substitutions from independently fixed
    # file offsets. A changed manifest cannot authorize other byte changes.
    label = b'v2.42  Nov  8 2026'
    before_label = b'v%d.%02d  %s\0\0\0\0Jul 13 2016\0'
    after_label = (label + b'\0').ljust(28, b'\0')
    replacements = [(0xd149, before_label, after_label),
                    (0x3aa7, bytes.fromhex('3008'), bytes.fromhex('3648'))]
    expected = bytearray(original)
    for offset, before, after in replacements:
        require(len(before) == len(after), 'Replacement changes length')
        require(original[offset:offset + len(before)] == before, 'Original bytes mismatch')
        expected[offset:offset + len(after)] = after
    struct.pack_into('>I', expected, 21, zlib.crc32(expected[25:]))
    require(patched == expected, 'Output contains missing or unapproved changes')

    # MOV immediate to R8; the halfword store and its RAM destination are original.
    mov = int.from_bytes(patched[0x3aa7:0x3aa9], 'big')
    require(mov & 0xf00f == 0x3008 and (mov >> 4) & 255 == 100, 'Wrong idle MOV')
    require(patched[0x3aa3:0x3aab] == bytes.fromhex('fef902f23648b208'), 'Idle load/store changed')
    require(struct.unpack_from('>I', patched, 0x8000bd7c - DELTA)[0] == 0x2336,
            'Idle brightness store targets wrong RAM')

    # Info call: unused date/number arguments, format pointer, 33-byte bound,
    # output pointer, call and stack cleanup must retain their stock encodings.
    call = bytes.fromhex('fef8023a1ad834981ad830181ad8fefa0230321bfefc022ef01f004c2fdd')
    require(patched[0x80016776 - DELTA:0x80016794 - DELTA] == call, 'Info call changed')
    require(patched[0x800169b0 - DELTA:0x800169bc - DELTA] ==
            bytes.fromhex('80015140800151300000545c'), 'Info pointers changed')
    require(original.count(bytes.fromhex('80015140')) == 1, 'Unexpected direct date references')
    require(b'%' not in label and len(label) + 1 <= 33, 'Label formatting/buffer invalid')
    require(patched[0xd149:0xd165] == after_label, 'Label/padding invalid')

    # Explicit regression checks on the routines modified by the older v2.73.
    for start, end in [(0x80011238, 0x80011394), (0x8000ed44, 0x8000f598),
                       (0x80024100, 0x80024a00)]:
        require(original[start - DELTA:end - DELTA] == patched[start - DELTA:end - DELTA],
                'Original motor/startup routine changed')
    require(patched[0x9383:0x938b] == bytes.fromhex('29c81039e08a0013'), 'Opening allowance changed')
    require(patched[0x1c459:0x1c45b] == bytes.fromhex('3028'), 'Startup attempt limit changed')
    require(patched[0x6e25:0x6e27] == bytes.fromhex('3038'), 'Special startup seed changed')

    changed = [hex(i) for i, (a, b) in enumerate(zip(original, patched)) if a != b]
    manifest = json.loads((ROOT / 'DTX9003.json').read_text())
    require(manifest['firmware_version'] == '2.42', 'Wrong manifest version')
    require(manifest['source'] == str(SOURCE) and manifest['output'] == str(ROOT / 'DTX9003.uc3'),
            'Wrong manifest paths')
    require(manifest['source_sha256'] == SOURCE_SHA256 and manifest['output_sha256'] == sha(patched),
            'Manifest hash mismatch')
    require(manifest['size'] == len(patched) and manifest['changed_byte_offsets'] == changed,
            'Manifest size/diff mismatch')
    require(manifest['original_crc32'] == hex(zlib.crc32(original[25:])) and
            manifest['patched_crc32'] == hex(zlib.crc32(patched[25:])), 'Manifest CRC mismatch')
    require(len(manifest['patches']) == len(replacements), 'Wrong manifest patch count')
    for record, (offset, before, after) in zip(manifest['patches'], replacements):
        require(int(record['file_offset'], 16) == offset and int(record['address'], 16) == offset + DELTA
                and record['before'] == before.hex() and record['after'] == after.hex(),
                'Manifest patch record mismatch')

    extra_entries = []
    if update_dir is not None:
        update_dir = Path(update_dir)
        extra_entries = sorted(p.name for p in update_dir.iterdir()
                               if p.name not in {'DTX9003.uc3', 'license.key'})
        if strict_package:
            require(not extra_entries, 'Update folder must contain exactly the two required files')
        for name, data in [('DTX9003.uc3', patched), ('license.key', license_bytes)]:
            target = update_dir / name
            require(target.is_file() and not target.is_symlink(), 'Update entry is not a regular file')
            require(target.read_bytes() == data, 'Update copy differs: ' + name)

    return dict(status='PASS', firmware_version='2.42', rendered_version=label.decode('ascii'),
                source_sha256=SOURCE_SHA256, output_sha256=sha(patched), size=len(patched),
                crc32='{:08X}'.format(zlib.crc32(patched[25:])), changed_byte_count=len(changed),
                license_sha256=sha(license_bytes), supplied_license_matches_source=True,
                update_wrapper_preserved=True, only_approved_bytes_changed=True,
                normal_startup_attempts=3, original_motor_and_startup_bytes_preserved=True,
                update_dir=str(update_dir) if update_dir is not None else None,
                update_files_match=update_dir is not None,
                extra_entries=extra_entries, strict_package=strict_package,
                validation_scope='Static bytes, instruction fields, Info call and package integrity',
                bootloader_acceptance_verified=False, hardware_execution=False,
                persistence_verified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--update-dir', type=Path, help='Compare firmware and license on a USB drive or in a package folder')
    parser.add_argument('--strict-package', action='store_true', help='Also reject extra entries in the package folder')
    args = parser.parse_args()
    try:
        result = verify(args.update_dir, args.strict_package)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit('FAIL: ' + str(error))
    report = json.dumps(result, indent=2) + '\n'
    (ROOT / 'verification.json').write_text(report)
    print(report, end='')


if __name__ == '__main__':
    main()
