from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox
from PyQt6.QtCore import Qt
from typing import Optional

class EditorWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Edit Form Data:")
        layout.addWidget(self.label)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Enter data here...")
        layout.addWidget(self.input_field)

        self.text_area = QTextEdit(self)
        self.text_area.setPlaceholderText("Additional details...")
        layout.addWidget(self.text_area)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_data)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_data(self):
        data = self.input_field.text()
        details = self.text_area.toPlainText()
        if not data:
            QMessageBox.warning(self, "Warning", "Input field cannot be empty.")
            return
        # Here you would typically save the data to the database
        QMessageBox.information(self, "Success", "Data saved successfully!")