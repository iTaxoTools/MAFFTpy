# MAFFTpy

Multiple sequence alignment.

This is a Python wrapper for MAFFT: <https://mafft.cbrc.jp/alignment/software/>

## Quick start

*(you will need a C compiler when building from source)*

Install using pip, then run the GUI:

```
$ pip install . -f packages.html
$ mafftpy-gui
```

Simple command line tools:

```
$ mafftpy-fftns1 tests/sample
$ mafftpy-ginsi tests/sample
```

## Building on Windows

You must have Git and MS Visual Studio 2019 installed.
The Windows version depends on the open pthread-win32 library,
which is included as a git submodule. Setuptools will automatically
fetch and compile the library.

## Packaging

It is advised to do this inside a virtual environment
using a tool such as pipenv:

```
$ pipenv shell
$ pip install ".[dev]" -f packages.html
$ pyinstaller scripts/mafftpy.spec
```
