
"""GUI entry point"""


def run():
    """
    Show the MAFFTpy window and enter the main event loop.
    Imports are made locally to optimize multiprocessing.
    """

    import sys
    import pathlib
    from PySide6 import QtWidgets
    from PySide6 import QtCore
    from .main import Main

    def init(self):
        if len(sys.argv) >= 2:
            file = pathlib.Path(sys.argv[1])
            self.handleOpen(fileName=str(file))

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    main = Main(init=init)
    main.setWindowFlags(QtCore.Qt.Window)
    main.show()
    sys.exit(app.exec_())
