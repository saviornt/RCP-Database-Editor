"""
Dialog for confirming deletion of a document in the active collection.
"""
from typing import Callable, Optional, Any
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget, QMessageBox
from utils.helpers import refresh_app

class DeleteDialog(QDialog):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        on_delete: Optional[Callable[[], Any]] = None,
        documents: Optional[list] = None,
        *args,
        **kwargs
    ):
        super().__init__(parent, *args, **kwargs)
        self.setWindowTitle("Delete Document(s)")
        self.on_delete = on_delete
        self._refresh_parent = parent
        self.documents = documents or []

        layout = QVBoxLayout()
        if len(self.documents) == 1:
            name = self.documents[0].get('displayName', self.documents[0].get('full_tag', ''))
            label = QLabel(f"Are you sure you want to delete this document?\n\n{name}\n\n")
        else:
            names = [d.get('displayName', d.get('full_tag', '')) for d in self.documents if d]
            if names:
                label = QLabel(f"Are you sure you want to delete these {len(self.documents)} documents?\n\n" + ''.join(f'{n}\n' for n in names) + "\n\n")
            else:
                label = QLabel("Are you sure you want to delete these documents?")
        label.setWordWrap(True)
        layout.addWidget(label)

        button_layout = QHBoxLayout()
        yes_button = QPushButton("Yes")
        no_button = QPushButton("No")
        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        yes_button.clicked.connect(self.confirm_delete)
        no_button.clicked.connect(self.reject)

    def confirm_delete(self):
        if callable(self.on_delete):
            self.on_delete()  # No arguments, for compatibility
        parent = self.parent()
        while parent and not hasattr(parent, 'db_handler'):
            parent = parent.parent()
        if parent:
            refresh_app(parent)
        # Show informational dialog after deletion
        info_box = QMessageBox(self)
        info_box.setIcon(QMessageBox.Icon.Information)
        info_box.setWindowTitle("Deleted")
        if len(self.documents) == 1:
            name = self.documents[0].get('displayName', self.documents[0].get('full_tag', ''))
            info_box.setText(f"Deleted 1 document: {name}")
        else:
            names = [d.get('displayName', d.get('full_tag', '')) for d in self.documents if d]
            if names:
                info_box.setText(f"Deleted {len(self.documents)} documents:\n\n" + '\n'.join(names))
            else:
                info_box.setText(f"Deleted {len(self.documents)} documents.\n")
        info_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        info_box.buttonClicked.connect(self.accept)
        info_box.exec()
