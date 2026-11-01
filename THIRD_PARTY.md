# Third-party materials

The MIT license covers this project's original scripts, documentation, and header artwork. It does not grant rights to third-party materials embedded in or supplied with this research.

| Materials | Attribution / scope |
| --- | --- |
| `DTX9003 v1.72/DTX9003.uc3`, `DTX9003 v1.73/DTX9003.uc3` | Ekoheat/Ekopower controller firmware; respective rights holders retain ownership. |
| `analysis/patched/**/*.uc3` | Derivatives of vendor firmware; the project's MIT license does not relicense the underlying firmware. |
| Decompiled vendor routines, disassembly, firmware strings, extracted bitmap previews | Derived from the analyzed firmware; underlying code and artwork retain their owners' rights. |
| `docs/ekoheat_series.pdf`, `docs/ekopower ekoheat installation manual 2 2014 eng.pdf` | Supplied Ekoheat/Ekopower manuals; retain their original notices. |
| `docs/WNSTS00019-1.pdf` | Winstar Display Co., Ltd. display specification; retains its original notices. |

I keep these materials here as references for my boiler research. Their inclusion does not establish permission to redistribute them or use the vendor's trademarks. I do not claim ownership of them.

Ghidra's native source/build is excluded from Git. The disassembler helper uses the upstream Ghidra SLEIGH API; obtain Ghidra and its license notices from [the official project](https://github.com/NationalSecurityAgency/ghidra).

The supplied `license.key` files are included alongside each original firmware image. They are vendor activation files, not part of the project's MIT license. Offline analysis and patch generation do not use them.
