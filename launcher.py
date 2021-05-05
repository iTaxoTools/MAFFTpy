#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Executable for PyInstaller
$ python pyinstaller launcher.specs
"""

import sys
import multiprocessing
import src.mafftpy.qt

if __name__ == '__main__':
    multiprocessing.freeze_support()
    src.mafftpy.qt.main.show()
