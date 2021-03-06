#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Launch the mafftpy GUI"""

import multiprocessing
from itaxotools.mafftpy.gui import run

if __name__ == '__main__':
    multiprocessing.freeze_support()
    run()
