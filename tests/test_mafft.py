from __future__ import annotations

from pathlib import Path
from typing import Callable, NamedTuple
import difflib

import pytest

from itaxotools.mafftpy import MultipleSequenceAlignment

TEST_DATA_DIR = Path(__file__).parent

"""
Target output files were generated using the following mafft commands (v7.511):

mafft  --retree 1 --inputorder "sample" > "sample.fftns1"
mafft  --retree 1 --inputorder --adjustdirection "sample" > "sample.fftns1.adjustdirection"
mafft  --retree 1 --inputorder --adjustdirectionaccurately "sample" > "sample.fftns1.adjustdirectionaccurately"

mafft  --globalpair --maxiterate 16 --inputorder "sample" > "sample.ginsi"
mafft  --globalpair --maxiterate 16 --inputorder --adjustdirection "sample" > "sample.ginsi.adjustdirection"
mafft  --globalpair --maxiterate 16 --inputorder --adjustdirectionaccurately "sample" > "sample.ginsi.adjustdirectionaccurately"

These were repeated for each sample file.
"""


class MafftTest(NamedTuple):
    input: str
    output: str
    strategy: str
    adjustdirection: int

    def validate(self, tmp_path: Path) -> None:
        a = MultipleSequenceAlignment(TEST_DATA_DIR / self.input)
        a.params.general.strategy = self.strategy
        a.params.general.adjustdirection = self.adjustdirection
        a.launch()

        fixed_path = TEST_DATA_DIR / self.output
        output_path = Path(a.results) / 'pre'
        fixed_text = fixed_path.read_text()
        output_text = output_path.read_text()

        trans = str.maketrans('', '', '\r\n')
        fixed_text = fixed_text.translate(trans)
        output_text = output_text.translate(trans)

        if fixed_text != output_text:
            diff = difflib.unified_diff(
                fixed_text.splitlines(),
                output_text.splitlines()
            )
            print('\n'.join(diff))

        assert fixed_text == output_text


mafft_tests = list()
for sample in ['sample1', 'sample2', 'sample3', 'sample4']:
    mafft_tests.extend([
        MafftTest(f'{sample}/sample', f'{sample}/sample.fftns1', 'fftns1', 0),
        MafftTest(f'{sample}/sample', f'{sample}/sample.fftns1.adjustdirection', 'fftns1', 1),
        MafftTest(f'{sample}/sample', f'{sample}/sample.fftns1.adjustdirectionaccurately', 'fftns1', 2),

        MafftTest(f'{sample}/sample', f'{sample}/sample.ginsi', 'ginsi', 0),
        MafftTest(f'{sample}/sample', f'{sample}/sample.ginsi.adjustdirection', 'ginsi', 1),
        MafftTest(f'{sample}/sample', f'{sample}/sample.ginsi.adjustdirectionaccurately', 'ginsi', 2),
    ])

@pytest.mark.parametrize("test", mafft_tests)
def test_write_sequences(test: MafftTest, tmp_path: Path) -> None:
    test.validate(tmp_path)
