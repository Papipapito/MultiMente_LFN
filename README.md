# MM_LFN — long file names for Multi Mente (MSX)

An unofficial patch that makes **Multi Mente** (`MM.COM`, by MOGU) show **long file names** (VFAT, the ones you see
in Windows) instead of `METALG~1.ROM`. It fits two builds: the original **2.07_A** and the community build
**2.07A+ RC5** (FAT16 and Y2K fixes). [Versión en castellano](LEEME.md).

```
before:   ALESTE~1.ROM    FRAY2-~5.ROM    GOLVEL~5.ROM    KING'S~9.ROM    METALG~5.ROM
after:    Aleste 1 - E>   Fray 2 - Ver>   Golvellius 3>   King's Valle>   Metal Gear 3>
```

- **In the list**, each slot shows the first 12 characters of the long name (a `>` marks that it goes on).
- **In File info**, the *Name:* field shows the whole long name (up to 31 characters).
- Files without a long name show their 8.3 name as always.

## Apply it

You need your own copy of the original `MM.COM` of one of these versions. They are **not** included here:

| Version | `MM.COM` | sha1 | Result |
| --- | --- | --- | --- |
| 2.07_A | 23,539 bytes | `db7316e2b8f17deb1c34df909e2b8da8133e1601` | 25,673 bytes, `479dade9e4d01e6477d9f07e29a0e7d5aa0e6911` |
| 2.07A+ RC5 | 23,552 bytes | `09c4a6b4f6fa4db19e94fa08fdcba0da2a3c29d0` | 25,673 bytes, `5b97f818fc2496069c4aeef4e9cfcf2688dfe2bd` |

The RC5 is the "MultiMente v2.07A+ RC5" build published on the MSX Resource Center downloads. In its zip, the English
`MM.COM` is the one in the root of the inner `MMv2.07Aplus-RC5.zip` (not the one in `Japanese\`). Use the `MM.EXE`
that comes with your `MM.COM`; the patch does not touch it.

Pick any of these:

1. **Web page, nothing to install:** open [the online patcher](https://papipapito.github.io/MultiMente_LFN/aplicar.html)
   (or the downloaded [`aplicar.html`](aplicar.html)) in a browser and drop your `MM.COM` on it. It runs in your
   browser; the file is not uploaded anywhere.
2. **Python 3:** `python aplicar.py MM.COM` → writes `MM_LFN.COM` next to it.
3. **Any IPS patcher** (Floating IPS, Lunar IPS…): apply [`MM_LFN.ips`](MM_LFN.ips) (2.07_A) or
   [`MM_LFN_RC5.ips`](MM_LFN_RC5.ips) (RC5) to `MM.COM`. IPS patchers do not check the source file, so check the
   sha1 above first.

Then copy the result to the card as `MM.COM`, in the Multi Mente folder (next to `MM.EXE` and `MM.CFG`).
`aplicar.py` and `aplicar.html` recognise the version by its sha1, refuse any file that is not exactly an original, and
check the sha1 of the result.

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
- Multi Mente's own limits stay: the 2.07A+ RC5 manual says not to use Sort or the Filer on FAT16 and that
  "wr[Y]ting" is ignored there.
- Tested only in openMSX (Philips NMS 8245, 4 MB, Sunrise IDE, FAT16 image): 2.07_A with Nextor 2.1.1, 2.1.4 and
  3.0.0 beta 2; RC5 with Nextor 2.1.1 and 2.1.4 (not tried with Nextor 3.0 yet). Both builds: list, File info, sort,
  mark, enter folders, come back from `[X]ecom` programs, delete, copy, and `CS MM` (the patched file is about 2.1 KB
  longer, and CS edits only the settings block). Not tried on real hardware. The details, with the list of what was
  tried, are in [docs/TECNICO.md](docs/TECNICO.md) (Spanish).

## Rebuild and test

The patch is hand-written Z80 (`src/mmlfn.asm`) over the disassembly of the binary. With
[pasmo](http://pasmo.speccy.org/) (or WSL on Windows) and the originals in `original/` (`MM.COM` for 2.07_A,
`MM_RC5.COM` for the RC5):

```
python tools/hacer_parche.py     # builds the .ips files, aplicar.py and aplicar.html
python tests/probar.py           # checks the three ways of applying it (node is optional)
```

`tests/openmsx/probar_mm.py` runs a patched `MM.COM` inside openMSX (Nextor on a Sunrise IDE, an FAT16 image with
long-name files) and takes screenshots of the list and File info; see its header for the options. It needs
openMSX, the system ROMs and your own MSX-DOS 2 files, none of which are in this repository.

## About Multi Mente and this patch

Multi Mente is the work of MOGU. This repository is an unofficial add-on and is not endorsed by the author. It
contains **none of Multi Mente's code**: the `.ips` files hold only the new bytes (about 2.4 KB each) and the tools
check that every byte of the patch differs from the original at its place. You must supply your own `MM.COM`. If the
author or any rights holder objects, tell us and it will be taken down.

The code in this repository (the patch source and the tools) is under the GNU GPL v3, see [LICENSE](LICENSE).
