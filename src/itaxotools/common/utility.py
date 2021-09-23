
"""Utility classes and functions"""


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


# these will be removed

from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtStateMachine
from PySide6 import QtGui

from contextlib import contextmanager

import sys, os
import multiprocessing

from . import io


class NamedEvent(QtCore.QEvent):
    """Custom event for use in state machines"""
    userEvent = QtCore.QEvent.registerEventType()
    events = set()
    def __init__(self, name, *args, **kwargs):
        """Pass name and args"""
        super().__init__(QtCore.QEvent.Type(self.userEvent))
        self.name = name
        self.args = args
        self.kwargs = kwargs
        # Avoid garbage-collection
        NamedEvent.events.add(self)

class NamedTransition(QtStateMachine.QAbstractTransition):
    """Custom transition for use in state machines"""
    def __init__(self, name):
        """Only catch events with given name"""
        super().__init__()
        self.name = name
    def eventTest(self, event):
        """Check for NamedEvents"""
        if event.type() == NamedEvent.userEvent:
            return event.name == self.name
        return False
    def onTransition(self, event):
        """Override virtual function"""
        # Allow event to be garbage-collected
        # NamedEvent.events.remove(event)
