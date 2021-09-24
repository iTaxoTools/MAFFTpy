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

"""Extensions for QStateMachines"""


from PySide6 import QtStateMachine


class TaggedEvent(QtStateMachine.QStateMachine.SignalEvent):
    """Wraps a SignalEvent meant for a TaggedTransition."""

    def __init__(self, event):
        if self.isValidCast(event):
            super().__init__(event.sender(), event.signalIndex(), [])
            self.tag = event.arguments()[0]
            self.args = event.arguments()[1]
            self.kwargs = event.arguments()[2]
        else:
            super().__init__(None, -1, [])
            self.type = event.type
            self.tag = None
            self.args = []
            self.kwargs = {}

    @staticmethod
    def isValidCast(event):
        return (isinstance(event, QtStateMachine.QStateMachine.SignalEvent)
                and len(event.arguments()) == 3
                and isinstance(event.arguments()[1], list)
                and isinstance(event.arguments()[2], dict)
                )


class TaggedTransition(QtStateMachine.QSignalTransition):
    """Only catches TaggedEvent with matching tags."""

    def __init__(
        self,
        signal, # created with: Signal(object, list, dict)
        tag,
        filter=lambda e: True,
        effect=lambda e: None,
    ):
        print('testmesignal!', signal, dir(signal))
        super().__init__(signal)
        self.tag = tag
        self.filter = filter
        self.effect = effect

    def eventTest(self, event):
        taggedEvent = TaggedEvent(event)
        if self.tag == taggedEvent.tag:
            return self.filter(event)
        return False

    def onTransition(self, event):
        taggedEvent = TaggedEvent(event)
        self.effect(taggedEvent)
        super().onTransition(event)
