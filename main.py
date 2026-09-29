import PySide6.QtWidgets as QtWidgets
from login import Loginapp

if __name__ == "__main__":
    app=QtWidgets.QApplication([])
    window=Loginapp()
    window.show()
    app.exec()