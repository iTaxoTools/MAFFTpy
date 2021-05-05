#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Console entry point"""

import sys
from . import core

#! This should be expanded to accept all arguments
def main():
    """Anayze given file"""
    if len(sys.argv) == 2:
        print(' ')
        a=core.MultipleSequenceAlignment(sys.argv[1])
        a.launch()
    else:
        print('Usage: mafftpy FILE')
        print('Ex:    mafftpy tests/sample')
