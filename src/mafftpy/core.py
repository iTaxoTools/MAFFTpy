#-----------------------------------------------------------------------------
# MAFFTpy - Multiple sequence alignment with MAFFT
# Copyright (C) 2021  Patmanidis Stefanos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------


from multiprocessing import Process

import tempfile
import shutil
import pathlib
from datetime import datetime

from . import mafft
from . import param
from . import params

class MultipleSequenceAlignment():
    """
    Container for input/output of MAFFT core.
    """

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state

    def __init__(self, file):
        """
        """
        self.file = file
        self.useLogfile = False
        self.target = None
        self.results = None
        # self.time_format = '%x - %I:%M%p'
        self.time_format = '%FT%T'
        self.param = param.ParamList(params.params)

    def fetch(self, destination):
        """
        Copy results as a new directory.
        """
        if self.results is None:
            raise RuntimeError('No results to fetch.')
        shutil.copytree(self.results, destination)

    def run(self):
        """
        Run the MAFFT core with given params,
        save results to a temporary directory.
        """
        kwargs = self.param.as_dictionary()
        kwargs['file'] = self.file
        kwargs['logfile'] = self.useLogfile
        kwargs['time'] = datetime.now().strftime(self.time_format)
        if self.target is not None:
            kwargs['out'] = self.target
        print(kwargs)
        mafft.main(kwargs)
        self.results = self.target

    def launch(self):
        """
        Should always use a seperate process to launch the MAFFT core,
        since it uses exit(1) and doesn't always free allocated memory.
        Save results on a temporary directory, use fetch() to retrieve them.
        """
        # When the last reference of TemporaryDirectory is gone,
        # the directory is automatically cleaned up, so keep it here.
        self._temp = tempfile.TemporaryDirectory(prefix='mafft_')
        self.target = pathlib.Path(self._temp.name).as_posix()
        p = Process(target=self.run)
        p.start()
        p.join()
        if p.exitcode != 0:
            raise RuntimeError('MAFFT internal error, please check logs.')
        # Success, update analysis object for parent process
        self.results = self.target
