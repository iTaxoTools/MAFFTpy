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


        defaultiterate=0
        defaultcycle=2
        defaultgop="1.53"
        #defaultaof="0.123"
        defaultaof="0.000"
        defaultlaof="0.100"
        defaultlgop="-2.00"
        defaultfft=1
        defaultrough=0
        defaultdistance="ktuples"
        #defaultdistance="local"
        defaultweighti=2.7
        defaultweightr="0.0"
        defaultweightm="1.0"
        defaultdafs=0
        defaultmccaskill=0
        defaultcontrafold=0
        defaultalgopt="  "
        defaultalgoptit="  "
        defaultsbstmodel=" -b 62 "
        defaultfmodel=" "
        defaultkappa=" "

        if True: #ginsi
        	defaultfft=1
        	defaultcycle=1
        	defaultiterate=1000
        	defaultdistance="global"

        if False: #fftns1
        	defaultfft=1
        	defaultcycle=1
        	defaultdistance="ktuples"

        outputfile=""
        namelength=-1
        anysymbol=0
        parallelizationstrategy="BAATARI2"
        kappa=defaultkappa
        sbstmodel=defaultsbstmodel
        fmodel=defaultfmodel
        nmodel=" "
        gexp=0
        gop=defaultgop
        gopdist=defaultgop
        aof=defaultaof
        cycle=defaultcycle
        iterate=defaultiterate
        fft=defaultfft
        rough=defaultrough
        distance=defaultdistance
        forcefft=0
        memopt=" "
        weightopt=" "
        GGOP="-6.00"
        LGOP="-6.00"
        LEXP="-0.000"
        GEXP="-0.000"
        lgop=defaultlgop
        lexp="-0.100"
        laof=defaultlaof
        pggop="-2.00"
        pgexp="-0.10"
        pgaof="0.10"
        rgop="-1.530"
        rgep="-0.000"
        seqtype="  "
        weighti=defaultweighti
        weightr=defaultweightr
        weightm=defaultweightm
        rnaalifold=0
        dafs=defaultdafs
        mccaskill=defaultmccaskill
        contrafold=defaultcontrafold
        progressfile="/dev/stderr"
        anchorfile="/dev/null"
        anchoropt=""
        maxanchorseparation=1000
        debug=0
        sw=0
        algopt=defaultalgopt
        algoptit=defaultalgoptit
        #algspecified=0
        pairspecified=0
        scorecalcopt=" "
        coreout=0
        corethr="0.5"
        corewin="100"
        coreext=" "
        outputformat="pir"
        f2clext="-N"
        outorder="input"
        seed="x"
        seedtable="x"
        auto=0
        groupsize=-1
        partsize=50
        partdist="ktuples"
        partorderopt=" -x "
        treeout=0
        nodeout=0
        distout=0
        treein=0
        topin=0
        treeinopt="  "
        seedfiles="/dev/null"
        seedtablefile="/dev/null"
        pdblist="/dev/null"
        ownlist="/dev/null"
        strdir="$PWD"
        scorematrix="/dev/null"
        textmatrix="/dev/null"
        treeinfile="/dev/null"
        rnascoremtx=" "
        laraparams="/dev/null"
        foldalignopt=" "
        treealg=" -X 0.1 "
        sueff="1.0"
        maxambiguous="1.0"
        scoreoutarg=" "
        numthreads=0
        numthreadsit=-1
        numthreadstb=-1
        randomseed=0
        addfile="/dev/null"
        addarg0=" "
        addarg=" "
        addsinglearg=" "
        add2ndhalfarg=" "
        mapoutfile="/dev/null"
        fragment=0
        legacygapopt=" "
        mergetable="/dev/null"
        mergearg=" "
        seedoffset=0
        outnum=" "
        last_e=5000
        last_m=3
        last_subopt=" "
        last_once=" "
        adjustdirection=0
        tuplesize=6
        termgapopt=" -O "
        #termgapopt=" " # gap/gap ga kakenai node
        similarityoffset="0.0"
        unalignlevel="0.0"
        unalignspecified=0
        spfactor="100.0"
        shiftpenaltyspecified=0
        opdistspecified=0
        allowshift=0
        enrich=0        # ato de kezuru
        enrichseq=0     # ato de kezuru
        enrichstr=0     # ato de kezuru
        seektarget=""   # ato de kezuru
        newdash=0
        newdash_originalsequenceonly=0
        exclude_ho=0
        fixthreshold="0.0"
        bunkatsuopt=" "
        npickup=0
        minimumweight="0.00001" # 2016/Mar
        usenaivepairscore=" "
        oldgenafparam=0
        sprigorous=0
        treeext="none"
        initialramusage="20GB"
        focusarg=" "
        lhlimit=" "
        mpiscript="/dev/null"

        # TMPFILE=`env TMPDIR="$MAFFT_TMPDIR" mktemp -dt "$progname.XXXXXXXXXX"`
        # os.chdir()

        # REMOVE \r from infile

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

        infilename = self.file

        # do something with seedfiles

        # numthreads = number of cores
        # max 16 and 8 threads for some reason
        numthreadstb = numthreads
        numthreadsit = numthreads

        nadd="0"

        # check auto strats here

        # fragments

        gopdist=gop

        if parallelizationstrategy == "BESTFIRST" or parallelizationstrategy == "BAATARI0":
            iteratelimit=254
        else:
            iteratelimit=16
        if iterate > iteratelimit:
            iterate=iteratelimit

        rnaopt="  "
        rnaoptit=" -F "

        model=sbstmodel + kappa + fmodel + nmodel

        swopt=" "
        parttreeoutopt=" "
        treeoutopt=" "

        # check format (>)

        # nseq = number of lines starting with > or =
        nseq = 333
        if nseq ==2:
            cycle = 1
        if nseq > 3:
            cycle = 3

        if nseq > 60000 and iterate > 1:
            print("Too many sequences to perform iterative refinement!")
            print("Please use a progressive method.")
            return

        if distance == "ktuples":
            localparam=""
            weighti=0.0
        else:
            localparam="-l " + str(weighti)
            if cycle > 1:
                cycle = 1

        param_fft=" -F "
        memsavetree=0

        cycletbfast=1
        if localparam=='' and fragment == 0 and distance != "parttree":
    #		echo "use disttbfast"
            cycletbfast=1
            cycledisttbfast=cycle
            if cycledisttbfast == 0:
                cycledisttbfast=1
            else:
                #		echo "use tbfast"
                cycletbfast=cycle
                cycledisttbfast=1

        if distance == "global" or distance == "distonly":
            strategy="G-"
        elif fft == 1:
            strategy="FFT-"
        else:
            strategy="NW-"

        if weighti > 0:
            strategy=strategy+"I"
        strategy=strategy+"NS-"

        if iterate > 0:
            strategy += "i"
        else:
            strategy += str(cycle)

        explanation='?'
        performance='Not tested.'

        outputopt="-f"

        # GOTO 2501 toi finally call the thing!
        if distance == "global" and memsavetree == 0:
                pass
                # "$prefix/tbfast" _  -u $unalignlevel $localparam  -C $numthreads $seqtype $model -g $pgexp -f $pggop -Q $spfactor -h $pgaof  -A  $usenaivepairscore $focusarg  _ -+ $iterate -W $minimumweight -V "-"$gopdist -s $unalignlevel $legacygapopt $mergearg $outnum $addarg $add2ndhalfarg -C $numthreadstb $rnaopt $weightopt $treeinopt $treeoutopt $distoutopt $seqtype $model -f "-"$gop -Q $spfactor -h $aof  $param_fft $localparam   $algopt $treealg $scoreoutarg $focusarg < infile   > /dev/null 2>>"$progressfile" || exit 1
        else:
            if fragment != 0:
                pass
        # "$prefix/addsingle" -Q 100 $legacygapopt -W $tuplesize -O $outnum $addsinglearg $addarg $add2ndhalfarg -C $numthreads $memopt $weightopt $treeinopt $treeoutopt $distoutopt $seqtype $model -f "-"$gop  -h $aof  $param_fft $localparam   $algopt $treealg $scoreoutarg < infile   > /dev/null 2>>"$progressfile" || exit 1
            else:
                pass
        # echo "$prefix/disttbfast" -q $npickup -E $cycledisttbfast -V "-"$gopdist  -s $unalignlevel $legacygapopt $mergearg -W $tuplesize $termgapopt $outnum $addarg $add2ndhalfarg -C $numthreads-$numthreadstb $memopt $weightopt $treeinopt $treeoutopt $distoutopt $seqtype $model -g $gexp -f "-"$gop -Q $spfactor -h $aof  $param_fft $algopt $treealg $scoreoutarg $anchoropt -x $maxanchorseparation $oneiterationopt \< infile   \> pre 2\>\>"$progressfile"
        # "$prefix/disttbfast" -q $npickup -E $cycledisttbfast -V "-"$gopdist  -s $unalignlevel $legacygapopt $mergearg -W $tuplesize $termgapopt $outnum $addarg $add2ndhalfarg -C $numthreads-$numthreadstb $memopt $weightopt $treeinopt $treeoutopt $distoutopt $seqtype $model -g $gexp -f "-"$gop -Q $spfactor -h $aof  $param_fft $algopt $treealg $scoreoutarg $anchoropt -x $maxanchorseparation $oneiterationopt < infile   > pre 2>>"$progressfile" || exit 1
        # mv hat3.seed hat3\

        while cycletbfast > 1:
            if distance == "parttree":
                pass
                # mv pre infile
                # "$prefix/splittbfast" $legacygapopt -Z $algopt $splitopt $partorderopt $parttreeoutopt $memopt $seqtype $model -f "-"$gop -Q $spfactor -h $aof  -p $partsize -s $groupsize $treealg $outnum -i infile   > pre 2>>"$progressfile" || exit 1
            else:
                pass
                # "$prefix/tbfast" -W $minimumweight -V "-"$gopdist -s $unalignlevel $legacygapopt $mergearg $termgapopt $outnum -C $numthreadstb $rnaopt $weightopt $treeoutopt $distoutopt $memopt $seqtype $model  -f "-"$gop -Q $spfactor -h $aof $param_fft  $localparam $algopt -J $treealg $scoreoutarg < pre > /dev/null 2>>"$progressfile" || exit 1
                # fragment>0 no baai, nanimoshinai
                # seed youchuui!!
            cycletbfast -= 1

        if iterate > 0:
            if distance == "ktuples":
                pass
            # "$prefix/dndpre" $seqtype $model -M 2 -C $numthreads < pre     > /dev/null 2>>"$progressfile" || exit 1
        # "$prefix/dvtditr" -W $minimumweight $bunkatsuopt -E $fixthreshold -s $unalignlevel  $legacygapopt $mergearg $outnum -C $numthreadsit -t $randomseed $rnaoptit $memopt $scorecalcopt $localparam -z 50 $seqtype $model -f "-"$gop -Q $spfactor -h $aof  -I $iterate $weightopt $treeinopt $algoptit $treealg -p $parallelizationstrategy  $scoreoutarg  -K $nadd < pre     > /dev/null 2>>"$progressfile" || exit 1

        print(strategy)
        print(explanation)
        print(performance)

        # call f2cl for windows
        # print file named "pre"

        # kwargs = self.param.as_dictionary()
        # kwargs['file'] = self.file
        # kwargs['logfile'] = self.useLogfile
        # kwargs['time'] = datetime.now().strftime(self.time_format)
        # kwargs['a'] = None
        # kwargs['1'] = 2
        kwargs = dict()
        kwargs['-i'] = self.file
        # if self.target is not None:
        #     kwargs['out'] = self.target
        print(kwargs)
        mafft.disttbfast(kwargs)
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
