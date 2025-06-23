"""
Dialog for testing and displaying MongoDB connection info.
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
import time

class DBTestConnDialog(QDialog):
    def __init__(self, db_handler, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Connection Info")
        layout = QVBoxLayout(self)
        start = time.time()
        connected = db_handler.connect()
        ping_ms = None
        if connected:
            try:
                ping_start = time.time()
                db_handler.client.admin.command('ping')
                ping_ms = int((time.time() - ping_start) * 1000)
            except Exception:
                ping_ms = None
        uri = db_handler.uri
        if '@' in uri:
            uri = uri.split('@', 1)[-1]
            if '://' in uri:
                uri = uri.split('://', 1)[-1]
            uri = 'mongodb://' + uri
        msg = f"<b>Database URI:</b> {uri}<br>"
        msg += f"<b>Database Name:</b> {db_handler.db_name}<br>"
        if connected:
            msg += f"<b>Status:</b> <span style='color:green;'>Connected</span><br>"
            if ping_ms is not None:
                msg += f"<b>Ping:</b> {ping_ms} ms"
        else:
            msg += f"<b>Status:</b> <span style='color:red;'>Disconnected</span>"
        label = QLabel()
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setText(msg)
        layout.addWidget(label)
        btn_box = QHBoxLayout()
        btn_ok = QPushButton("OK", self)
        btn_ok.setMinimumWidth(100)
        btn_ok.clicked.connect(self.accept)
        btn_box.addStretch(1)
        btn_box.addWidget(btn_ok)
        btn_box.addStretch(1)
        layout.addLayout(btn_box)
        self.setLayout(layout)
        # Optionally, show a status message in the parent status bar
        if hasattr(parent, 'status_bar'):
            if connected:
                parent.status_bar.showMessage("Successfully connected to MongoDB.", 3000)
            else:
                parent.status_bar.showMessage("Failed to connect to MongoDB.", 3000)
