
"""Console entry points"""

import sys
from pathlib import Path
from . import core
import argparse

def default_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument("input", type=Path)
	parser.add_argument("save", type=Path, nargs="?")
	parser.add_argument("--adjustdirection", action="store_true")
	parser.add_argument("--adjustdirectionaccurately", action="store_true")
	return parser

#! This should be expanded to accept all arguments
def main():
	"""Analyze given file"""
	parser = default_parser()
	args = parser.parse_args()
	a = core.quick(args)

def ginsi():
	parser = default_parser()
	args = parser.parse_args()
	a = core.ginsi(args)

def fftns1():
	parser = default_parser()
	args = parser.parse_args()
	a = core.fftns1(args)
