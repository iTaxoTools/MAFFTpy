# MAFFTpy

Multiple sequence alignment.

This is a Python wrapper for MAFFT: <https://mafft.cbrc.jp/alignment/software/>

## Quick start

*(you will need a C compiler when building from source)*

Install using pip:

```
$ pip install .
```

Run the GUI:

```
$ mafftpy-qt
```

Simple command line tools:

```
$ mafftpy-fftns1 tests/sample
$ mafftpy-ginsi tests/sample
```

## Building on Windows

You must have MS Visual Studio 2019 installed.
The Windows version depends on the open pthread-win32 library,
which is included as a submodule. Make sure to fetch the latest
version before you begin:

```
$ git submodule init
$ git submodule update
```

Setuptools will automatically compile the library. Use the Native Tools
Command Prompt to automatically configure the path and build environment.
Alternatively, run the corresponding batch script before installing.
Please make sure to match the architecture you are compiling for (x64/x86).
Then use setuptools to install as usual:

```
$ "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"
$ pip install .
```

## Packaging

It is advised to do this inside a virtual environment using a tool such as pipenv:

```
$ pipenv shell
$ pip install -e .[dev]
$ pyinstaller scripts/mafftpy.spec
```
