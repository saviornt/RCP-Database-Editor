"""
Form card widget for displaying and editing a single document.
"""
from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit
from typing import Optional, Dict, Any

class FormCard(QWidget):
    """Widget for displaying and editing a single form/document."""
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._layout = QFormLayout(self)
        self.fields: Dict[str, QLineEdit] = {}
        self.setLayout(self._layout)
        self.current_doc: Optional[Dict[str, Any]] = None

    def load_document(self, doc: Dict[str, Any]) -> None:
        self.current_doc = doc
        # Remove old fields
        for field in self.fields.values():
            self._layout.removeWidget(field)
            field.deleteLater()
        self.fields.clear()
        # Add fields for each key in doc
        for key, value in doc.items():
            if key == '_id':
                continue
            line_edit = QLineEdit(str(value), self)
            self.fields[key] = line_edit
            self._layout.addRow(key, line_edit)
