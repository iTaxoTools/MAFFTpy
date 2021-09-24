# -----------------------------------------------------------------------------
# Param - Parameter view
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
Parameter view for PySide6
"""

from PySide6.QtCore import Qt, QModelIndex, Signal, QRect, QSize
from PySide6.QtWidgets import (
    QFrame, QLabel, QLineEdit, QCheckBox, QScrollArea, QMessageBox,
    QComboBox, QGroupBox, QVBoxLayout, QHBoxLayout, QLayout, QPushButton)
from PySide6.QtGui import QValidator, QIntValidator, QDoubleValidator

from . import Field


class FieldLayout(QLayout):
    """Last widget added has the same width for all instances"""
    def __init__(self, label, widget, parent=None):
        super().__init__(parent)
        self.itemList = []
        self.www = 100
        self.gap = 6
        self.addWidget(label)
        self.addWidget(widget)

    def addItem(self, item):
        self.itemList.append(item)

    def itemAt(self, index):
        try:
            return self.itemList[index]
        except IndexError:
            return None

    def takeAt(self, index):
        return self.itemList.pop(index)

    def count(self):
        return len(self.itemList)

    def sizeHint(self):
        w, h = 0, 0
        for item in self.itemList:
            h = max(h, item.sizeHint().height())
        w += self.itemList[0].sizeHint().width()
        w += self.gap + self.www + 10
        return QSize(w, h)

    def minimumSize(self):
        if self.itemList:
            return self.itemList[-1].sizeHint()
        else:
            return QSize(0, 0)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        w = rect.width()
        if w >= self.www:
            div = rect.right() - self.www
            rl = QRect(rect)
            rl.setRight(div - self.gap)
            self.itemList[0].setGeometry(rl)
            rw = QRect(rect)
            rw.setLeft(div)
            self.itemList[-1].setGeometry(rw)


class FieldWidget(QFrame):

    # Emit (_index, value) when user changes the field value
    dataChanged = Signal(object, object)

    def __init__(self, index, field, view, parent=None):
        super().__init__(parent)
        view.dataChanged.connect(self.onModelDataChange)
        self.dataChanged.connect(view.onWidgetDataChange)
        self._index = index
        self._field = field
        self._view = view

    def onModelDataChange(self, index):
        """Refresh data if model index was updated"""
        if index == self._index:
            self.refreshData()

    def refreshData(self):
        """Called by view when field value is changed"""
        raise NotImplementedError()


class BoolWidget(FieldWidget):

    dataChanged = Signal(object, object)

    def __init__(self, index, field, view, parent=None):
        super().__init__(index, field, view, parent)
        self.checkbox = QCheckBox()
        self.checkbox.setText(self._field.label)
        self.checkbox.stateChanged.connect(self.onDataChange)
        self.checkbox.setToolTip(self._field.doc)
        self.refreshData()
        layout = QHBoxLayout()
        layout.addWidget(self.checkbox)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def onDataChange(self, state):
        v = self.checkbox.isChecked()
        self.dataChanged.emit(self._index, v)

    def refreshData(self):
        data = self._field.value
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(data)
        self.checkbox.blockSignals(False)

    def setFocus(self, reason=Qt.OtherFocusReason):
        self.checkbox.setFocus(reason)

    def sizeHint(self):
        return self.checkbox.sizeHint() + QSize(5, 0)


class EmptyOrIntValidator(QIntValidator):
    def validate(self, input, pos):
        if not input:
            return QValidator.Acceptable
        return super().validate(input, pos)


class EmptyOrDoubleValidator(QDoubleValidator):
    def validate(self, input, pos):
        if not input:
            return QValidator.Acceptable
        return super().validate(input, pos)


class EntryWidget(FieldWidget):

    def __init__(self, index, field, view, parent=None):
        super().__init__(index, field, view, parent)
        self.label = QLabel(self._field.label + ': ')
        self.entry = QLineEdit()
        self.entry.editingFinished.connect(self.onDataChange)
        if issubclass(self._field.type, int):
            self.entry.setValidator(EmptyOrIntValidator(self.entry))
        elif issubclass(self._field.type, float):
            self.entry.setValidator(EmptyOrDoubleValidator(self.entry))
        self.label.setToolTip(self._field.doc)
        self.entry.setToolTip(self._field.doc)
        self.refreshData()
        layout = FieldLayout(self.label, self.entry)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def onDataChange(self):
        v = self.entry.text()
        self.dataChanged.emit(self._index, v)

    def refreshData(self):
        self.entry.setText(str(self._field.value))

    def setFocus(self, reason=Qt.OtherFocusReason):
        self.entry.setFocus(reason)


class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event):
        if self.hasFocus:
            event.ignore()
        else:
            self.wheelEvent(event)


class ListWidget(FieldWidget):

    def __init__(self, index, field, view, parent=None):
        super().__init__(index, field, view, parent)
        self.label = QLabel(self._field.label + ': ')
        self.combo = NoWheelComboBox()
        # self.combo.setFocusPolicy(Qt.StrongFocus)
        self.combo.currentIndexChanged.connect(self.onDataChange)
        self.populateCombo()
        self.label.setToolTip(self._field.doc)
        self.combo.setToolTip(self._field.doc)
        layout = FieldLayout(self.label, self.combo)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def populateCombo(self):
        self.combo.clear()
        if isinstance(self._field.list, list):
            for k in self._field.list:
                self.combo.addItem(str(k), k)
        elif isinstance(self._field.list, dict):
            for k, v in self._field.list.items():
                self.combo.addItem(v, k)
        self.refreshData()

    def onDataChange(self):
        if self.combo.count() > 0:
            v = self.combo.currentData()
            self.dataChanged.emit(self._index, v)

    def refreshData(self):
        data = self._field.value
        i = list(self._field.list).index(data)
        self.combo.blockSignals(True)
        self.combo.setCurrentIndex(i)
        self.combo.blockSignals(False)

    def setFocus(self, reason=Qt.OtherFocusReason):
        self.combo.setFocus(reason)


class View(QScrollArea):
    """Widget-based view for param.Model"""
    # Emited for every index when model data change
    dataChanged = Signal(object)

    def __init__(self, model=None, showResetButton=True, parent=None):
        super().__init__(parent)
        self.showResetButton = showResetButton
        self._model = None
        self._rootIndex = QModelIndex()
        self._widgets = dict()
        self._customParamClass = dict()
        self.setWidgetResizable(False)
        if model is not None:
            self.setModel(model)

    def rootIndex(self):
        return self._rootIndex

    def setRootIndex(self, index):
        self._rootIndex = index
        self.draw()

    def model(self):
        return self._model

    def setModel(self, model):
        self._widgets = dict()
        self._model = model
        model.dataChanged.connect(self.onModelDataChange)
        self.setRootIndex(QModelIndex())
        self.draw()

    def draw(self):
        widget = self._populate(self._rootIndex, 0)
        self.setWidget(widget)
        widget.setStyleSheet("""
            FieldWidget[depth="1"] {
                margin-left: 1px;
                margin-right: 10px;
                }
            QGroupBox:!flat {
                background-color: rgba(0,0,0,0.02);
                border: 1px solid Palette(Mid);
                margin-top: 28px;
                padding: 0px;
                }
            QGroupBox::title:!flat {
                color: Palette(Text);
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px -1px;
                }
            QGroupBox:flat {
                border-top: 1px solid Palette(Mid);
                border-left: 0px;
                border-bottom: 0px;
                margin-top: 24px;
                margin-right: -20px;
                padding-left: 12px;
                padding-bottom: 0px;
                }
            QGroupBox::title:flat {
                color: Palette(Text);
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px -1px;
                }
        """)
        widget.show()

    def onInvalidValue(self, error):
        """Called when a field value was invalid"""
        QMessageBox.warning(self, 'Warning', error)

    def addCustomParamWidget(self, param, _class):
        """The view for `param` will be an instance of `_class`"""
        self._customParamClass[id(param)] = _class
        self.draw()

    def onModelDataChange(self, topLeft, bottomRight, roles):
        """Send signal updates for all indices changed"""
        if bottomRight.parent() != topLeft.parent():
            raise RuntimeError(
                'View: Model dataChanged items have different parents')
        parent = topLeft.parent()
        top = topLeft.row()
        bottom = bottomRight.row()
        for row in range(top, bottom+1):
            index = self._model.index(row, 0, parent)
            self.dataChanged.emit(index)

    def onWidgetDataChange(self, index, data):
        """Update model"""
        if not self._model.setData(index, data):
            self.onInvalidValue(self._model.setDataError)
            self.sender().refreshData()
            self.sender().setFocus()
            # QTimer.singleShot(0, self.sender().setFocus)

    def _fieldWidget(self, index, field, depth=0):
        """Generate and return an appropriate widget for the field"""
        type_to_widget = {
            bool: BoolWidget,
            float: EntryWidget,
            str: EntryWidget,
            int: EntryWidget,
            }
        if id(field) in self._customParamClass:
            _class = self._customParamClass[id(field)]
            widget = _class(index, field, self)
        elif field.list:
            widget = ListWidget(index, field, self)
        elif field.type in type_to_widget.keys():
            widget = type_to_widget[field.type](index, field, self)
        else:
            widget = EntryWidget(index, field, self)
        widget.setProperty('depth', depth)
        return widget

    def _populate(self, index, depth=0):
        """Recursively populate and return a widget with params"""
        data = self._model.data(index, self._model.DataRole)

        if isinstance(data, Field):
            return self._fieldWidget(index, data, depth)

        if depth == 0:
            widget = QFrame()
            layout = QVBoxLayout()
        # elif depth == 1:
        #     widget = QGroupBox(data.label)
        #     layout = QVBoxLayout()
        else:
            widget = QGroupBox(data.label)
            widget.setFlat(True)
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 6, 0, 3)

        rows = self._model.rowCount(index)
        for row in range(0, rows):
            childIndex = self._model.index(row, 0, index)
            child = self._populate(childIndex, depth+1)
            layout.addWidget(child)

        if self.showResetButton and depth == 0:
            resetButton = QPushButton('Reset to defaults')
            resetButton.setAutoDefault(False)
            resetButton.clicked.connect(self._resetParams)
            layout.addWidget(resetButton)

        widget.setLayout(layout)
        return widget

    def _resetParams(self, checked=False):
        self._model.resetParams()
