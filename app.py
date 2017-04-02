from gui.MainWindow import Application
from PyQt5.QtWidgets import QApplication
import sys
import logging

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(asctime)s %(name)s %(message)s',
                        filename='test.log',
                        level=logging.DEBUG
                        )
    logging.debug("program started")
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    appstatus = app.exec_()
    logging.debug("program terminated")
    sys.exit(appstatus)
