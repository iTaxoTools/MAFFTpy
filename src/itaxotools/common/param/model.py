# -----------------------------------------------------------------------------
# Param - Parameter model
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


"""
Parameter model for PySide6
"""

from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex

from . import Field, Group


class Model(QAbstractItemModel):

    DataRole = Qt.ItemDataRole.UserRole
    columns = ['key', 'label', 'value', 'doc',
               'list', 'range', 'type', 'default']

    def __init__(self, group, parent=None):
        super().__init__(parent)
        self.rootItem = group
        self.headers = list(self.columns)

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parentItem = self.rootItem
        if parent.isValid():
            parentItem = parent.internalPointer()
        try:
            keys = list(parentItem._children.keys())
            key = keys[row]
            childItem = parentItem[key]
        except KeyError:
            return QModelIndex()
        return self.createIndex(row, column, childItem)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        childItem = index.internalPointer()
        parentItem = childItem._parent
        if parentItem == self.rootItem or parentItem is None:
            return QModelIndex()
        grandParentItem = parentItem._parent
        keys = list(grandParentItem._children.keys())
        row = keys.index(parentItem.key)
        return self.createIndex(row, 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0
        parentItem = self.rootItem
        if parent.isValid():
            parentItem = parent.internalPointer()
        if isinstance(parentItem, Group):
            return len(parentItem._children)
        return 0

    def columnCount(self, parent):
        return len(self.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            try:
                attr = self.columns[index.column()]
                return str(getattr(item, attr))
            except AttributeError:
                return None
        elif (role == Qt.ItemDataRole.ToolTipRole or
                role == Qt.ItemDataRole.WhatsThisRole):
            return item.doc
        elif role == self.DataRole:
            return item
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        try:
            if index.isValid() and role == Qt.ItemDataRole.EditRole:
                item = index.internalPointer()
                item.value = item.type(value)
                roles = [Qt.ItemDataRole.DisplayRole, self.DataRole]
                self.dataChanged.emit(index, index, roles)
                return True
            return False
        except (ValueError, TypeError) as e:
            self.setDataError = str(e)
            return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        item = index.internalPointer()
        flag = Qt.ItemFlag.NoItemFlags
        if (isinstance(item, Field) and
                self.columns[index.column()] == 'value'):
            flag = Qt.ItemFlag.ItemIsEditable
        return super().flags(index) | flag

    def headerData(self, section, orientation,
                   role=Qt.ItemDataRole.DisplayRole):
        if (orientation == Qt.Orientation.Horizontal and
                role == Qt.ItemDataRole.DisplayRole):
            return self.headers[section]
        return None

    def setHeaderData(self, section, orientation, value,
                      role=Qt.ItemDataRole.DisplayRole):
        if (orientation == Qt.Orientation.Horizontal and
                role == Qt.ItemDataRole.DisplayRole):
            self.headers[section] = value
            self.headerDataChanged.emit(orientation, section, section)
            return True
        return False

    def paramIndex(self, param):
        if param._parent is None:
            return QModelIndex()
        keys = list(param._parent._children.keys())
        row = keys.index(param.key)
        return self.createIndex(row, 0, param)

    def resetParams(self, index=QModelIndex()):
        rows = self.rowCount(index)
        if rows == 0:
            return
        for row in range(0, rows):
            childIndex = self.index(row, 0, index)
            childItem = childIndex.internalPointer()
            if isinstance(childItem, Field):
                childItem.value = childItem.default
            self.resetParams(childIndex)
        topLeft = self.index(0, 0, index)
        bottomRight = self.index(rows - 1, 0, index)
        roles = [Qt.ItemDataRole.DisplayRole, self.DataRole]
        self.dataChanged.emit(topLeft, bottomRight, roles)
