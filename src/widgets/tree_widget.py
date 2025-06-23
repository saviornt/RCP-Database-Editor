from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtCore import Qt

class TreeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tree = QTreeWidget(self)
        self.tree.setHeaderLabels(["Collection Types"])
        self.layout.addWidget(self.tree)
        self.setLayout(self.layout)
        self.populate_tree()

    def populate_tree(self):
        collection_types = [
            "Race",
            "Class",
            "Profession"
        ]
        for collection in collection_types:
            item = QTreeWidgetItem(self.tree, [collection])
            self.tree.addTopLevelItem(item)

    def get_selected_collection(self):
        selected_items = self.tree.selectedItems()
        if selected_items:
            return selected_items[0].text(0)
        else:
            QMessageBox.warning(self, "Selection Error", "No collection selected.")
            return None