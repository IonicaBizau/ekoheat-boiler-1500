# Reference documents

For the USB preparation, controller menu steps, and checks after updating, see [Updating the boiler software](updating-firmware.md).

| File | Contents | Useful pages |
| --- | --- | --- |
| [Ekoheat series manual](ekoheat_series.pdf) | Boiler installation, operation, and wiring | PDF page 11: ambient thermostat connection described. PDF page 48 / printed page 44: J1 terminals 8–9 labelled TA (air thermostat), with a link shown. |
| [2014 English installation manual](ekopower%20ekoheat%20installation%20manual%202%202014%20eng.pdf) | Earlier controller, setup, maintenance, and updating | Page 12: controller terminal photograph. Page 16: firmware update procedure. |
| [Winstar WNSTS00019-1](WNSTS00019-1.pdf) | WF57ETIBCDD# display specification | Display interface, electrical characteristics, controller and dimensions. |

I kept both boiler manuals because they show different wiring. Check which one matches your controller before using the terminal labels. The series manual's TA terminal mapping has not been traced to firmware GPIO `0x20`, and its electrical input requirements have not been established here.

These are the manuals and datasheet I use as references. Their original ownership and notices still apply; see [THIRD_PARTY.md](../THIRD_PARTY.md).
