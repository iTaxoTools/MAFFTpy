"""Console entry points"""

import argparse
from pathlib import Path

from . import core


def parse_arguments(ask_strategy: bool = False):
    #! This should be expanded to accept all arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    if ask_strategy:
        strategies = ["auto", "ginsi", "fftns1"]
        parser.add_argument("--strategy", type=str, choices=strategies, default="auto")
    parser.add_argument("--adjustdirection", action="store_true")
    parser.add_argument("--adjustdirectionaccurately", action="store_true")
    kwargs = vars(parser.parse_args())
    input = kwargs.pop("input")
    output = kwargs.pop("output")
    return input, output, kwargs


def auto():
    input, output, kwargs = parse_arguments()
    core.auto(input, output, **kwargs)


def ginsi():
    input, output, kwargs = parse_arguments()
    core.ginsi(input, output, **kwargs)


def fftns1():
    input, output, kwargs = parse_arguments()
    core.fftns1(input, output, **kwargs)


def main():
    input, output, kwargs = parse_arguments(ask_strategy=True)
    core.quick(input, output, **kwargs)


if __name__ == "__main__":
    main()
