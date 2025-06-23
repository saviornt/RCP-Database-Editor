from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtCore import Qt, QPoint

class OrgChartLines(QWidget):
    def __init__(self, box_widgets, children_map, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.box_widgets = box_widgets
        self.children_map = children_map
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.GlobalColor.black, 2)
        painter.setPen(pen)
        for parent_tag, children in self.children_map.items():
            parent_box = self.box_widgets.get(parent_tag)
            if not parent_box:
                continue
            parent_rect = parent_box.geometry()
            parent_bottom = QPoint(parent_rect.center().x(), parent_rect.bottom())
            for child_tag in children:
                child_box = self.box_widgets.get(child_tag)
                if not child_box:
                    continue
                child_rect = child_box.geometry()
                child_top = QPoint(child_rect.center().x(), child_rect.top())
                painter.drawLine(parent_bottom, child_top)
        painter.end()
