# Third-party materials

The MIT license covers this project's original scripts, documentation, and header artwork. It does not grant rights to third-party materials embedded in or supplied with this research.

| Materials | Attribution / scope |
| --- | --- |
| `Ecoheat_v1.72/DTX9003.uc3`, `DTX9003 v1.73/DTX9003.uc3` | Ekoheat/Ekopower controller firmware; respective rights holders retain ownership. |
| `analysis/patched/**/*.uc3` | Derivatives of vendor firmware; the project's MIT license does not relicense the underlying firmware. |
| Decompiled vendor routines, disassembly, firmware strings, extracted bitmap previews | Derived from the analyzed firmware; underlying code and artwork retain their owners' rights. |
| `docs/ekoheat_series.pdf`, `docs/ekopower ekoheat installation manual 2 2014 eng.pdf` | Supplied Ekoheat/Ekopower manuals; retain their original notices. |
| `docs/WNSTS00019-1.pdf` | Winstar Display Co., Ltd. display specification; retains its original notices. |

These materials were supplied with the local research project. Their inclusion does not establish permission to redistribute them or use the vendor's trademarks. This repository does not claim ownership of them.

Ghidra's native source/build is excluded from Git. The disassembler helper uses the upstream Ghidra SLEIGH API; obtain Ghidra and its license notices from [the official project](https://github.com/NationalSecurityAgency/ghidra).

Activation files named `license.key` are excluded from version control. Use your own appropriate activation file if required by your controller; no activation bypass is provided.
