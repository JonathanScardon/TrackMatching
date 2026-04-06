import pyqtgraph as pg
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QRadioButton,
    QVBoxLayout, QWidget
)
class CandidateGraph(QWidget):
    '''
    position (y-left - y-right) vs time graph
    '''

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.plot_graph = pg.PlotWidget()
        self.plot_graph.setBackground('w')

        layout = QVBoxLayout()
        layout.addWidget(self.plot_graph)
        layout.addStretch()
        self.setLayout(layout)

    def update(self, x, y):
        self.plot_graph.plot(x, y)

    def clear(self):
        self.plot_graph.clear()