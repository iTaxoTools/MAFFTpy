# MAFFTpy

Multiple sequence alignment. This is a Python wrapper for
[MAFFT](https://mafft.cbrc.jp/alignment/software/).

## Executables

Download and run the standalone executables without installing Python.</br>
[See the latest release here.](https://github.com/iTaxoTools/MAFFTpy/releases/latest)

## Installing

Installing from source requires a C++ compiler:

```
$ pip install git+https://github.com/iTaxoTools/MAFFTpy.git
```

### Building on Windows

You must have Git and MS Visual Studio 2019 or later installed.
Please make sure your environment is properly configured to use MSVC.
The Windows version depends on the open
[pthread-win32](https://github.com/GerHobbelt/pthread-win32) library,
which is included as a git submodule. Setuptools will automatically
fetch and compile the library.

## Quick start

Run the GUI:
```
$ mafftpy-gui
```

Simple command line tools:
```
$ mafftpy-fftns1 tests/sample tests/sample.out
$ mafftpy-ginsi tests/sample
```

## Python API

Call the functions from within Python:
```
from itaxotools.mafftpy import quick, fftns1, ginsi
from pathlib import Path

quick(Path('tests/sample'), strategy='auto')
fftns1(Path('tests/sample'), Path('tests/sample.out'))
ginsi(Path('tests/sample'))
```

## Packaging

It is advised to use PyInstaller within a virtual environment:
```
$ pip install ".[dev]" -f packages.html
$ pyinstaller scripts/mafftpy.spec
```
