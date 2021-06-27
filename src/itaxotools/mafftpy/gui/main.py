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


from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtStateMachine
from PySide6 import QtGui

import sys
import re
import pickle
import shutil
import pathlib
import tempfile
import importlib.resources

from itaxotools.common.param import qt as param_qt
from itaxotools.common import utility
from itaxotools.common import widgets
from itaxotools.common import resources
from itaxotools.common import io

from .. import core

from time import sleep

_resource_path = importlib.resources.files(resources)
def get_resource(path):
    return str(_resource_path / path)
def get_icon(path):
    return str(_resource_path / 'icons/svg' / path)


class TextEditInput(QtWidgets.QTextEdit):
    def __init__(self, main, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main = main
        self.notifyOnNextUpdate = True
        self.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.setAcceptRichText(False)
        self.setFont(QtGui.QFontDatabase.systemFont(
            QtGui.QFontDatabase.FixedFont))
        self.document().setDocumentMargin(6)
        self.textChanged.connect(self.handleInputChange)
        self.setPlaceholderText(
            "\n"
            "  Please enter the sequences in fasta format:" + "\n\n"
            "    - Open a file, or" + "\n\n"
            "    - Drag and drop a file, or" + "\n\n"
            "    - Paste plain text" + "\n\n"
            "  Then select a strategy and click on \"Run\"."
            )
        self.setStyleSheet("""
            QTextEdit {
                background-color: palette(Base);
                border: 1px solid palette(Mid);
                }
            """)

    def handleInputChange(self):

        if self.document().isEmpty():
            self.main.machine.postEvent(utility.NamedEvent('EMPTY'))
            self.notifyOnNextUpdate = True
        elif self.notifyOnNextUpdate == True:
            self.main.file = None
            self.main.machine.postEvent(utility.NamedEvent('UPDATE'))
            self.notifyOnNextUpdate = False

    def canInsertFromMimeData(self, source):
        if source.hasUrls():
            urls = source.urls()
            if len(urls) > 1:
                return False
            return bool(urls[0].toLocalFile())
        elif source.hasText():
            return True
        else:
            return False

    def insertFromMimeData(self, source):
        if source.hasUrls():
            url = source.urls()[0]
            self.main.handleOpen(fileName=url.toLocalFile())
        elif source.hasText():
            super().insertFromMimeData(source)


class TextEditOutput(QtWidgets.QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.setAcceptRichText(False)
        self.setFont(QtGui.QFontDatabase.systemFont(
            QtGui.QFontDatabase.FixedFont))
        self.document().setDocumentMargin(6)
        self.setReadOnly(True)
        self.setPlaceholderText(
            "\n"
            "  Aligned sequences will be displayed here." + "\n\n"
            )
        self.setStyleSheet("""
            QTextEdit {
                background-color: palette(Base);
                border: 1px solid palette(Mid);
                }
            """)


class TextEditLogger(widgets.TextEditLogger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.document().setDocumentMargin(6)
        self.setStyleSheet("""
            QTextEdit {
                background-color: palette(Base);
                border: 1px solid palette(Mid);
                }
            """)


class Main(widgets.ToolDialog):
    """Main window, handles everything"""

    def __init__(self, parent=None, init=None):
        super(Main, self).__init__(parent)

        self.title = 'MAFFTpy'
        self.analysis = core.MultipleSequenceAlignment()
        self.file = None
        self._temp = None
        self.temp = None

        self.setWindowTitle(self.title)
        self.setWindowIcon(QtGui.QIcon(get_resource('logos/ico/mafft.ico')))
        self.resize(960,540)

        self.process = None
        self.machine = None
        self.skin()
        self.draw()
        self.act()
        self.cog()

        if init is not None:
            self.machine.started.connect(init)


    def __getstate__(self):
        return (self.analysis,)

    def __setstate__(self, state):
        (self.analysis,) = state

    def onReject(self):
        """If running, verify cancel"""
        if self.state['running'] in list(self.machine.configuration()):
            self.handleStop()
            return True
        else:
            return None

    def cog(self):
        """Initialize state machine"""

        self.machine = QtStateMachine.QStateMachine(self)

        self.state = {}
        self.state['idle'] = QtStateMachine.QState(
            QtStateMachine.QState.ChildMode.ParallelStates, self.machine)

        self.state['idle/input'] = QtStateMachine.QState(self.state['idle'])
        self.state['idle/input.none'] = QtStateMachine.QState(self.state['idle/input'])
        self.state['idle/input.file'] = QtStateMachine.QState(self.state['idle/input'])
        self.state['idle/input.raw'] = QtStateMachine.QState(self.state['idle/input'])
        self.state['idle/input.last'] = QtStateMachine.QHistoryState(self.state['idle/input'])
        self.state['idle/input.last'].setDefaultState(self.state['idle/input.none'])
        self.state['idle/input'].setInitialState(self.state['idle/input.none'])

        self.state['idle/output'] = QtStateMachine.QState(self.state['idle'])
        self.state['idle/output.none'] = QtStateMachine.QState(self.state['idle/output'])
        self.state['idle/output.complete'] = QtStateMachine.QState(self.state['idle/output'])
        self.state['idle/output.failed'] = QtStateMachine.QState(self.state['idle/output'])
        self.state['idle/output.updated'] = QtStateMachine.QState(self.state['idle/output'])
        self.state['idle/output.last'] = QtStateMachine.QHistoryState(self.state['idle/output'])
        self.state['idle/output.last'].setDefaultState(self.state['idle/output.none'])
        self.state['idle/output'].setInitialState(self.state['idle/output.none'])

        self.state['running'] = QtStateMachine.QState(self.machine)

        self.machine.setInitialState(self.state['idle'])

        state = self.state['idle']
        state.assignProperty(self.action['run'], 'visible', True)
        state.assignProperty(self.action['stop'], 'visible', False)
        state.assignProperty(self.action['open'], 'enabled', True)
        state.assignProperty(self.subheader, 'enabled', True)
        def onEntry(event):
            self.textInput.setReadOnly(False)
            self.stack.setCurrentWidget(self.textOutput)
        state.onEntry = onEntry

        state = self.state['idle/input.none']
        state.assignProperty(self.action['run'], 'enabled', False)
        state.assignProperty(self.footer, 'text', 'Waiting for sequences.')

        state = self.state['idle/input.file']
        state.assignProperty(self.action['run'], 'enabled', True)
        state.assignProperty(self.footer, 'text', 'Click "Run" to align.')
        def onEntry(event):
            self.textInput.notifyOnNextUpdate = True
        state.onEntry = onEntry

        state = self.state['idle/input.raw']
        state.assignProperty(self.action['run'], 'enabled', True)
        state.assignProperty(self.footer, 'text', 'Click "Run" to align.')

        state = self.state['idle/output.none']
        state.assignProperty(self.action['save'], 'enabled', False)
        def onEntry(event):
            self.pane['output'].title = 'Output'
            self.pane['input'].flag = None
            self.pane['output'].flag = None
            self.pane['input'].flagTip = None
            self.pane['output'].flagTip = None
            self.stack.setCurrentWidget(self.textOutput)
        state.onEntry = onEntry

        state = self.state['idle/output.failed']
        state.assignProperty(self.action['save'], 'enabled', False)
        tip = 'An error occured, please check the logs for details.'
        state.assignProperty(self.footer, 'text', tip)
        def onEntry(event):
            self.pane['output'].title = 'Progress Log'
            self.pane['input'].flag = None
            self.pane['output'].flag = None
            self.pane['input'].flagTip = None
            self.pane['output'].flagTip = None
            self.stack.setCurrentWidget(self.textLogger)
        state.onEntry = onEntry

        state = self.state['idle/output.complete']
        state.assignProperty(self.action['save'], 'enabled', True)
        state.assignProperty(self.footer, 'text', 'Sequence aligment was successful.')
        def onEntry(event):
            self.pane['output'].title = 'Results [{}]'.format(self.analysis.strategy)
            self.stack.setCurrentWidget(self.textOutput)
        state.onEntry = onEntry

        state = self.state['idle/output.updated']
        state.assignProperty(self.action['save'], 'enabled', True)
        tip = 'Input has changed, run a new analysis to update results.'
        state.assignProperty(self.footer, 'text', tip)
        def onEntry(event):
            self.pane['output'].title += ' [outdated]'
            self.stack.setCurrentWidget(self.textOutput)
        state.onEntry = onEntry

        state = self.state['running']
        state.assignProperty(self.action['run'], 'visible', False)
        state.assignProperty(self.action['stop'], 'visible', True)
        state.assignProperty(self.action['open'], 'enabled', False)
        state.assignProperty(self.action['save'], 'enabled', False)
        state.assignProperty(self.subheader, 'enabled', False)
        state.assignProperty(self.footer, 'text', 'Aligning sequences, please wait...')
        def onEntry(event):
            self.pane['output'].title = 'Progress Log'
            self.stack.setCurrentWidget(self.textLogger)
            self.textInput.setReadOnly(True)
        state.onEntry = onEntry

        internal = QtStateMachine.QAbstractTransition.TransitionType.InternalTransition

        transition = utility.NamedTransition('EMPTY')
        transition.setTransitionType(internal)
        def onTransition(event):
            self.setWindowTitle(self.title)
            self.pane['input'].title = 'Input'
        transition.onTransition = onTransition
        transition.setTargetState(self.state['idle/input.none'])
        self.state['idle/input'].addTransition(transition)

        transition = utility.NamedTransition('UPDATE')
        transition.setTransitionType(internal)
        def onTransition(event):
            self.setWindowTitle(self.title + ' - From Text')
            self.pane['input'].title = 'Input - From Text'
        transition.onTransition = onTransition
        transition.setTargetState(self.state['idle/input.raw'])
        self.state['idle/input'].addTransition(transition)

        transition = utility.NamedTransition('UPDATE')
        transition.setTransitionType(internal)
        transition.setTargetState(self.state['idle/output.updated'])
        self.state['idle/output.complete'].addTransition(transition)

        transition = utility.NamedTransition('OPEN')
        transition.setTransitionType(internal)
        def onTransition(event):
            fileInfo = QtCore.QFileInfo(event.kwargs['file'])
            fileName = fileInfo.fileName()
            if len(fileName) > 40:
                fileName = fileName[:37] + '...'
            self.setWindowTitle(self.title + ' - ' + fileName)
            self.pane['input'].title = 'Input - ' + fileName
        transition.onTransition = onTransition
        transition.setTargetStates([
            self.state['idle/input.file'],
            self.state['idle/output.none'],
            ])
        self.state['idle'].addTransition(transition)

        transition = utility.NamedTransition('RUN')
        transition.setTargetState(self.state['running'])
        self.state['idle'].addTransition(transition)

        transition = utility.NamedTransition('DONE')
        def onTransition(event):
            msgBox = QtWidgets.QMessageBox(self)
            msgBox.setWindowTitle(self.windowTitle())
            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setText('Alignment complete.')
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
            self.msgShow(msgBox)
        transition.onTransition = onTransition
        transition.setTargetStates([
            self.state['idle/input.last'],
            self.state['idle/output.complete'],
            ])
        self.state['running'].addTransition(transition)

        transition = utility.NamedTransition('FAIL')
        def onTransition(event):
            self.fail(event.args[0])
        transition.onTransition = onTransition
        transition.setTargetStates([
            self.state['idle/input.last'],
            self.state['idle/output.failed'],
            ])
        self.state['running'].addTransition(transition)

        transition = utility.NamedTransition('CANCEL')
        transition.setTargetStates([
            self.state['idle/input.last'],
            self.state['idle/output.last'],
            ])
        self.state['running'].addTransition(transition)

        self.machine.start()

    def skin(self):
        """Configure widget appearance"""
        color = {
            'white':  '#ffffff',
            'light':  '#eff1ee',
            'beige':  '#e1e0de',
            'gray':   '#abaaa8',
            'iron':   '#8b8d8a',
            'black':  '#454241',
            'red':    '#ee4e5f',
            'pink':   '#eb9597',
            'orange': '#eb6a4a',
            'brown':  '#655c5d',
            'green':  '#00ff00',
            }
        # using green for debugging
        palette = QtGui.QGuiApplication.palette()
        scheme = {
            QtGui.QPalette.Active: {
                QtGui.QPalette.Window: 'light',
                QtGui.QPalette.WindowText: 'black',
                QtGui.QPalette.Base: 'white',
                QtGui.QPalette.AlternateBase: 'light',
                QtGui.QPalette.PlaceholderText: 'brown',
                QtGui.QPalette.Text: 'black',
                QtGui.QPalette.Button: 'light',
                QtGui.QPalette.ButtonText: 'black',
                QtGui.QPalette.Light: 'white',
                QtGui.QPalette.Midlight: 'beige',
                QtGui.QPalette.Mid: 'gray',
                QtGui.QPalette.Dark: 'iron',
                QtGui.QPalette.Shadow: 'brown',
                QtGui.QPalette.Highlight: 'red',
                QtGui.QPalette.HighlightedText: 'white',
                # These work on linux only?
                QtGui.QPalette.ToolTipBase: 'beige',
                QtGui.QPalette.ToolTipText: 'brown',
                # These seem bugged anyway
                QtGui.QPalette.BrightText: 'green',
                QtGui.QPalette.Link: 'green',
                QtGui.QPalette.LinkVisited: 'green',
                },
            QtGui.QPalette.Disabled: {
                QtGui.QPalette.Window: 'light',
                QtGui.QPalette.WindowText: 'iron',
                QtGui.QPalette.Base: 'white',
                QtGui.QPalette.AlternateBase: 'light',
                QtGui.QPalette.PlaceholderText: 'green',
                QtGui.QPalette.Text: 'iron',
                QtGui.QPalette.Button: 'light',
                QtGui.QPalette.ButtonText: 'gray',
                QtGui.QPalette.Light: 'white',
                QtGui.QPalette.Midlight: 'beige',
                QtGui.QPalette.Mid: 'gray',
                QtGui.QPalette.Dark: 'iron',
                QtGui.QPalette.Shadow: 'brown',
                QtGui.QPalette.Highlight: 'pink',
                QtGui.QPalette.HighlightedText: 'white',
                # These seem bugged anyway
                QtGui.QPalette.BrightText: 'green',
                QtGui.QPalette.ToolTipBase: 'green',
                QtGui.QPalette.ToolTipText: 'green',
                QtGui.QPalette.Link: 'green',
                QtGui.QPalette.LinkVisited: 'green',
                },
            }
        scheme[QtGui.QPalette.Inactive] = scheme[QtGui.QPalette.Active]
        for group in scheme:
            for role in scheme[group]:
                palette.setColor(group, role,
                    QtGui.QColor(color[scheme[group][role]]))
        QtGui.QGuiApplication.setPalette(palette)

        self.colormap = {
            widgets.VectorIcon.Normal: {
                '#000': color['black'],
                '#f00': color['red'],
                },
            widgets.VectorIcon.Disabled: {
                '#000': color['gray'],
                '#f00': color['orange'],
                },
            }
        self.colormap_icon =  {
            '#000': color['black'],
            '#f00': color['red'],
            '#f88': color['pink'],
            }
        self.colormap_icon_light =  {
            '#000': color['iron'],
            '#ff0000': color['red'],
            '#ffa500': color['pink'],
            }

    def draw(self):
        """Draw all widgets"""

        self.header = widgets.Header()
        self.header.logoTool = widgets.VectorPixmap(get_resource('logos/svg/mafft.svg'),
            colormap=self.colormap_icon)
        self.header.logoProject = QtGui.QPixmap(get_resource('logos/png/itaxotools-micrologo.png'))
        self.header.description = (
            'Multiple alignment program' + '\n'
            'for amino acid or nucleotide sequences'
            )
        self.header.citation = (
            'MAFFT by Kazutaka Katoh (...)' + '\n'
            'GUI by Stefanos Patmanidis'
        )

        self.subheader = widgets.Subheader()
        self.subheader.setStyleSheet(self.subheader.styleSheet() +
            """QRadioButton {padding-right: 12px; padding-top: 2px;}""")

        self.subheader.icon = QtWidgets.QLabel()
        self.subheader.icon.setPixmap(widgets.VectorPixmap(get_icon('arrow-right.svg'),
            colormap=self.colormap_icon_light))
        self.subheader.icon.setStyleSheet('border-style: none;')

        self.labelTree = QtWidgets.QLabel("Strategy:")
        self.labelTree.setStyleSheet("""
            QLabel {
                color: palette(Shadow);
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 1px;
                padding: 4px 4px 6px 4px;
                border: none;
                }
            """)
        self.labelTree.setAlignment(QtCore.Qt.AlignCenter)
        self.labelTree.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)

        self.radio = {}
        self.radio['auto'] = QtWidgets.QRadioButton('Auto')
        self.radio['auto'].setChecked(True)
        self.radio['auto'].setToolTip("Select strategy based on data size")
        self.radio['fftns1'] = QtWidgets.QRadioButton('FFT-NS-1')
        self.radio['fftns1'].setToolTip("Very fast; recommended for >2,000 sequences; progressive method")
        self.radio['ginsi'] = QtWidgets.QRadioButton('G-INS-i')
        self.radio['ginsi'].setToolTip("Very slow; recommended for <200 sequences with global homology")

        self.searchWidget = widgets.SearchWidget()

        layout = QtWidgets.QHBoxLayout()
        layout.addSpacing(4)
        layout.addWidget(self.labelTree)
        layout.addSpacing(16)
        layout.addWidget(self.radio['auto'])
        layout.addWidget(self.radio['fftns1'])
        layout.addWidget(self.radio['ginsi'])
        layout.addStretch(1)
        layout.addWidget(self.searchWidget)
        layout.addSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)
        self.subheader.setLayout(layout)

        self.pane = {}

        self.textInput = TextEditInput(self)

        self.pane['input'] = widgets.Panel(self)
        self.pane['input'].title = 'Input'
        self.pane['input'].footer = ''
        self.pane['input'].body.addWidget(self.textInput)
        self.pane['input'].body.setContentsMargins(0, 0, 0, 0)

        self.textOutput = TextEditOutput()
        self.textLogger = TextEditLogger()
        self.textLogIO = io.TextEditLoggerIO(self.textLogger)

        self.stack = QtWidgets.QStackedLayout()
        self.stack.addWidget(self.textOutput)
        self.stack.addWidget(self.textLogger)

        self.pane['output'] = widgets.Panel(self)
        self.pane['output'].title = 'Output'
        self.pane['output'].footer = ''
        self.pane['output'].body.addLayout(self.stack)
        self.pane['output'].body.setContentsMargins(0, 0, 0, 0)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.pane['input'])
        self.splitter.addWidget(self.pane['output'])
        self.splitter.setStretchFactor(0,1)
        self.splitter.setStretchFactor(1,1)
        self.splitter.setCollapsible(0,False)
        self.splitter.setCollapsible(1,False)
        self.splitter.setStyleSheet("QSplitter::handle { height: 8px; }")
        self.splitter.setContentsMargins(8, 4, 8, 4)

        self.footer = QtWidgets.QLabel('Open a file to begin.')
        self.footer.setStyleSheet("""
            QLabel {
                color: palette(Shadow);
                font-size: 12px;
                background: palette(Window);
                border-top: 1px solid palette(Mid);
                padding: 6px 8px 8px 8px;
                }
            QLabel:disabled {
                color: palette(Mid);
                background: palette(Window);
                border: 1px solid palette(Mid);
                }
            """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.header, 0)
        layout.addWidget(self.subheader, 0)
        layout.addSpacing(8)
        layout.addWidget(self.splitter, 1)
        layout.addSpacing(8)
        layout.addWidget(self.footer, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def act(self):
        """Populate dialog actions"""
        self.action = {}

        self.action['open'] = QtGui.QAction('&Open', self)
        self.action['open'].setIcon(widgets.VectorIcon(get_icon('open.svg'), self.colormap))
        self.action['open'].setShortcut(QtGui.QKeySequence.Open)
        self.action['open'].setStatusTip('Open an existing file')
        self.action['open'].triggered.connect(self.handleOpen)

        self.action['save'] = QtGui.QAction('&Save', self)
        self.action['save'].setIcon(widgets.VectorIcon(get_icon('save.svg'), self.colormap))
        self.action['save'].setShortcut(QtGui.QKeySequence.Save)
        self.action['save'].setStatusTip('Save results')
        self.action['save'].triggered.connect(self.handleSave)

        self.action['run'] = QtGui.QAction('&Run', self)
        self.action['run'].setIcon(widgets.VectorIcon(get_icon('run.svg'), self.colormap))
        self.action['run'].setShortcut('Ctrl+R')
        self.action['run'].setStatusTip('Align sequences')
        self.action['run'].triggered.connect(self.handleRun)

        self.action['stop'] = QtGui.QAction('&Stop', self)
        self.action['stop'].setIcon(widgets.VectorIcon(get_icon('stop.svg'), self.colormap))
        self.action['stop'].setStatusTip('Cancel alignment')
        self.action['stop'].triggered.connect(self.handleStop)

        self.action['find'] = QtGui.QAction('&Find', self)
        self.action['find'].setShortcut(QtGui.QKeySequence.Find)
        self.action['find'].setStatusTip('Find a sequence or name')
        self.action['find'].triggered.connect(self.handleFind)

        self.action['find_next'] = QtGui.QAction('&Find Next', self)
        pixmap = widgets.VectorPixmap(get_icon('search.svg'),
            colormap=self.colormap_icon_light)
        self.action['find_next'].setIcon(pixmap)
        self.action['find_next'].setShortcut(QtGui.QKeySequence.FindNext)
        self.action['find_next'].setStatusTip('Find next')
        self.action['find_next'].triggered.connect(self.handleFindNext)


        self.header.toolbar.addAction(self.action['open'])
        self.header.toolbar.addAction(self.action['save'])
        self.header.toolbar.addAction(self.action['run'])
        self.header.toolbar.addAction(self.action['stop'])

        self.addAction(self.action['find'])
        self.searchWidget.setSearchAction(self.action['find_next'])

    def handleFind(self):
        self.searchWidget.setFocus()
        self.searchWidget.selectAll()

    def handleFindNext(self):
        what = self.searchWidget.text()
        def findLoop(widget, what):
            x = widget.find(what)
            if not x:
                cursor = widget.textCursor()
                cursor.movePosition(QtGui.QTextCursor.Start)
                widget.setTextCursor(cursor)
                widget.find(what)
        findLoop(self.textInput, what)
        findLoop(self.textOutput, what)

    def handleRunWork(self):
        """Runs on the UProcess, defined here for pickability"""
        self.analysis.log = sys.stdout
        self.analysis.run()
        return (self.analysis.results, self.analysis.strategy)

    def handleRun(self):
        """Called by Run button"""
        for strategy in self.radio:
            if self.radio[strategy].isChecked():
                self.analysis.params.general.strategy = strategy
        try:
            self._temp = tempfile.TemporaryDirectory(prefix='mafftpy_')
            target = pathlib.Path(self._temp.name)
            self.analysis.target = target.as_posix()
            if self.file is not None:
                self.analysis.file = self.file
            else:
                temp = target / 'from_text'
                with open(str(temp), 'w') as file:
                    file.write(self.textInput.toPlainText())
                    file.write('\n')
                self.analysis.file = str(temp)
        except Exception as exception:
            self.fail(exception)
            return
        self.textLogger.clear()

        def done(tuple):
            result, strategy = tuple
            self.temp = self._temp
            self.analysis.results = result
            self.analysis.strategy = strategy
            with open(pathlib.Path(result) / 'pre') as output:
                self.textOutput.setPlainText(output.read())
            self.textInput.notifyOnNextUpdate = True
            self.machine.postEvent(utility.NamedEvent('DONE', True))

        def fail(exception):
            self.textInput.notifyOnNextUpdate = True
            self.machine.postEvent(utility.NamedEvent('FAIL', exception))

        self.process = utility.UProcess(self.handleRunWork)
        self.process.done.connect(done)
        self.process.fail.connect(fail)
        self.process.setStream(self.textLogIO)
        self.process.start()
        self.machine.postEvent(utility.NamedEvent('RUN'))

    def handleStop(self):
        """Called by cancel button"""
        msgBox = QtWidgets.QMessageBox(self)
        msgBox.setWindowTitle(self.windowTitle())
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
        msgBox.setText('Cancel ongoing analysis?')
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.No)
        confirm = self.msgShow(msgBox)
        if confirm == QtWidgets.QMessageBox.Yes:
            if self.process is not None:
                self.process.quit()
            self.textInput.notifyOnNextUpdate = True
            self.machine.postEvent(utility.NamedEvent('CANCEL'))

    def handleOpen(self, checked=False, fileName=None):
        """Called by toolbar action"""
        # `checked` kwarg provided by default trigger event
        if fileName is None:
            (fileName, _) = QtWidgets.QFileDialog.getOpenFileName(self,
                self.title + ' - Open File',
                QtCore.QDir.currentPath(),
                'All Files (*)')
        if len(fileName) == 0:
            return
        try:
            with open(fileName) as input:
                self.textInput.setPlainText(input.read())
        except Exception as e:
            self.fail(e)
        self.textOutput.clear()
        self.machine.postEvent(utility.NamedEvent('OPEN',file=fileName))
        self.file = fileName

    def handleSave(self):
        """Pickle and save current analysis"""
        if self.file is not None:
            outName = pathlib.Path(self.file).stem
        else:
            outName = "sequence"
        outName += '_' + self.analysis.strategy
        outName += '.fas'
        (fileName, _) = QtWidgets.QFileDialog.getSaveFileName(self,
            self.title + ' - Save Analysis',
            QtCore.QDir.currentPath() + '/' + outName,
            'Fasta sequence (*.fas)')
        if len(fileName) == 0:
            return
        try:
            source = pathlib.Path(self.analysis.results) / 'pre'
            shutil.copyfile(source, fileName)
        except Exception as exception:
            self.fail(exception)
        else:
            self.footer.setText(
                'Saved aligned sequence to file: {}'.format(fileName))


def show():
    """Entry point"""
    def init():
        if len(sys.argv) >= 2:
            file = pathlib.Path(sys.argv[1])
            main.handleOpen(fileName=str(file))

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    main = Main(init=init)
    main.setWindowFlags(QtCore.Qt.Window)
    main.setModal(True)
    main.show()
    sys.exit(app.exec_())
