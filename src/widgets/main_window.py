from PyQt6.QtWidgets import QMainWindow, QMenuBar, QStatusBar, QToolBar, QAction, QWidget, QVBoxLayout
from .tree_widget import TreeWidget
from .editor_widget import EditorWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RCP Database Editor")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()

    def init_ui(self):
        self.create_menu_bar()
        self.create_status_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        self.tree_widget = TreeWidget()
        self.editor_widget = EditorWidget()

        layout.addWidget(self.tree_widget)
        layout.addWidget(self.editor_widget)

    def create_menu_bar(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def create_status_bar(self):
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)