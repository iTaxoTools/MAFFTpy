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
import re
import os
import sys
from datetime import datetime
from contextlib import contextmanager

from . import mafft
from . import param
from . import params


@contextmanager
def pushd(target):
    """Temporarily change directory"""
    re = os.getcwd()
    os.chdir(target)
    try:
        yield
    finally:
        os.chdir(re)

@contextmanager
def _redirect(stream='stdout', dest=None):
    """Redirect system stream to file stream"""
    # High-level redirection
    original = getattr(sys, stream)
    original.flush()
    setattr(sys, stream, dest)
    # Low-level redirection
    duplicate = os.dup(original.fileno())
    os.dup2(dest.fileno(), original.fileno())
    try:
        yield dest
    finally:
        # Restore stream
        os.dup2(duplicate, original.fileno())
        dest.flush()
        setattr(sys, stream, original)

@contextmanager
def redirect(stream='stdout', dest=None, mode='w'):
    """
    Redirect system stream according to `dest`:
    - If None: Do nothing
    - If String: Open file and redirect
    - Else: Assume IOWrapper, redirect
    """
    if dest is None:
        yield getattr(sys, stream)
    elif isinstance(dest, str):
        with open(dest, mode) as file, _redirect(stream, file) as f:
            yield f
    else:
        with _redirect(src, tar) as f:
            yield f


class MafftVars():
    """Variables used by MAFFT core"""
    def __init__(self, params=None):
        """As defined in the mafft bash script"""
        self.defaultiterate = 0
        self.defaultcycle = 2
        self.defaultgop = "1.53"
        # self.defaultaof = "0.123"
        self.defaultaof = "0.000"
        self.defaultlaof = "0.100"
        self.defaultlgop = "-2.00"
        self.defaultfft = 1
        self.defaultrough = 0
        self.defaultdistance = "ktuples"
        # self.defaultdistance = "local"
        self.defaultweighti = 2.7
        self.defaultweightr = "0.0"
        self.defaultweightm = "1.0"
        self.defaultdafs = 0
        self.defaultmccaskill = 0
        self.defaultcontrafold = 0
        self.defaultalgopt = "  "
        self.defaultalgoptit = "  "
        self.defaultsbstmodel = " -b 62 "
        self.defaultfmodel = " "
        self.defaultkappa = " "

        self.outputfile = ""
        self.namelength = -1
        self.anysymbol = 0
        self.parallelizationstrategy = "BAATARI2"
        self.kappa = self.defaultkappa
        self.sbstmodel = self.defaultsbstmodel
        self.fmodel = self.defaultfmodel
        self.nmodel = " "
        self.gexp = 0
        self.gop = self.defaultgop
        self.gopdist = self.defaultgop
        self.aof = self.defaultaof
        self.cycle = self.defaultcycle
        self.iterate = self.defaultiterate
        self.fft = self.defaultfft
        self.rough = self.defaultrough
        self.distance = self.defaultdistance
        self.forcefft = 0
        self.memopt = " "
        self.weightopt = " "
        self.GGOP = "-6.00"
        self.LGOP = "-6.00"
        self.LEXP = "-0.000"
        self.GEXP = "-0.000"
        self.lgop = self.defaultlgop
        self.lexp = "-0.100"
        self.laof = self.defaultlaof
        self.pggop = "-2.00"
        self.pgexp = "-0.10"
        self.pgaof = "0.10"
        self.rgop = "-1.530"
        self.rgep = "-0.000"
        self.seqtype = "  "
        self.weighti = self.defaultweighti
        self.weightr = self.defaultweightr
        self.weightm = self.defaultweightm
        self.rnaalifold = 0
        self.dafs = self.defaultdafs
        self.mccaskill = self.defaultmccaskill
        self.contrafold = self.defaultcontrafold
        self.progressfile = "/dev/stderr"
        self.anchorfile = "/dev/null"
        self.anchoropt = ""
        self.maxanchorseparation = 1000
        self.debug = 0
        self.sw = 0
        self.algopt = self.defaultalgopt
        self.algoptit = self.defaultalgoptit
        # self.algspecified = 0
        self.pairspecified = 0
        self.scorecalcopt = " "
        self.coreout = 0
        self.corethr = "0.5"
        self.corewin = "100"
        self.coreext = " "
        self.outputformat = "pir"
        self.f2clext = "-N"
        self.outorder = "input"
        self.seed = "x"
        self.seedtable = "x"
        self.auto = 0
        self.groupsize = -1
        self.partsize = 50
        self.partdist = "ktuples"
        self.partorderopt = " -x "
        self.treeout = 0
        self.nodeout = 0
        self.distout = 0
        self.distoutopt = " "
        self.treein = 0
        self.topin = 0
        self.treeinopt = "  "
        self.seedfiles = "/dev/null"
        self.seedtablefile = "/dev/null"
        self.pdblist = "/dev/null"
        self.ownlist = "/dev/null"
        self.strdir = "$PWD"
        self.scorematrix = "/dev/null"
        self.textmatrix = "/dev/null"
        self.treeinfile = "/dev/null"
        self.rnascoremtx = " "
        self.laraparams = "/dev/null"
        self.foldalignopt = " "
        self.treealg = " -X 0.1 "
        self.sueff = "1.0"
        self.maxambiguous = "1.0"
        self.scoreoutarg = " "
        self.numthreads = 0
        self.numthreadsit = -1
        self.numthreadstb = -1
        self.randomseed = 0
        self.addfile = "/dev/null"
        self.addarg0 = " "
        self.addarg = " "
        self.addsinglearg = " "
        self.add2ndhalfarg = " "
        self.mapoutfile = "/dev/null"
        self.fragment = 0
        self.legacygapopt = " "
        self.oneiterationopt = " "
        self.mergetable = "/dev/null"
        self.mergearg = " "
        self.seedoffset = 0
        self.outnum = " "
        self.last_e = 5000
        self.last_m = 3
        self.last_subopt = " "
        self.last_once = " "
        self.adjustdirection = 0
        self.tuplesize = 6
        self.termgapopt = " -O "
        # self.termgapopt = " " # gap/gap ga kakenai node
        self.similarityoffset = "0.0"
        self.unalignlevel = "0.0"
        self.unalignspecified = 0
        self.spfactor = "100.0"
        self.shiftpenaltyspecified = 0
        self.opdistspecified = 0
        self.allowshift = 0
        self.enrich = 0        # ato de kezuru
        self.enrichseq = 0     # ato de kezuru
        self.enrichstr = 0     # ato de kezuru
        self.seektarget = ""   # ato de kezuru
        self.newdash = 0
        self.newdash_originalsequenceonly = 0
        self.exclude_ho = 0
        self.fixthreshold = "0.0"
        self.bunkatsuopt = " "
        self.npickup = 0
        self.minimumweight = "0.00001" # 2016/Mar
        self.usenaivepairscore = None
        self.oldgenafparam = 0
        self.sprigorous = 0
        self.treeext = "none"
        self.initialramusage = "20GB"
        self.focusarg = " "
        self.lhlimit = " "
        self.mpiscript = "/dev/null"

        if params is not None:
            self.update_from_params(params)

    def update_from_params(self, params):
        """Parse params and update variables"""

        d = params.as_dictionary()

        if d['strategy'] == 'ginsi':
            self.fft = 1
            self.cycle = 1
            self.iterate = 1000
            self.distance = "global"
        elif d['strategy'] == 'fftns1':
            self.fft = 1
            self.cycle = 1
            self.distance = "ktuples"


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
        self.target = None
        self.results = None
        self.log = None
        self.params = param.ParamList(params.params)
        self.vars = MafftVars(self.params)

    @staticmethod
    def _vars_to_kwargs(list):
        """Convert strings into kwargs accepted by the module"""
        res = dict()
        for item in list:
            for var in re.finditer('-([\+a-zA-Z])\s*([^-\s]*)?', item):
                key = var.group(1)
                val = None if var.group(2) == '' else var.group(2)
                res[key] = val
        return res

    @staticmethod
    def _trim(file, dest):
        """Copy file while trimming carriage returns"""
        tr = str.maketrans('\r','\n')
        with open(file, 'r') as fin:
            with open(dest, 'w') as fout:
                for line in fin:
                    fout.write(line.translate(tr))

    def fetch(self, destination):
        """Copy results as a new directory"""
        if self.results is None:
            raise RuntimeError('No results to fetch.')
        shutil.copytree(self.results, destination)

    def run(self):
        """
        Run the MAFFT core with given params,
        save results to a temporary directory.
        """

        self.vars.update_from_params(self.params)

        self.vars.progressfile = self.log
        self.vars.infilename = 'infile'
        self._trim(self.file, pathlib.Path(self.target) / self.vars.infilename)

        if self.target is None:
            self._temp = tempfile.TemporaryDirectory(prefix='mafft_')
            self.target = pathlib.Path(self._temp.name).as_posix()

        with pushd(self.target):
            self._script()

    def _script(self):

        v = self.vars

        # if maxambiguous != 1: call filter()

    # cat "$scorematrix"    | tr "\r" "\n" | grep -v "^$" > "$TMPFILE/_aamtx"
    # cat "$mergetable"     | tr "\r" "\n" | grep -v "^$" > "$TMPFILE/_subalignmentstable"
    # cat "$treeinfile"     | tr "\r" "\n" | grep -v "^$" > "$TMPFILE/_guidetree"
    # cat "$seedtablefile"  | tr "\r" "\n" | grep -v "^$" > "$TMPFILE/_seedtablefile"
    # cat "$laraparams"     | tr "\r" "\n" | grep -v "^$" > "$TMPFILE/_lara.params"
    # cat "$pdblist"        | tr "\r" "\n" | grep -v "^$" > "$TMPFILE/pdblist"
    # cat "$ownlist"        | tr "\r" "\n" | grep -v "^$" > "$TMPFILE/ownlist"
    # cat "$anchorfile"     | tr "\r" "\n" | grep -v "^$" > "$TMPFILE/_externalanchors"

        # check that files are ASCII, not utf-16-32

        # do something with seedfiles

        # numthreads = number of cores
        # max 16 and 8 threads for some reason
        v.numthreadstb = v.numthreads
        v.numthreadsit = v.numthreads

        v.nadd = "0"

        # check auto strats here

        # fragments

        v.gopdist = v.gop

        if v.parallelizationstrategy == "BESTFIRST" or v.parallelizationstrategy == "BAATARI0":
            v.iteratelimit=254
        else:
            v.iteratelimit=16
        if v.iterate > v.iteratelimit:
            v.iterate = v.iteratelimit

        v.rnaopt = "  "
        v.rnaoptit = " -F "

        v.model = v.sbstmodel + v.kappa + v.fmodel + v.nmodel

        v.swopt = " "
        v.parttreeoutopt = " "
        v.treeoutopt = " "

        if v.cycle == 0:
            if v.nodeout == 1:
                v.treeoutopt = "-^ -T"
            else:
                v.treeoutopt = "-t -T"
            v.iterate = 0
            v.weighti = "0.0"
            if v.treeout == 1:
                v.parttreeoutopt = "-t"
                v.groupsize = 1
            else:
                v.parttreeoutopt = " "
            if distout == 1:
                v.distoutopt = "-y -T"
                if v.treeout == 0:
                    v.treeoutopt = ""
        else:
            if v.nodeout == 1:
                if v.iterate > 0:
                    print("The --nodeout option supports only progressive method (--maxiterate 0) for now.")
                    return
                v.parttreeoutopt = "-t"
                v.treeoutopt = "-^"
            elif v.treeout == 1:
                v.parttreeoutopt = "-t"
                v.treeoutopt = "-t"
            else:
                v.parttreeoutopt = " "
                v.treeoutopt = " "
            if v.distout == 1:
                v.distoutopt = "-y"

        # check format (>)

        # nseq = number of lines starting with > or =
        v.nseq = 333
        if v.nseq ==2:
            v.cycle = 1
        if v.nseq > 3:
            v.cycle = 3

        if v.nseq > 60000 and v.iterate > 1:
            print("Too many sequences to perform iterative refinement!")
            print("Please use a progressive method.")
            return

        if v.distance == "ktuples":
            # THIS IS CHEATING, setting cycle to 1 for no good reason
            v.cycle = 1

            v.localparam = ""
            v.weighti = 0.0
        else:
            v.localparam = "-l " + str(v.weighti)
            if v.cycle > 1:
                v.cycle = 1

        v.param_fft = " -F "
        v.memsavetree = 0

        v.cycletbfast = 1
        if v.localparam == '' and v.fragment == 0 and v.distance != "parttree":
    #		echo "use disttbfast"
            v.cycletbfast = 1
            v.cycledisttbfast = v.cycle
            if v.cycledisttbfast == 0:
                v.cycledisttbfast = 1
            else:
                #		echo "use tbfast"
                v.cycletbfast = v.cycle
                v.cycledisttbfast = 1

        if v.distance == "global" or v.distance == "distonly":
            v.strategy = "G-"
        elif v.fft == 1:
            v.strategy = "FFT-"
        else:
            v.strategy = "NW-"

        if v.weighti > 0:
            v.strategy += "I"
        v.strategy += "NS-"

        if v.iterate > 0:
            v.strategy += "i"
        else:
            v.strategy += str(v.cycle)

        v.explanation = '?'
        v.performance = 'Not tested.'

        v.outputopt = "-f"

        if v.distance == "global" and v.memsavetree == 0:
            with redirect('stdout', os.devnull, 'w'), \
                 redirect('stderr', v.progressfile, 'a'):
            # if True:
                mafft.tbfast(
                        i = v.infilename,
                        pair = dict(
                            i = v.infilename,
                            u = v.unalignlevel,
                            C = v.numthreads,
                            g = v.pgexp,
                            f = v.pggop,
                            Q = v.spfactor,
                            h = v.pgaof,
                            A = v.usenaivepairscore,
                            **self._vars_to_kwargs([
                                v.localparam,
                                v.seqtype,
                                v.model,
                                v.focusarg,
                            ]),
                        ),
                        W = v.minimumweight,
                        V = '-' + v.gopdist,
                        s = v.unalignlevel,
                        C = v.numthreadstb,
                        f = '-' + v.gop,
                        Q = v.spfactor,
                        h = v.aof,
                        **self._vars_to_kwargs([
                            '-+ ' + str(v.iterate),
                            v.legacygapopt,
                            v.mergearg,
                            v.outnum,
                            v.addarg,
                            v.add2ndhalfarg,
                            v.rnaopt,
                            v.weightopt,
                            v.treeinopt,
                            v.treeoutopt,
                            v.distoutopt,
                            v.seqtype,
                            v.model,
                            v.param_fft,
                            v.localparam,
                            v.algopt,
                            v.treealg,
                            v.scoreoutarg,
                            v.focusarg,
                        ])
                    )
            # print('BREAK HERE')
            # return
        else:
            if v.fragment != 0:
                pass
        # "$prefix/addsingle" -Q 100 $legacygapopt -W $tuplesize -O $outnum $addsinglearg $addarg $add2ndhalfarg -C $numthreads $memopt $weightopt $treeinopt $treeoutopt $distoutopt $seqtype $model -f "-"$gop  -h $aof  $param_fft $localparam   $algopt $treealg $scoreoutarg < infile   > /dev/null 2>>"$progressfile" || exit 1
            else:
                with redirect('stdout', 'pre', 'w'), \
                     redirect('stderr', v.progressfile, 'a'):
                    mafft.disttbfast(
                            i = v.infilename,
                            q = v.npickup,
                            E = v.cycledisttbfast,
                            V = '-' + v.gopdist,
                            s = v.unalignlevel,
                            W = v.tuplesize,
                            C = str(v.numthreads) + '-' + str(v.numthreadstb),
                            g = v.gexp,
                            f = '-' + v.gop,
                            Q = v.spfactor,
                            h = v.aof,
                            x = v.maxanchorseparation,
                            **self._vars_to_kwargs([
                                v.legacygapopt,
                                v.mergearg,
                                v.termgapopt,
                                v.outnum,
                                v.addarg,
                                v.add2ndhalfarg,
                                v.memopt,
                                v.weightopt,
                                v.treeinopt,
                                v.distoutopt,
                                v.seqtype,
                                v.model,
                                v.param_fft,
                                v.algopt,
                                v.treealg,
                                v.scoreoutarg,
                                v.anchoropt,
                                v.oneiterationopt,
                            ])
                        )

        # v.progressfile = 'err2.log'

        while v.cycletbfast > 1:
            if v.distance == "parttree":
                pass
                # mv pre infile
                # "$prefix/splittbfast" $legacygapopt -Z $algopt $splitopt $partorderopt $parttreeoutopt $memopt $seqtype $model -f "-"$gop -Q $spfactor -h $aof  -p $partsize -s $groupsize $treealg $outnum -i infile   > pre 2>>"$progressfile" || exit 1
            else:
                # mafft.disttbfast(W=v.minimumweight, V='-'+v.gopdist, s=v.unalignlevel, S=None)
                pass
                # "$prefix/tbfast" -W $minimumweight -V "-"$gopdist -s $unalignlevel $legacygapopt $mergearg $termgapopt $outnum -C $numthreadstb $rnaopt $weightopt $treeoutopt $distoutopt $memopt $seqtype $model  -f "-"$gop -Q $spfactor -h $aof $param_fft  $localparam $algopt -J $treealg $scoreoutarg < pre > /dev/null 2>>"$progressfile" || exit 1
                # fragment>0 no baai, nanimoshinai
                # seed youchuui!!
            v.cycletbfast -= 1

        if v.iterate > 0:
            if v.distance == "ktuples":
                # "$prefix/dndpre" $seqtype $model -M 2 -C $numthreads < pre     > /dev/null 2>>"$progressfile" || exit 1
                pass

            # with redirect(sys.stdout, os.devnull, 'w'), \
            #      redirect(sys.stderr, v.progressfile, 'a'):
            with redirect('stdout', os.devnull, 'w'), \
                 redirect('stderr', v.progressfile, 'a'):
                mafft.dvtditr(
                        i = 'pre',
                        W = v.minimumweight,
                        E = v.fixthreshold,
                        s = v.unalignlevel,
                        C = v.numthreadsit,
                        t = v.randomseed,
                        z = 50,
                        f = '-' + v.gop,
                        Q = v.spfactor,
                        h = v.aof,
                        I = v.iterate,
                        p = v.parallelizationstrategy,
                        K = v.nadd,
                        **self._vars_to_kwargs([
                            v.bunkatsuopt,
                            v.legacygapopt,
                            v.mergearg,
                            v.outnum,
                            v.rnaoptit,
                            v.memopt,
                            v.scorecalcopt,
                            v.localparam,
                            v.seqtype,
                            v.model,
                            v.weightopt,
                            v.treeinopt,
                            v.algoptit,
                            v.treealg,
                            v.scoreoutarg,
                        ])
                    )

        print('Strategy:', v.strategy)
        print('Explanation:', v.explanation)
        print('Performance:', v.performance)

        # call f2cl for windows
        # print file named "pre"

        # if self.target is not None:
        #     kwargs['out'] = self.target
        # mafft.disttbfast(i=self.file)
        self.results = self.target

        print('Results:', self.results)

    def launch(self):
        """
        Should always use a seperate process to launch the MAFFT core,
        as the script uses global I/O redirection, some internal functions
        call exit(), while repeated calls may cause segfaults.
        Save results in a temporary directory, use fetch() to retrieve them.
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

def quick(input=None, save=None, strategy='fftns1'):
    """Quick analysis"""
    a = MultipleSequenceAlignment(input)
    a.params.general.strategy = strategy
    a.launch()
    if save is not None:
        savefile = open(save, 'w')
    else:
        savefile = sys.stdout
    with open(pathlib.Path(a.results) / 'pre') as result:
        print(result.read(), file=savefile)
    if save is not None:
        savefile.close()

def fftns1(input=None, save=None):
    quick(input, save, 'fftns1')

def ginsi(input=None, save=None):
    quick(input, save, 'ginsi')
