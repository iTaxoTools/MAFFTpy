# MAFFTpy

[![PyPI - Version](https://img.shields.io/pypi/v/itaxotools-mafftpy?color=tomato)](
    https://pypi.org/project/itaxotools-mafftpy)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/itaxotools-mafftpy)](
    https://pypi.org/project/itaxotools-mafftpy)
[![GitHub - Tests](https://img.shields.io/github/actions/workflow/status/iTaxoTools/MAFFTpy/test.yml?label=tests)](
    https://github.com/iTaxoTools/MAFFTpy/actions/workflows/test.yml)

Multiple sequence alignment. This is a Python wrapper for
[MAFFT](https://mafft.cbrc.jp/alignment/software/).

The GUI is no longer distributed with this package. For the legacy executables, see below.

## Installation

MAFFTpy is available on PyPI. You can install it through `pip`:

```
pip install itaxotools-mafftpy
```

## Executables

[![Release](https://img.shields.io/badge/v0.1.2-MAFFTpy-tomato?style=for-the-badge)](
    https://github.com/iTaxoTools/MAFFTpy/releases/tag/v0.1.2)
[![Windows](https://img.shields.io/badge/Windows-blue.svg?style=for-the-badge&logo=data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPCEtLSBDcmVhdGVkIHdpdGggSW5rc2NhcGUgKGh0dHA6Ly93d3cuaW5rc2NhcGUub3JnLykgLS0+Cjxzdmcgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiB2ZXJzaW9uPSIxLjEiIHZpZXdCb3g9IjAgMCAxMi43IDEyLjciIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiA8ZyBmaWxsPSIjZmZmIiBzdHJva2UtbGluZWNhcD0ic3F1YXJlIiBzdHJva2Utd2lkdGg9IjMuMTc0OSI+CiAgPHJlY3QgeD0iLjc5MzczIiB5PSIuNzkzNzMiIHdpZHRoPSI1LjAyNyIgaGVpZ2h0PSI1LjAyNyIvPgogIDxyZWN0IHg9IjcuMTQzNiIgeT0iLjc5MzczIiB3aWR0aD0iNC43NjI0IiBoZWlnaHQ9IjUuMDI3Ii8+CiAgPHJlY3QgeD0iLjc5MzczIiB5PSI2Ljg3OSIgd2lkdGg9IjUuMDI3IiBoZWlnaHQ9IjUuMDI3Ii8+CiAgPHJlY3QgeD0iNy4xNDM2IiB5PSI2Ljg3OSIgd2lkdGg9IjQuNzYyNCIgaGVpZ2h0PSI1LjAyNyIvPgogPC9nPgo8L3N2Zz4K)](
    https://github.com/iTaxoTools/MAFFTpy/releases/download/v0.1.2/MAFFTpy-0.1.2-win-x86-64.exe)
[![MacOS](https://img.shields.io/badge/macOS-slategray.svg?style=for-the-badge&logo=apple)](
    https://github.com/iTaxoTools/MAFFTpy/releases/download/v0.1.2/MAFFTpy-0.1.2-macosx-universal2.dmg)

Download and run the legacy executables without installing Python from [the MAFFTpy release page](
    https://github.com/iTaxoTools/MAFFTpy/releases/tag/v0.1.2).

No executables are currently provided for the command-line tool, which is only available after installation.

## Usage

The package comes with a command-line tool:

```
mafftpy examples/brygoo.fas aligned.fas
mafftpy-fftns1 --adjustdirectionaccurately examples/brygoo.fas
```

The following limited features from *MAFFT* are available:
- two strategies: FFT-NS-1 and G-INS-i
- two options: --adjustdirection and --adjustdirectionaccurately

To use the Python API, import `itaxotools.mafftpy.MultipleSequenceAlignment` and use the `start()` method.

## Dependencies

Building from source requires a C++ compiler ([GCC](https://gcc.gnu.org/), [msvc](https://visualstudio.microsoft.com/vs/features/cplusplus/))

In addition, *pthread-win32* is required for Windows and is included as a git submodule.<br>

## Citation

*Katoh, K., Misawa, K., Kuma, K., & Miyata, T. (2002). MAFFT: a novel method for rapid multiple sequence alignment based on fast Fourier transform. Nucleic Acids Research, 30(14), 3059-3066.*
