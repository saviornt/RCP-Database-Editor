from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QContextMenuEvent

class OrgChartBox(QFrame):
    boxDoubleClicked = pyqtSignal(str)  # full_tag as identifier
    boxActionRequested = pyqtSignal(str, str)  # (full_tag, action: 'edit'|'create_child')

    def __init__(self, display_name: str, full_tag: str, description: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.full_tag = full_tag
        self.setFrameShape(QFrame.Shape.Box)
        self.setLineWidth(2)
        self.setStyleSheet("background: white; border-radius: 8px;")
        self.setFixedSize(120, 120)  # Make the box square and fixed size
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Header area (top 1/3)
        header_widget = QWidget(self)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(8, 8, 8, 0)
        header_layout.setSpacing(2)
        header = QLabel(display_name)
        header.setStyleSheet("font-weight: bold; font-size: 16px; color: #3a3a7a; background: #e0e6f8;") # border-top-left-radius: 8px; border-top-right-radius: 8px;
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel(full_tag)
        subtitle.setStyleSheet("font-style: italic; font-size: 11px; color: #555; background: #e0e6f8;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(header)
        header_layout.addWidget(subtitle)
        header_widget.setFixedHeight(60)
        layout.addWidget(header_widget, 1)
        # Description area (bottom 2/3)
        desc_widget = QWidget(self)
        desc_layout = QVBoxLayout(desc_widget)
        desc_layout.setContentsMargins(8, 0, 8, 8)
        desc_layout.setSpacing(0)
        desc = QLabel(description)
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        desc.setStyleSheet("font-size: 12px; margin-top: 6px; color: #2a2a2a; background: #f8f8fa; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;")
        desc_layout.addWidget(desc)
        desc_widget.setMinimumHeight(60)
        layout.addWidget(desc_widget, 2)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.boxDoubleClicked.emit(self.full_tag)
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #fff;
                color: #111;
                border: 1px solid #888;
                border-radius: 6px;
                padding: 4px;
                box-shadow: 0px 4px 16px rgba(0,0,0,0.18);
            }
            QMenu::item {
                background: transparent;
                color: #111;
                padding: 6px 24px 6px 24px;
            }
            QMenu::item:selected {
                background: #e0e6f8;
                color: #111;
            }
        """)
        edit_action = menu.addAction("Edit")
        create_child_action = menu.addAction("Create Child")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        action = menu.exec(event.globalPos())
        if action == edit_action:
            self.boxActionRequested.emit(self.full_tag, 'edit')
        elif action == create_child_action:
            self.boxActionRequested.emit(self.full_tag, 'create_child')
        elif action == delete_action:
            self.boxActionRequested.emit(self.full_tag, 'delete')
