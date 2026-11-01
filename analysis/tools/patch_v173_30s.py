#!/usr/bin/env python3
"""Keep v1.73 awake, allow 30 extra opening seconds and five startup attempts."""
import patch_firmware as patch
from pathlib import Path

patch.SOURCE = Path('DTX9003 v1.73/DTX9003.uc3')
patch.OUTPUT = Path('analysis/patched/v2.73/DTX9003.uc3')
patch.EXPECTED_SHA256 = 'e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a'
patch.FIRMWARE_VERSION = "2.73"
patch.PATCHES = [
    (0x80016780, '3018', '3028',
     'Display v2.73: MOV R8,1 -> MOV R8,2 for the major version argument; preserve format and date'),
    (0x8000ba8e, '3008', '3648',
     'Idle expiry: MOV R8,0 -> MOV R8,100; retain active display brightness'),
    (0x8001136a, '29c81039e08a0013', 'f0c8fed41238c122',
     'Opening check: add 300 instead of 100; swap comparison and use unsigned short branch to same target'),
    (0x80024440, '3028', '3048',
     'Startup: compare incremented attempt count with 4 instead of 2; fail after five total attempts'),
    (0x8000ee0c, '3038', '3058',
     'Special startup path: seed count to the new exhausted limit 5 instead of 3; retain failure on its first timeout'),
]

if __name__ == '__main__':
    patch.main()
