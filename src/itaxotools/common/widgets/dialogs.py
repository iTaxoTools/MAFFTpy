# -----------------------------------------------------------------------------
# Commons - Utility classes for iTaxoTools modules
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
# -----------------------------------------------------------------------------

"""Widgets for dialog windows"""


from PySide6 import QtCore
from PySide6 import QtWidgets

import enum

from .graphics import ScalingImage
from .layouts import VLineSeparator

class PushButton(QtWidgets.QPushButton):
    """A larger button with square borders"""
    def __init__(self, *args, **kwargs):
        onclick = None
        if 'onclick' in kwargs:
            onclick = kwargs.pop('onclick')
        super().__init__(*args, **kwargs)
        if onclick:
            self.clicked.connect(onclick)
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid Palette(Mid);
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 Palette(Light), stop: 1 Palette(Window));
                color: Palette(Text);
                padding: 5px 15px;
                min-width: 80px;
                outline: none;
                }
            QPushButton:hover {
                border: 1px solid qlineargradient(x1: -1, y1: 0, x2: 0, y2: 2,
                    stop: 0 Palette(Midlight), stop: 1 Palette(Mid));
                background: Palette(Light);
                }
            QPushButton:focus:hover {
                border: 1px solid Palette(Highlight);
                background: Palette(Light);
                }
            QPushButton:focus:!hover {
                border: 1px solid Palette(Highlight);
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 10,
                    stop: 0 Palette(Light), stop: 1 Palette(Highlight));
                }
            QPushButton:focus:pressed {
                border: 1px solid Palette(Highlight);
                background: Palette(Midlight);
                }
            QPushButton:pressed {
                border: 1px solid Palette(Highlight);
                background: Palette(Midlight);
                }
            QPushButton:disabled {
                border: 1px solid qlineargradient(x1: 0, y1: -1, x2: 0, y2: 2,
                    stop: 0 Palette(Midlight), stop: 1 Palette(Dark));
                background: Palette(Midlight);
                color: Palette(Dark)
        }""")


class _HeaderLabels(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tool = QtWidgets.QLabel('TOOL')
        self.tool.setAlignment(QtCore.Qt.AlignBottom)
        self.tool.setStyleSheet("""
            color: palette(Text);
            font-size: 14px;
            letter-spacing: 1px;
            font-weight: bold;
            text-decoration: underline;
            """)

        self.citation = QtWidgets.QLabel('CITATION')
        self.citation.setAlignment(QtCore.Qt.AlignBottom)
        self.citation.setStyleSheet("""
            color: palette(Shadow);
            font-size: 12px;
            font-style: italic;
            """)

        self.task = QtWidgets.QLabel('TASK')
        self.task.setAlignment(QtCore.Qt.AlignBottom)
        self.task.setStyleSheet("""
            color: palette(Shadow);
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 1px;
            """)

        self.description = QtWidgets.QLabel('DESCRIPTION')
        self.description.setAlignment(QtCore.Qt.AlignTop)
        self.description.setStyleSheet("""
            color: palette(Text);
            font-size: 12px;
            letter-spacing: 1px;
            """)

        layout = QtWidgets.QGridLayout()
        layout.setRowStretch(0, 2)
        layout.addWidget(self.tool, 1, 0, 1, 2)
        layout.addWidget(self.citation, 1, 2)
        layout.addWidget(self.task, 2, 0, 1, 2)
        layout.addWidget(self.description, 3, 1, 1, 3)
        layout.setRowStretch(4, 2)
        layout.setColumnStretch(3, 1)
        layout.setRowMinimumHeight(0, 6)
        layout.setRowMinimumHeight(4, 6)
        layout.setColumnMinimumWidth(0, 4)
        layout.setHorizontalSpacing(4)
        layout.setVerticalSpacing(4)
        layout.setContentsMargins(0, 0, 0, 4)
        self.setLayout(layout)


class _HeaderToolBar(QtWidgets.QToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIconSize(QtCore.QSize(32, 32))
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Minimum)
        self.setToolButtonStyle(
            QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setStyleSheet("""
            QToolBar {
                spacing: 2px;
                }
            QToolButton {
                color: palette(ButtonText);
                background: transparent;
                border: 2px solid transparent;
                border-radius: 3px;
                font-size: 14px;
                min-width: 50px;
                min-height: 60px;
                padding: 6px 0px 0px 0px;
                margin: 4px 0px 4px 0px;
                }
            QToolButton:hover {
                background: palette(Window);
                border: 2px solid transparent;
                }
            QToolButton:pressed {
                background: palette(Midlight);
                border: 2px solid palette(Mid);
                border-radius: 3px;
                }
            QToolButton[popupMode="2"]:pressed {
                padding-bottom: 5px;
                border: 1px solid palette(Dark);
                margin: 5px 1px 0px 1px;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                }
            QToolButton::menu-indicator {
                image: none;
                width: 30px;
                border-bottom: 2px solid palette(Mid);
                subcontrol-origin: padding;
                subcontrol-position: bottom;
                }
            QToolButton::menu-indicator:disabled {
                border-bottom: 2px solid palette(Midlight);
                }
            QToolButton::menu-indicator:pressed {
                border-bottom: 0px;
                }
            """)


class Header(QtWidgets.QFrame):
    """
    The Taxotools toolbar, with space for a title, description,
    citations and two logos.
    """
    def __init__(self):
        super().__init__()
        self.dictTool = {'title': '', 'citation': '', 'description': ''}
        self.dictTask = {'title': '', 'description': ''}
        self._logoTool = None
        self.draw()

    def draw(self):
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Maximum)
        self.setStyleSheet("""
            Header {
                background: palette(Light);
                border-top: 1px solid palette(Mid);
                border-bottom: 1px solid palette(Dark);
                }
            """)

        self.labels = _HeaderLabels()
        self.widgetLogoTool = QtWidgets.QLabel()
        self.widgetLogoTool.setAlignment(QtCore.Qt.AlignCenter)
        self.widgetLogoProject = ScalingImage()
        self.toolbar = _HeaderToolBar()
        self.widget = QtWidgets.QWidget()

        layout = QtWidgets.QHBoxLayout()
        layout.addSpacing(8)
        layout.addWidget(self.widgetLogoTool)
        layout.addSpacing(8)
        layout.addWidget(self.labels, 0)
        layout.addSpacing(8)
        layout.addWidget(self.toolbar, 0)
        layout.addWidget(self.widget, 1)
        layout.addSpacing(12)
        layout.addWidget(self.widgetLogoProject)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def setTool(self, title, citation, description):
        self.showTool(title=title, citation=citation, description=description)
        self.updateLabelWidth()

    def showTool(self, **kwargs):
        d = {k: v for k, v in kwargs.items() if v is not None}
        d = {k: v for k, v in d.items() if k in self.dictTool.keys()}
        self.dictTool.update(d)
        self.labels.tool.setText(self.dictTool['title'])
        self.labels.citation.setText(self.dictTool['citation'])
        self.labels.description.setText(self.dictTool['description'])
        self.labels.task.setVisible(False)
        self.labels.tool.setVisible(True)
        self.labels.citation.setVisible(True)

    def showTask(self, **kwargs):
        d = {k: v for k, v in kwargs.items() if v is not None}
        d = {k: v for k, v in d.items() if k in self.dictTask.keys()}
        self.dictTask.update(d)
        self.labels.task.setText(self.dictTask['title'])
        self.labels.description.setText(self.dictTask['description'])
        self.labels.tool.setVisible(False)
        self.labels.citation.setVisible(False)
        self.labels.task.setVisible(True)

    def updateLabelWidth(self):
        width = max(self.labels.minimumWidth(), self.labels.sizeHint().width())
        self.labels.setMinimumWidth(width)

    @property
    def logoTool(self):
        return self._logoTool

    @logoTool.setter
    def logoTool(self, logo):
        self.widgetLogoTool.setPixmap(logo)
        self._logoTool = logo

    @property
    def logoProject(self):
        return self.logoProject.logo

    @logoProject.setter
    def logoProject(self, logo):
        self.widgetLogoProject.logo = logo


class HeaderOld(QtWidgets.QFrame):
    """
    The Taxotools toolbar, with space for a title, description,
    citations and two logos.
    """
    def __init__(self):
        """ """
        super().__init__()

        self._title = None
        self._description = None
        self._citation = None
        self._logoTool = None

        self.logoSize = 64

        self.draw()

    def draw(self):
        """ """
        self.setStyleSheet("""
            HeaderOld {
                background: palette(Light);
                border-top: 2px solid palette(Mid);
                border-bottom: 1px solid palette(Dark);
                }
            """)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Maximum)

        self.labelDescription = QtWidgets.QLabel('DESCRIPTION')
        self.labelDescription.setAlignment(QtCore.Qt.AlignBottom)
        self.labelDescription.setStyleSheet("""
            color: palette(Text);
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 1px;
            """)

        self.labelCitation = QtWidgets.QLabel('CITATION')
        self.labelCitation.setAlignment(QtCore.Qt.AlignTop)
        self.labelCitation.setStyleSheet("""
            color: palette(Shadow);
            font-size: 12px;
            """)

        labels = QtWidgets.QVBoxLayout()
        labels.addStretch(1)
        labels.addWidget(self.labelDescription)
        labels.addWidget(self.labelCitation)
        labels.addStretch(1)
        labels.addSpacing(4)
        labels.setSpacing(4)

        self.labelLogoTool = QtWidgets.QLabel()
        self.labelLogoTool.setAlignment(QtCore.Qt.AlignCenter)

        self.labelLogoProject = ScalingImage()
        layoutLogoProject = QtWidgets.QHBoxLayout()
        layoutLogoProject.addWidget(self.labelLogoProject)
        layoutLogoProject.setContentsMargins(2,4,2,4)

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setIconSize(QtCore.QSize(32,32))
        self.toolbar.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.toolbar.setToolButtonStyle(
            QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.toolbar.setStyleSheet("""
            QToolBar {
                spacing: 2px;
                }
            QToolButton {
                color: palette(ButtonText);
                background: transparent;
                border: 2px solid transparent;
                border-radius: 3px;
                font-size: 14px;
                min-width: 50px;
                min-height: 60px;
                padding: 6px 0px 0px 0px;
                margin: 4px 0px 4px 0px;
                }
            QToolButton:hover {
                background: palette(Window);
                border: 2px solid transparent;
                }
            QToolButton:pressed {
                background: palette(Midlight);
                border: 2px solid palette(Mid);
                border-radius: 3px;
                }
            QToolButton[popupMode="2"]:pressed {
                padding-bottom: 5px;
                border: 1px solid palette(Dark);
                margin: 5px 1px 0px 1px;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                }
            QToolButton::menu-indicator {
                image: none;
                width: 30px;
                border-bottom: 2px solid palette(Mid);
                subcontrol-origin: padding;
                subcontrol-position: bottom;
                }
            QToolButton::menu-indicator:disabled {
                border-bottom: 2px solid palette(Midlight);
                }
            QToolButton::menu-indicator:pressed {
                border-bottom: 0px;
                }
            """)

        layout = QtWidgets.QHBoxLayout()
        layout.addSpacing(8)
        layout.addWidget(self.labelLogoTool)
        layout.addSpacing(6)
        layout.addWidget(VLineSeparator())
        layout.addSpacing(12)
        layout.addLayout(labels, 0)
        layout.addSpacing(12)
        layout.addWidget(VLineSeparator())
        layout.addSpacing(8)
        layout.addWidget(self.toolbar, 0)
        layout.addStretch(1)
        layout.addWidget(VLineSeparator())
        layout.addLayout(layoutLogoProject, 0)
        # layout.addWidget(self.labelLogoProject)
        layout.addSpacing(2)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self.labelDescription.setText(description)
        self._description = description

    @property
    def citation(self):
        return self._citation

    @citation.setter
    def citation(self, citation):
        self.labelCitation.setText(citation)
        self._citation = citation

    @property
    def logoTool(self):
        return self._logoTool

    @logoTool.setter
    def logoTool(self, logo):
        self.labelLogoTool.setPixmap(logo)
        self._logoTool = logo

    @property
    def logoProject(self):
        return self.labelLogoProject.logo

    @logoProject.setter
    def logoProject(self, logo):
        self.labelLogoProject.logo = logo


class Subheader(QtWidgets.QFrame):
    """A simple styled frame"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Maximum)
        self.setStyleSheet("""
            QFrame {
                background-color: palette(Midlight);
                border-style: solid;
                border-width: 1px 0px 1px 0px;
                border-color: palette(Mid);
                }
            """)


class NavigationButton(PushButton):
    def __init__(self, text, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self._default_text = text

    def setText(self, text=None):
        if text is None:
            return super().setText(self._default_text)
        return super().setText(text)


def _mode_method(mode):
    """
    Class method decorator that populates `_mode_methods` with the
    given mode, pointing to the decorated function, for use by setMode().
    """
    class ModeMethod:
        def __init__(self, method):
            self.method = method

        def __call__(self, *args, **kwargs):
            self.method(*args, **kwargs)

        def __set_name__(self, owner, name):
            owner._mode_methods[mode] = self.method
            setattr(owner, name, self.method)
    return ModeMethod


class NavigationFooter(QtWidgets.QFrame):
    """A styled footer with navigation buttons"""

    _mode_methods = {}
    _buttons = []

    class Mode(enum.Enum):
        First = enum.auto()
        Middle = enum.auto()
        Final = enum.auto()
        Wait = enum.auto()
        Error = enum.auto()
        Frozen = enum.auto()

    class ButtonMode(enum.Enum):
        Enabled = enum.auto()
        Disabled = enum.auto()
        Hidden = enum.auto()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QFrame {
                border-style: solid;
                border-width: 1px 0px 0px 0px;
                border-color: Palette(Mid);
                }
            """)

        self.back = self.addButton('< &Back')
        self.next = self.addButton('&Next >')
        self.exit = self.addButton('E&xit')
        self.cancel = self.addButton('&Cancel')
        self.new = self.addButton('&New')

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.cancel)
        layout.addWidget(self.new)
        layout.addStretch(1)
        layout.addWidget(self.back)
        layout.addWidget(self.next)
        layout.addWidget(self.exit)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        self.setLayout(layout)

    def addButton(self, text):
        button = NavigationButton(text)
        self._buttons.append(button)
        return button

    def setButtonActions(self, dictionary):
        """Bind functions to buttons"""
        for name in dictionary:
            button = getattr(self, name)
            button.clicked.connect(dictionary[name])

    def setMode(self, mode: Mode, backwards=False):
        """Calls the function corresponding to given mode"""
        if mode in self._mode_methods:
            self._mode_methods[mode](self, backwards)
            for button in self._buttons:
                button.setText()
        else:
            raise ValueError(f'Mode {mode} has no matching method.')

    def setButtonMode(self, button, mode):
        button.setVisible(mode != self.ButtonMode.Hidden)
        button.setEnabled(mode == self.ButtonMode.Enabled)

    @_mode_method(Mode.First)
    def setModeFirst(self, backwards=False):
        self.setButtonMode(self.back, self.ButtonMode.Disabled)
        self.setButtonMode(self.next, self.ButtonMode.Enabled)
        self.setButtonMode(self.exit, self.ButtonMode.Hidden)
        self.setButtonMode(self.cancel, self.ButtonMode.Disabled)
        self.setButtonMode(self.new, self.ButtonMode.Hidden)
        self.next.setFocus()

    @_mode_method(Mode.Middle)
    def setModeMiddle(self, backwards=False):
        self.setButtonMode(self.back, self.ButtonMode.Enabled)
        self.setButtonMode(self.next, self.ButtonMode.Enabled)
        self.setButtonMode(self.exit, self.ButtonMode.Hidden)
        self.setButtonMode(self.cancel, self.ButtonMode.Disabled)
        self.setButtonMode(self.new, self.ButtonMode.Hidden)
        if backwards:
            self.back.setFocus()
        else:
            self.next.setFocus()

    @_mode_method(Mode.Final)
    def setModeFinal(self, backwards=False):
        self.setButtonMode(self.back, self.ButtonMode.Enabled)
        self.setButtonMode(self.next, self.ButtonMode.Hidden)
        self.setButtonMode(self.exit, self.ButtonMode.Enabled)
        self.setButtonMode(self.cancel, self.ButtonMode.Hidden)
        self.setButtonMode(self.new, self.ButtonMode.Enabled)
        self.exit.setFocus()

    @_mode_method(Mode.Wait)
    def setModeWait(self, backwards=False):
        self.setButtonMode(self.back, self.ButtonMode.Disabled)
        self.setButtonMode(self.next, self.ButtonMode.Disabled)
        self.setButtonMode(self.exit, self.ButtonMode.Hidden)
        self.setButtonMode(self.cancel, self.ButtonMode.Enabled)
        self.setButtonMode(self.new, self.ButtonMode.Hidden)
        self.cancel.setFocus()

    @_mode_method(Mode.Error)
    def setModeError(self, backwards=False):
        self.setButtonMode(self.back, self.ButtonMode.Enabled)
        self.setButtonMode(self.next, self.ButtonMode.Disabled)
        self.setButtonMode(self.exit, self.ButtonMode.Hidden)
        self.setButtonMode(self.cancel, self.ButtonMode.Disabled)
        self.setButtonMode(self.new, self.ButtonMode.Hidden)
        self.back.setFocus()

    @_mode_method(Mode.Frozen)
    def setModeFrozen(self, backwards=False):
        self.setButtonMode(self.back, self.ButtonMode.Disabled)
        self.setButtonMode(self.next, self.ButtonMode.Disabled)
        self.setButtonMode(self.exit, self.ButtonMode.Hidden)
        self.setButtonMode(self.cancel, self.ButtonMode.Disabled)
        self.setButtonMode(self.new, self.ButtonMode.Hidden)


class Panel(QtWidgets.QWidget):
    """
    A stylized panel with title, footer and body.
    Set `self.title`, `self.footer` and `self.flag` with text.
    Use `self.body.addWidget()`` to populate the pane.
    """
    def __init__(self, parent):
        """Initialize internal vars"""
        super().__init__(parent=parent)
        self._title = None
        self._foot = None
        self._flag = None
        self._flagTip = None

        # if not hasattr(parent, '_pane_foot_height'):
        #     parent._pane_foot_height = None
        self.draw()

    def draw(self):
        """ """
        self.labelTitle = QtWidgets.QLabel('TITLE GO HERE')
        self.labelTitle.setIndent(4)
        self.labelTitle.setMargin(2)
        self.labelTitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                letter-spacing: 1px;
                color: palette(Light);
                background: palette(Shadow);
                border-right: 1px solid palette(Dark);
                border-bottom: 2px solid palette(Shadow);
                border-bottom-left-radius: 0px;
                border-top-right-radius: 1px;
                padding-top: 2px;
                }
            QLabel:disabled {
                background: palette(Mid);
                border-right: 1px solid palette(Mid);
                border-bottom: 2px solid palette(Mid);
                }
            """)

        self.labelFlag = QtWidgets.QLabel('')
        self.labelFlag.setVisible(False)
        self.labelFlag.setIndent(4)
        self.labelFlag.setMargin(2)
        self.labelFlag.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 1px;
                color: palette(Light);
                background: palette(Mid);
                border-right: 1px solid palette(Midlight);
                border-bottom: 2px solid palette(Midlight);
                border-bottom-left-radius: 1px;
                border-top-right-radius: 1px;
                padding-top: 1px;
                }
            QLabel:disabled {
                background: palette(Midlight);
                border-right: 1px solid palette(Light);
                border-bottom: 2px solid palette(Light);
                }
            """)

        # To be filled by user
        self.body = QtWidgets.QVBoxLayout()

        self.labelFoot = QtWidgets.QLabel('FOOTER')
        self.labelFoot.setAlignment(QtCore.Qt.AlignCenter)
        self.labelFoot.setStyleSheet("""
            QLabel {
                color: palette(Shadow);
                background: palette(Window);
                border: 1px solid palette(Mid);
                padding: 5px 10px 5px 10px;
                }
            QLabel:disabled {
                color: palette(Mid);
                background: palette(Window);
                border: 1px solid palette(Mid);
                }
            """)

        layoutTop = QtWidgets.QHBoxLayout()
        layoutTop.addWidget(self.labelTitle, 1)
        layoutTop.addWidget(self.labelFlag, 0)
        layoutTop.setSpacing(4)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(layoutTop, 0)
        layout.addLayout(self.body, 1)
        layout.addWidget(self.labelFoot, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self.labelTitle.setText(title)
        self._title = title

    @property
    def flag(self):
        return self._flag

    @flag.setter
    def flag(self, flag):
        if flag is not None:
            self.labelFlag.setText(flag)
            self.labelFlag.setVisible(True)
        else:
            self.labelFlag.setVisible(False)
        self._flag = flag

    @property
    def flagTip(self):
        return self._flagTip

    @flagTip.setter
    def flagTip(self, flagTip):
        if flagTip is not None:
            self.labelFlag.setToolTip(flagTip)
        else:
            self.labelFlag.setToolTip('')
        self._flagTip = flagTip

    @property
    def footer(self):
        return self._foot

    @footer.setter
    def footer(self, footer):
        self.labelFoot.setVisible(footer != '')
        self.labelFoot.setText(footer)
        self._foot = footer


class ToolDialog(QtWidgets.QDialog):
    """
    For use as the main window of a tool.
    Handles notification sub-dialogs.
    Asks for verification before closing.
    """
    def reject(self, force=False):
        """Called on dialog close or <ESC>"""
        if force:
            return self._reject()
        filter = self.filterReject()
        if filter is None:
            return self._reject()
        if not filter:
            return
        msgBox = QtWidgets.QMessageBox(self)
        msgBox.setWindowTitle(self.windowTitle())
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
        msgBox.setText('Are you sure you want to quit?')
        msgBox.setStandardButtons(
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Yes)
        confirm = self.msgShow(msgBox)
        if confirm == QtWidgets.QMessageBox.Yes:
            self._reject()

    def _reject(self):
        self.onReject()
        super().reject()

    def onReject(self):
        """Called when dialog is closed"""
        pass

    def filterReject(self):
        """Intercept reject events: True allows, False blocks, None rejects"""
        return True

    def msgCloseAll(self):
        """Rejects any open QMessageBoxes"""
        for widget in self.children():
            if widget.__class__ == QtWidgets.QMessageBox:
                widget.reject()

    def msgShow(self, dialog):
        """Exec given QMessageBox after closing all others"""
        self.msgCloseAll()
        return dialog.exec()

    def fail(self, exception):
        """Show exception dialog"""
        msgBox = QtWidgets.QMessageBox(self)
        msgBox.setWindowTitle(self.windowTitle())
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        msgBox.setText('An exception occured:')
        msgBox.setInformativeText(str(exception))
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
        self.msgShow(msgBox)
