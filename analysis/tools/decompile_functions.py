#!/usr/bin/env python3
"""Batch native Ghidra decompiler. Each function gets isolated timeout/error handling."""
import argparse,json,os,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('addresses',nargs='*');p.add_argument('--ghidra',default='/Users/ionicabizau/Downloads/ghidra_12.2_PUBLIC');p.add_argument('--image',default='analysis/ghidra/firmware.xml');p.add_argument('--out',default='analysis/ghidra/decompiled');p.add_argument('--functions',default='analysis/ghidra/functions.json');p.add_argument('--limit',type=lambda x:int(x,0),default=0x80026048);a=p.parse_args()
fs=[int(x,0) for x in a.addresses] if a.addresses else [x for x in json.load(open(a.functions)) if x<a.limit]
out=Path(a.out);out.mkdir(exist_ok=True)
for f in fs:
 target=out/f'{f:08x}.txt'
 if target.exists():continue
 commands=f'load file {a.image}\noption readonly on\nmap function 0x{f:x} FUN_{f:08x}\ndecompile\nprint C\nquit\n'
 try:
  r=subprocess.run(['analysis/ghidra/native-src/decomp_opt'],input=commands,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env={**os.environ,'SLEIGHHOME':a.ghidra},timeout=45)
  target.write_text(r.stdout);print(hex(f),len(r.stdout),flush=True)
 except subprocess.TimeoutExpired:target.write_text('TIMEOUT 45 seconds\n');print(hex(f),'TIMEOUT',flush=True)
