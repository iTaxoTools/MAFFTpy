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
import pathlib
import importlib.resources

from itaxotools.common.param import qt as param_qt
from itaxotools.common import utility
from itaxotools.common import widgets
from itaxotools.common import resources
from itaxotools.common import io

from .. import core


_resource_path = importlib.resources.files(resources)
def get_resource(path):
    return str(_resource_path / path)
def get_icon(path):
    return str(_resource_path / 'icons/svg' / path)


class Main(widgets.ToolDialog):
    """Main window, handles everything"""

    def __init__(self, parent=None, init=None):
        super(Main, self).__init__(parent)

        self.title = 'MAFFTpy'
        self.analysis = core.MultipleSequenceAlignment()

        self.setWindowTitle(self.title)
        self.setWindowIcon(QtGui.QIcon(get_resource('logos/ico/mafft.ico')))
        self.resize(854,480)

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
        self.state['idle'] = QtStateMachine.QState(self.machine)
        self.state['idle.last'] = QtStateMachine.QHistoryState(self.state['idle'])
        self.state['idle.none'] = QtStateMachine.QState(self.state['idle'])
        self.state['idle.open'] = QtStateMachine.QState(self.state['idle'])
        self.state['idle.done'] = QtStateMachine.QState(self.state['idle'])
        self.state['idle.done.complete'] = QtStateMachine.QState(self.state['idle.done'])
        self.state['idle.done.updated'] = QtStateMachine.QState(self.state['idle.done'])
        self.state['idle.done'].setInitialState(self.state['idle.done.complete'])
        self.state['idle'].setInitialState(self.state['idle.none'])
        self.state['running'] = QtStateMachine.QState(self.machine)
        self.machine.setInitialState(self.state['idle'])

        state = self.state['idle']
        state.assignProperty(self.action['run'], 'visible', True)
        state.assignProperty(self.action['stop'], 'visible', False)
        state.assignProperty(self.action['open'], 'enabled', True)

        state = self.state['idle.none']
        state.assignProperty(self.action['run'], 'enabled', False)
        state.assignProperty(self.action['save'], 'enabled', False)

        state = self.state['idle.open']
        state.assignProperty(self.action['run'], 'enabled', True)
        state.assignProperty(self.action['save'], 'enabled', False)

        state = self.state['idle.done']
        state.assignProperty(self.action['run'], 'enabled', True)
        state.assignProperty(self.action['save'], 'enabled', True)

        state = self.state['running']
        state.assignProperty(self.action['run'], 'visible', False)
        state.assignProperty(self.action['stop'], 'visible', True)
        state.assignProperty(self.action['open'], 'enabled', False)
        state.assignProperty(self.action['save'], 'enabled', False)

        state = self.state['idle.done.complete']
        def onEntry(event):
            print('idle.done.complete')
        state.onEntry = onEntry

        state = self.state['idle.done.updated']
        def onEntry(event):
            print('idle.done.updated')
        state.onEntry = onEntry

        transition = utility.NamedTransition('OPEN')
        def onTransition(event):
            fileInfo = QtCore.QFileInfo(event.kwargs['file'])
            labelText = fileInfo.baseName()
            self.setWindowTitle(self.title + ' - ' + labelText)
            self.labelTree.setText(labelText)
        transition.onTransition = onTransition
        transition.setTargetState(self.state['idle.open'])
        self.state['idle'].addTransition(transition)

        transition = utility.NamedTransition('RUN')
        transition.setTargetState(self.state['running'])
        self.state['idle'].addTransition(transition)

        transition = utility.NamedTransition('DONE')
        def onTransition(event):
            msgBox = QtWidgets.QMessageBox(self)
            msgBox.setWindowTitle(self.windowTitle())
            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setText('Analysis complete.')
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
            self.msgShow(msgBox)
        transition.onTransition = onTransition
        transition.setTargetState(self.state['idle.done.complete'])
        self.state['running'].addTransition(transition)

        transition = utility.NamedTransition('UPDATE')
        transition.setTargetState(self.state['idle.done.updated'])
        self.state['idle.done'].addTransition(transition)

        transition = utility.NamedTransition('FAIL')
        def onTransition(event):
            self.pane['results'].setCurrentIndex(1)
            self.fail(event.args[0])
        transition.onTransition = onTransition
        transition.setTargetState(self.state['idle.last'])
        self.state['running'].addTransition(transition)

        transition = utility.NamedTransition('CANCEL')
        transition.setTargetState(self.state['idle.last'])
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
            '#ff0000': color['red'],
            '#ffa500': color['pink'],
            }
        self.colormap_icon_light =  {
            '#000': color['iron'],
            '#ff0000': color['red'],
            '#ffa500': color['pink'],
            }
        self.colormap_graph =  {
            'abgd': {
                'black':   color['black'],
                '#D82424': color['red'],
                '#EBE448': color['gray'],
                },
            'disthist': {
                'black':   color['black'],
                '#EBE448': color['beige'],
                },
            'rank': {
                'black':   color['black'],
                '#D82424': color['red'],
                },
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
        self.radio['fftns1'] = QtWidgets.QRadioButton('FFT-NS-1')
        self.radio['ginsi'] = QtWidgets.QRadioButton('G-INS-i')

        def search(what):
            print('SEARCH', what)
        self.searchWidget = widgets.SearchWidget()
        pixmap = widgets.VectorPixmap(get_icon('search.svg'),
            colormap=self.colormap_icon_light)
        self.searchWidget.setSearchAction(pixmap, search)
        self.searchWidget.setStyleSheet("""
            SearchWidget {
                min-width: 200px;
                }
            """)

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

        self.textInput = QtWidgets.QTextEdit()
        # myTextEdit->document()->isEmpty()

        self.pane['input'] = widgets.Panel(self)
        self.pane['input'].title = 'Input'
        self.pane['input'].footer = ''
        self.pane['input'].body.addWidget(self.textInput)
        self.pane['input'].body.setContentsMargins(0, 0, 0, 0)

        self.textOutput = QtWidgets.QTextEdit()

        self.pane['output'] = widgets.Panel(self)
        self.pane['output'].title = 'Output'
        self.pane['output'].footer = ''
        self.pane['output'].body.addWidget(self.textOutput)
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
        self.action['save'].setStatusTip('Save analysis state')
        self.action['save'].triggered.connect(self.handleSaveAnalysis)

        self.action['run'] = QtGui.QAction('&Run', self)
        self.action['run'].setIcon(widgets.VectorIcon(get_icon('run.svg'), self.colormap))
        self.action['run'].setShortcut('Ctrl+R')
        self.action['run'].setStatusTip('Run rate analysis')
        self.action['run'].triggered.connect(self.handleRun)

        self.action['stop'] = QtGui.QAction('&Stop', self)
        self.action['stop'].setIcon(widgets.VectorIcon(get_icon('stop.svg'), self.colormap))
        self.action['stop'].setStatusTip('Cancel analysis')
        self.action['stop'].triggered.connect(self.handleStop)

        self.header.toolbar.addAction(self.action['open'])
        self.header.toolbar.addAction(self.action['save'])
        self.header.toolbar.addAction(self.action['run'])
        self.header.toolbar.addAction(self.action['stop'])

    # def createTabLogs(self):
    #     tab = QtWidgets.QWidget()
    #
    #     self.logw = utility.TextEditLogger()
    #     fixedFont = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
    #     self.logw.setFont(fixedFont)
    #     self.logio = utility.TextEditLoggerIO(self.logw)
    #
    #     layout = QtWidgets.QHBoxLayout()
    #     layout.addWidget(self.logw)
    #     layout.setContentsMargins(5, 5, 5, 5)
    #     tab.setLayout(layout)
    #
    #     return tab

    def handleRunWork(self):
        """Runs on the UProcess, defined here for pickability"""
        self.analysis.run()
        return self.analysis.results

    def handleRun(self):
        """Called by Run button"""
        try:
            self.paramWidget.applyParams()
        except Exception as exception:
            self.fail(exception)
            return

        if self.analysis.param.general.scalar:
            msgBox = QtWidgets.QMessageBox(self)
            msgBox.setWindowTitle(self.windowTitle())
            msgBox.setIcon(QtWidgets.QMessageBox.Question)
            msgBox.setText('Scalar mode activated, all time constraints will be ignored.')
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
            confirm = self.msgShow(msgBox)
            if confirm == QtWidgets.QMessageBox.Cancel:
                return

        def done(result):
            with utility.redirect(sys, 'stdout', self.logio):
                result.print()
                print(result.chronogram.as_string(schema='newick'))
            self.analysis.results = result
            self.machine.postEvent(utility.NamedEvent('DONE', True))

        def fail(exception):
            self.machine.postEvent(utility.NamedEvent('FAIL', exception))

        self.process = utility.UProcess(self.handleRunWork)
        self.process.done.connect(done)
        self.process.fail.connect(fail)
        self.process.setStream(self.logio)
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
            self.logio.writeline('\nAnalysis aborted by user.')
            if self.process is not None:
                self.process.quit()
            self.machine.postEvent(utility.NamedEvent('CANCEL'))

    def handleOpen(self):
        """Called by toolbar action"""
        (fileName, _) = QtWidgets.QFileDialog.getOpenFileName(self,
            'MAFFTpy - Open File',
            QtCore.QDir.currentPath(),
            'All Files (*) ;; Newick (*.nwk) ;; Rates Analysis (*.r8s)')
        if len(fileName) == 0:
            return
        suffix = QtCore.QFileInfo(fileName).suffix()
        if suffix == 'r8s':
            self.handleOpenAnalysis(fileName)
        else:
            self.handleOpenFile(fileName)

    def handleSaveAnalysis(self):
        """Pickle and save current analysis"""
        (fileName, _) = QtWidgets.QFileDialog.getSaveFileName(self,
            'MAFFTpy - Save Analysis',
            QtCore.QDir.currentPath() + '/' + self.analysis.tree.label + '.r8s',
            'Rates Analysis (*.r8s)')
        if len(fileName) == 0:
            return
        try:
            self.paramWidget.applyParams()
            with open(fileName, 'wb') as file:
                pickle.dump(self.analysis, file)
        except Exception as exception:
            self.fail(exception)
        else:
            self.logio.writeline(
                'Saved analysis to file: {}\n'.format(fileName))
        pass


def show():
    """Entry point"""
    def init():
        if len(sys.argv) >= 2:
            file = pathlib.Path(sys.argv[1])
            main.handleOpen(str(file))

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    main = Main(init=init)
    main.setWindowFlags(QtCore.Qt.Window)
    main.setModal(True)
    main.show()
    sys.exit(app.exec_())
