"""Console entry points"""

import argparse
from pathlib import Path

from . import core


def parse_arguments():
    #! This should be expanded to accept all arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--adjustdirection", action="store_true")
    parser.add_argument("--adjustdirectionaccurately", action="store_true")
    kwargs = vars(parser.parse_args())
    input = kwargs.pop("input")
    output = kwargs.pop("output")
    return input, output, kwargs


def main():
    input, output, kwargs = parse_arguments()
    core.quick(input, output, strategy="auto", **kwargs)


def ginsi():
    input, output, kwargs = parse_arguments()
    core.quick(input, output, strategy="ginsi", **kwargs)


def fftns1():
    input, output, kwargs = parse_arguments()
    core.quick(input, output, strategy="fftns1", **kwargs)
