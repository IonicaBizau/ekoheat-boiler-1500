#!/usr/bin/env python3
"""Keep the v1.73 screen awake and allow 30 extra seconds for ash-plate opening."""
import patch_firmware as patch
from pathlib import Path

patch.SOURCE = Path('DTX9003 v1.73/DTX9003.uc3')
patch.OUTPUT = Path('analysis/patched/v1.73.42/DTX9003.uc3')
patch.EXPECTED_SHA256 = 'e57bb9517c66e8f37ecb864daca5735bc14e3ef6a2614c94a962dc62809f2e3a'
patch.FIRMWARE_VERSION = "1.73.42"
patch.PATCHES = [
    (0x80015130, b'v%d.%02d  %s\0\0\0\0'.hex(),
     b'v%d.%02d.42 %s\0\0'.hex(), 'Display custom firmware revision .42; preserve build date'),
    (0x8000ba8e, '3008', '3648',
     'Idle expiry: MOV R8,0 -> MOV R8,100; retain active display brightness'),
    (0x8001136a, '29c81039e08a0013', 'f0c8fed41238c122',
     'Opening check: add 300 instead of 100; swap comparison and use unsigned short branch to same target'),
]

if __name__ == '__main__':
    patch.main()
