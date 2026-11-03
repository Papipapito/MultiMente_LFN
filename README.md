# MM_LFN — long file names for Multi Mente (MSX)

An unofficial patch that makes **Multi Mente 2.07_A** (`MM.COM`, by MOGU) show **long file names** (VFAT, the
ones you see in Windows) instead of `METALG~1.ROM`. [Versión en castellano](LEEME.md).

```
before:   ALESTE~1.ROM    FRAY2-~5.ROM    GOLVEL~5.ROM    KING'S~9.ROM    METALG~5.ROM
after:    Aleste 1 - E>   Fray 2 - Ver>   Golvellius 3>   King's Valle>   Metal Gear 3>
```

- **In the list**, each slot shows the first 12 characters of the long name (a `>` marks that it goes on).
- **In File info**, the *Name:* field shows the whole long name (up to 31 characters).
- Files without a long name show their 8.3 name as always.

## Apply it

You need your own copy of the original **Multi Mente 2.07_A** `MM.COM` (23,539 bytes, sha1
`db7316e2b8f17deb1c34df909e2b8da8133e1601`). It is **not** included here. Pick any of these:

1. **Web page, nothing to install:** open [`aplicar.html`](aplicar.html) in a browser and drop your `MM.COM` on it.
   It runs in your browser; the file is not uploaded anywhere.
2. **Python 3:** `python aplicar.py MM.COM` → writes `MM_LFN.COM` next to it.
3. **Any IPS patcher** (Floating IPS, Lunar IPS…): apply [`MM_LFN.ips`](MM_LFN.ips) to `MM.COM`. IPS patchers do
   not check the source file, so check the sha1 above first.

Then copy the result to the card as `MM.COM`, in the Multi Mente folder (next to `MM.EXE` and `MM.CFG`).
`aplicar.py` and `aplicar.html` refuse any file that is not exactly the original (sha1 check), and check the sha1 of
the result (`479dade9e4d01e6477d9f07e29a0e7d5aa0e6911`, 25,673 bytes).

## Requirements and limits

- **Nextor 2.1 or 3.0**, FAT16 or FAT12 (Nextor does not read FAT32). With another DOS, or if anything fails, you
  just see the 8.3 names.
- **View only.** Copy, move, rename and delete work as before, on the 8.3 name; what MM copies or creates gets no
  long name. Sorting sorts by the 8.3 name.
- ASCII only: accented Latin letters show without the accent, anything else as `?`.
- Needs a free mapper segment (a 256 KB mapper or bigger) and room at the top of the TPA (≥ `D3EBh`; Nextor 2.1.4
  leaves `D806h`, Nextor 3.0 `D706h`). If either is missing, the list stays in 8.3 and only File info shows the
  long name.
- Entering a folder takes a little longer (about +0.9 s for 200 files with long names in openMSX); moving the
  cursor does not read the disk.
- Tested in openMSX (Philips NMS 8245, 4 MB, Sunrise IDE) with Nextor 2.1.4 and 3.0.0 beta 2. The details, with the
  list of what was tried, are in [docs/TECNICO.md](docs/TECNICO.md) (Spanish).

## Rebuild

The patch is hand-written Z80 (`src/mmlfn.asm`) over the disassembly of the binary. With
[pasmo](http://pasmo.speccy.org/) (or WSL on Windows) and the original `MM.COM` in `original/`:

```
python tools/hacer_parche.py     # builds MM_LFN.ips, aplicar.py and aplicar.html
python tests/probar.py           # checks the three ways of applying it (node is optional)
```

## About Multi Mente and this patch

Multi Mente is the work of MOGU. This repository is an unofficial add-on and is not endorsed by the author. It
contains **none of Multi Mente's code**: `MM_LFN.ips` holds only the new bytes (about 2.4 KB), and the tools check
that every byte of the patch differs from the original at its place. You must supply your own `MM.COM`. If the author
or any rights holder objects, tell us and it will be taken down.

The code in this repository (the patch source and the tools) is under the GNU GPL v3, see [LICENSE](LICENSE).
