from PyQt6.QtWidgets import QPushButton, QLineEdit, QLabel, QVBoxLayout, QWidget

class CustomButton(QPushButton):
    def __init__(self, text: str, parent: QWidget = None):
        super().__init__(text, parent)
        self.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px;")
        self.setFixedHeight(40)

class CustomLineEdit(QLineEdit):
    def __init__(self, placeholder: str, parent: QWidget = None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 10px;")

class CustomLabel(QLabel):
    def __init__(self, text: str, parent: QWidget = None):
        super().__init__(text, parent)
        self.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")

class CustomFormLayout(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

    def add_field(self, label_text: str, input_widget: QWidget):
        label = CustomLabel(label_text, self)
        self.layout.addWidget(label)
        self.layout.addWidget(input_widget)