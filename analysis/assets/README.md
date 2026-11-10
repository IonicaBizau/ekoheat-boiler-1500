# Extracted boiler logos

I found both display logos stored as uncompressed images in the firmware. All 23 images in the bitmap pointer table at `0x8004F954` were extracted into PNG previews by `../tools/extract_bitmaps.py`.

| Use | Bitmap index | Dimensions | Machine address | File offset | Pixel bytes |
| --- | --- | --- | --- | --- | --- |
| Startup/loading screen logo | 7 | 227 × 44 | `0x80040C4C` | `0x38C65` | 19976 |
| Runtime top-left logo | 11 | 130 × 25 | `0x8004764C` | `0x3F665` | 6500 |

Each asset consists of two little-endian 16-bit dimensions followed by row-major, little-endian RGB565 pixels. There is no image compression. White is part of the existing image; transparency is a renderer parameter, not an alpha channel.

## Evidence for placement

Screen pointer table: `0x800397A4`.

- Screen 11, used by the GUI during startup at `0x8001E7E8`, points to `0x8002CFEC` (file `0x25005`). Its image widget references bitmap 7. The record begins `0a 50 0f 80 00 00 00 00 a0 00 47 00 e2 00 2b 00 07 00`.
- Screen 21, rendered by the runtime main-screen routine `0x800165C8`, points to `0x8002D72C` (file `0x25745`). Its first image widget references bitmap 11, at `(5,2)`, with inclusive bounds 129 × 24 (130 × 25 pixels). The record begins `0a 50 0f 00 00 00 00 00 05 00 02 00 81 00 18 00 0b 00`.
- Widget drawing routine `0x80058D4C`, cases 10 and 18, calls `0x80054884` with the bitmap index.
- `0x80054884` resolves the index through the bitmap pointer table and calls `0x800508BC`.
- `0x800508BC` reads little-endian width and height from the first four bytes, then copies two-byte pixel values while swapping byte order for the framebuffer.

The corresponding native Ghidra decompilations are in `../ghidra/decompiled/`.

## Replacing the logos

Same-size artwork can replace each pixel payload without moving code, image pointers, or screen resources. Convert the artwork to RGB565, preserve each four-byte dimension header, and recalculate the firmware payload CRC32 at header offset `0x15`.

I have not replaced the logos. The current project keeps only the original 1.72/1.73 images and their clock-only derivatives; a logo change would need a separate, verified build.

Open `index.html` to view all extracted assets. `bitmaps.json` contains dimensions and offsets. The contact sheet clips wide images; individual PNG previews contain the entire images.
