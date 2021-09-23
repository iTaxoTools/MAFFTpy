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

"""Simple frames"""


from PySide6 import QtWidgets


class Frame(QtWidgets.QFrame):
    """A slightly darker than the background frame"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self.setStyleSheet("""
            Frame {
                background: rgba(0, 0, 0, 4);
                border: 1px solid rgba(0, 0, 0, 24);
            }""")


class VLineSeparator(QtWidgets.QFrame):
    """Vertical line separator"""
    def __init__(self, width=2):
        super().__init__()
        self.setFixedWidth(width)
        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setStyleSheet("""
            background: palette(Mid);
            border: none;
            margin: 4px;
            """)


class HLineSeparator(QtWidgets.QFrame):
    """Vertical line separator"""
    def __init__(self, height=2):
        super().__init__()
        self.setFixedHeight(height)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setStyleSheet("""
            background: palette(Mid);
            border: none;
            margin: 4px;
            """)
