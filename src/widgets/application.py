"""
Main application window widget.
"""
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QStatusBar, QMenuBar, QListWidgetItem, QLabel, QSplitter, QMessageBox
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtCore import Qt
from typing import Optional, List, Dict, Any
from .canvas import Canvas
from .nav_panel import NavPanel
from .form_card import FormCard
from db.mongo_handler import MongoDBHandler
from forms.form_data import COLLECTION_TYPES
from utils.helpers import refresh_app

class ApplicationWindow(QMainWindow):
    """Main application window for the RCP Database Editor."""
    def __init__(self, db_handler: MongoDBHandler, parent: Optional[QMainWindow] = None) -> None:
        super().__init__(parent)
        self.db_handler = db_handler
        self.setWindowTitle("RCP Database Editor")
        self.resize(1200, 800)

        # Central widget and layout
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # Instantiate widgets
        self.nav_panel = NavPanel(self)
        self.canvas = Canvas(self)
        self.form_card = FormCard(self)

        # Add widgets to splitter (left: nav_panel, right: canvas)
        splitter.addWidget(self.nav_panel)
        splitter.addWidget(self.canvas)
        splitter.setSizes([200, 1000])

        # Menu bar
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # File menu
        file_menu = self.menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = self.menu_bar.addMenu("Edit")
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        edit_menu.addAction(settings_action)
        edit_menu.addSeparator()
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(lambda: refresh_app(self))
        edit_menu.addAction(refresh_action)
        
        # Collections menu
        collections_menu = self.menu_bar.addMenu("Collections")
        self.collection_actions = {}
        for collection in ["Race", "Class", "Profession"]:
            action = QAction(collection, self)
            action.triggered.connect(lambda checked, c=collection: self.on_collection_selected(c))
            collections_menu.addAction(action)
            self.collection_actions[collection] = action
        
        # Database menu
        db_menu = self.menu_bar.addMenu("Database")
        test_conn_action = QAction("Test Connection", self)
        test_conn_action.triggered.connect(self.open_db_test_conn_dialog)
        db_menu.addAction(test_conn_action)
        
        # Status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_left = QLabel(f"Database: {self.db_handler.db_name}")
        self.status_right = QLabel()
        self.status_right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.status_bar_layout = QHBoxLayout()
        self.status_bar_layout.addWidget(self.status_left)
        self.status_bar_layout.addStretch(1)
        self.status_bar_layout.addWidget(self.status_right)
        status_bar_widget = QWidget()
        status_bar_widget.setLayout(self.status_bar_layout)
        self.status_bar.addPermanentWidget(status_bar_widget, 1)
        self.update_connection_status()

        # Connect signals
        # Remove: self.canvas.list_widget.itemClicked.connect(self.on_document_selected)
        # The org chart is now interactive via box widgets, not a list widget.
        # If you want to handle clicks, connect signals from OrgChartBox widgets in Canvas.

        # State
        self.current_collection: Optional[str] = None
        self.documents: List[Dict[str, Any]] = []

        # Set default collection to Race on startup
        self.on_collection_selected("Race")

    def update_connection_status(self) -> None:
        uri = self.db_handler.uri
        # Remove username and password from URI if present
        if '@' in uri:
            # Remove credentials
            uri = uri.split('@', 1)[-1]
            if '://' in uri:
                uri = uri.split('://', 1)[-1]
            uri = 'mongodb://' + uri
        if self.db_handler.client is not None and self.db_handler.db is not None:
            self.status_right.setText(f'<span style="color:green;">Connected to {uri}</span>')
        else:
            self.status_right.setText(f'<span style="color:red;">Disconnected</span>')

    def on_collection_selected(self, collection: str) -> None:
        self.current_collection = collection
        # Fetch documents from DB
        if self.db_handler.db is not None:
            docs = list(self.db_handler.db[collection].find())
        else:
            docs = []
        self.documents = docs
        self.canvas.update_documents(collection, docs)
        self.nav_panel.update_panel(collection, docs)
        self.status_bar.showMessage(f"Loaded {len(docs)} documents from {collection}")

    def on_document_selected(self, item: QListWidgetItem) -> None:
        doc = item.data(256)  # Qt.UserRole = 256
        self.form_card.load_document(doc)

    def refresh(self) -> None:
        """Reload the current collection and update the UI."""
        if self.current_collection:
            self.on_collection_selected(self.current_collection)

    def open_settings_dialog(self):
        from .settings_dialog import SettingsDialog
        dlg = SettingsDialog(self)
        dlg.exec()

    def open_db_test_conn_dialog(self):
        from .dbTestConn_dialog import DBTestConnDialog
        dlg = DBTestConnDialog(self.db_handler, self)
        dlg.exec()
