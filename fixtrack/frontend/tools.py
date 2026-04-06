import os

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QRadioButton,
    QVBoxLayout, QWidget
)

from fixtrack.backend.candidates import Candidates

class Tools(QWidget):
    #save button
    #undo / redo buttons
    fname_save = os.path.join(os.path.dirname(__file__), "icons", "save.svg")
    fname_undo = os.path.join(os.path.dirname(__file__), "icons", "rotate-ccw.svg")
    fname_redo = os.path.join(os.path.dirname(__file__), "icons", "rotate-cw.svg")

    def __init__(self, parent):

        QWidget.__init__(self, parent)
        self._parent = parent

        self.buttons = []
        hl1 = QHBoxLayout()

        self.btn_undo = QPushButton(self)
        self.btn_undo.setToolTip("Undo last action Ctrl+Z")
        self.btn_undo.setIcon(QtGui.QIcon(QtGui.QPixmap(self.fname_undo)))
        self.btn_undo.clicked.connect(self.cb_btn_undo)
        self.btn_undo.setFocusPolicy(QtCore.Qt.NoFocus)
        self.btn_undo.setMaximumWidth(70)
        hl1.addWidget(self.btn_undo)
        self.buttons.append(self.btn_undo)

        self.btn_redo = QPushButton(self)
        self.btn_redo.setToolTip("Redo last action Ctrl+Shift+Z")
        self.btn_redo.setIcon(QtGui.QIcon(QtGui.QPixmap(self.fname_redo)))
        self.btn_redo.clicked.connect(self.cb_btn_redo)
        self.btn_redo.setFocusPolicy(QtCore.Qt.NoFocus)
        self.btn_redo.setMaximumWidth(100)
        hl1.addWidget(self.btn_redo)
        self.buttons.append(self.btn_redo)

        self.btn_save_candidates = QPushButton(self)
        self.btn_save_candidates.setToolTip("Save candidate file")
        self.btn_save_candidates.setIcon(QtGui.QIcon(QtGui.QPixmap(self.fname_save)))
        self.btn_save_candidates.clicked.connect(self.cb_btn_save_candidates)
        self.btn_save_candidates.setFocusPolicy(QtCore.Qt.NoFocus)
        self.btn_save_candidates.setMaximumWidth(50)
        hl1.addWidget(self.btn_save_candidates)
        self.buttons.append(self.btn_save_candidates)

        hl1.addStretch()
        self.setLayout(hl1)

    def cb_btn_save_candidates(self):
        #get filename
        ext = ".txt"

        if self._parent.canvas.fname_candidates is not None:
            savedir = os.path.dirname(self._parent.canvas.fname_tracks)
        else:
            savedir = os.path.dirname(self._parent.canvas.fname_video)

        fname, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            savedir,
            f"Text File (*{ext});;All Files (*)"
        )

        if not fname:
            return None

        if not fname.lower().endswith(ext):
            fname += ext


        self._parent.canvas.candidates.save(fname)

        print(f"Saved candidates as {fname}")
        return

    def cb_btn_undo(self):
        self._parent.canvas.candidates.undo()
        self._parent.canvas.visuals["tracks"].refresh_candidate_table()
    
    def cb_btn_redo(self):
        self._parent.canvas.candidates.redo()
        self._parent.canvas.visuals["tracks"].refresh_candidate_table()