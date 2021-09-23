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

"""Graphical widgets and GUI elements"""


from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6 import QtSvg

import re


class VectorPixmap(QtGui.QPixmap):
    """A colored vector pixmap"""
    def __init__(self, fileName, size=None, colormap=None):
        """
        Load an SVG resource file and replace colors according to
        provided dictionary `colormap`. Only fill and stroke is replaced.
        Also scales the pixmap if a QSize is provided.
        """
        data = self.loadAndMap(fileName, colormap)

        renderer = QtSvg.QSvgRenderer(data)
        size = renderer.defaultSize() if size is None else size
        super().__init__(size)
        self.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(self)
        renderer.render(painter)
        painter.end()

    @staticmethod
    def loadAndMap(fileName, colormap):
        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QIODevice.ReadOnly):
            raise FileNotFoundError('Vector resource not found: ' + fileName)
        text = file.readAll().data().decode()
        file.close()

        if colormap is not None:
            regex = '(?P<color>'
            regex += '|'.join(map(re.escape, colormap.keys()))+')'
            text = re.sub(regex, lambda mo: colormap[mo.group('color')], text)

        return QtCore.QByteArray(text.encode())


class VectorIcon(QtGui.QIcon):
    """A colored vector icon"""
    def __init__(self, fileName, colormap_modes):
        """Create pixmaps with colormaps matching the dictionary modes"""
        super().__init__()
        for mode in colormap_modes.keys():
            pixmap = VectorPixmap(fileName, colormap=colormap_modes[mode])
            self.addPixmap(pixmap, mode)


class ScalingImage(QtWidgets.QLabel):
    """Keep aspect ratio, width adjusts with height"""
    def __init__(self, pixmap=None):
        """Remember given pixmap and ratio"""
        super().__init__()
        self.setScaledContents(False)
        self._polished = False
        self._logo = None
        self._ratio = 0
        if pixmap is not None:
            self.logo = pixmap

    @property
    def logo(self):
        return self._logo

    @logo.setter
    def logo(self, logo):
        self._logo = logo
        self._ratio = logo.width()/logo.height()
        self._scale()

    def _scale(self):
        """Create new pixmap to match new sizes"""
        if self._logo is None:
            return
        h = self.height()
        w = h * self._ratio
        self.setPixmap(self._logo.scaled(
            w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def minimumSizeHint(self):
        return QtCore.QSize(1, 1)

    def sizeHint(self):
        if self._polished is True and self._ratio != 0:
            h = self.height()
            return QtCore.QSize(h * self._ratio, h)
        else:
            return QtCore.QSize(1, 1)

    def resizeEvent(self, event):
        self._scale()
        super().resizeEvent(event)

    def event(self, ev):
        """Let sizeHint know that sizes are now real"""
        if ev.type() == QtCore.QEvent.PolishRequest:
            self._polished = True
            self.updateGeometry()
        return super().event(ev)
