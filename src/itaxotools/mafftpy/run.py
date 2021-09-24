
"""Console entry points"""

import sys
from . import core

#! This should be expanded to accept all arguments
def main():
    """Anayze given file"""
    if len(sys.argv) >= 2:
        input = sys.argv[1]
        save = sys.argv[2] if len(sys.argv) >= 3 else None
        a = core.quick(input, save)
    else:
        print('Usage: mafftpy INPUT_FILE [SAVE_FILE]')
        print('Ex:    mafftpy tests/sample')

def ginsi():
    if len(sys.argv) >= 2:
        input = sys.argv[1]
        save = sys.argv[2] if len(sys.argv) >= 3 else None
        a = core.ginsi(input, save)
    else:
        print('Usage: mafftpy-ginsi INPUT_FILE [SAVE_FILE]')
        print('Ex:    mafftpy-ginsi tests/sample')

def fftns1():
    if len(sys.argv) >= 2:
        input = sys.argv[1]
        save = sys.argv[2] if len(sys.argv) >= 3 else None
        a = core.fftns1(input, save)
    else:
        print('Usage: mafftpy-fftns1 INPUT_FILE [SAVE_FILE]')
        print('Ex:    mafftpy-fftns1 tests/sample')
