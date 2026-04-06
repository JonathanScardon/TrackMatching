from PyQt5 import QtCore, QtWidgets

class Table():
    def __init__(self):
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Track ID", "Start Frame", "End Frame", "Action"])