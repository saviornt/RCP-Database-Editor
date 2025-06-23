"""
Stub settings dialog for future configuration options.
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(500, 600)  # Match NewDialog dimensions
        layout = QVBoxLayout(self)
        label = QLabel("TO DO", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 32px; color: #888; font-weight: bold;")
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        btn_ok = QPushButton("OK", self)
        btn_ok.setMinimumWidth(100)
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)
