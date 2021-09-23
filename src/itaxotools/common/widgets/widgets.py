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

"""Miscellaneous widgets"""

from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui


class TextEditLogger(QtWidgets.QPlainTextEdit):
    """Thread-safe log display in a QPlainTextEdit"""
    _appendSignal = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)
        self._appendSignal.connect(self._appendTextInline)

    @QtCore.Slot(object)
    def _appendTextInline(self, text):
        """Using signals ensures thread safety"""
        self.moveCursor(QtGui.QTextCursor.End)
        self.insertPlainText(text)
        sb = self.verticalScrollBar()
        sb.setValue(sb.maximum())
        self.moveCursor(QtGui.QTextCursor.End)

    def append(self, text):
        """Call this to append text to the widget"""
        self._appendSignal.emit(str(text))


class SearchWidget(QtWidgets.QLineEdit):
    """Embedded line edit with search button"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPlaceholderText('Search')
        self.setStyleSheet(
            """
            SearchWidget {
                padding: 4px;
                padding-left: 4px;
                border: 1px solid Palette(Mid);
                border-radius: 0;
                min-width: 160px;
                }
            SearchWidget:focus {
                border: 1px solid Palette(Highlight);
                }
            """)

    def setSearchAction(self, action):
        """Bind a QAction to the widget"""
        self.returnPressed.connect(action.trigger)
        self.addAction(action, QtWidgets.QLineEdit.TrailingPosition)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        QtCore.QTimer.singleShot(0, self.selectAll)
