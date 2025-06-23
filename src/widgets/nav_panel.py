"""
Navigation panel widget for the left side of the application.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QDialog
from PyQt6.QtCore import Qt
from typing import Optional, Any
from widgets.new_dialog import NewDialog

class NavPanel(QWidget):
    """Navigation panel for displaying tag hierarchy and create item."""
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self.label = QLabel(self)
        self._layout.addWidget(self.label)
        self.tree = QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self._layout.addWidget(self.tree)
        self.setLayout(self._layout)
        self.active_collection = None
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        if item.data(0, Qt.ItemDataRole.UserRole) == "create_new":
            self.show_create_dialog()

    def show_create_dialog(self) -> None:
        from models.pydantic_models import DocumentModel_Race, DocumentModel_Base
        collection = self.active_collection
        if collection == "Race":
            model_cls = DocumentModel_Race
        elif collection in ("Class", "Profession"):
            model_cls = DocumentModel_Base
        else:
            return
        dialog = NewDialog(collection, model_cls, self)
        # No need to call refresh_app here; NewDialog handles refresh after creation
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Optionally, select the newly added document in the tree
            parent_app = self.parent()
            if parent_app and hasattr(parent_app, 'documents'):
                docs = parent_app.documents
                if docs:
                    new_doc = docs[-1]
                    full_tag = new_doc.get('full_tag', '')
                    if full_tag.startswith(collection + "."):
                        nav_label = full_tag[len(collection) + 1:]
                    else:
                        nav_label = full_tag
                    for i in range(self.tree.topLevelItemCount()):
                        item = self.tree.topLevelItem(i)
                        if item.text(0) == nav_label:
                            self.tree.setCurrentItem(item)
                            break

    def update_panel(self, collection: str, docs: list[dict[str, Any]]) -> None:
        """Update the navigation panel for the selected collection and its documents as a tree."""
        self.active_collection = collection
        self.label.setText(f"{collection} Collection")
        self.tree.clear()
        # Add 'Create New' item
        create_item = QTreeWidgetItem([f"Create New {collection}"])
        create_item.setData(0, Qt.ItemDataRole.UserRole, "create_new")
        self.tree.addTopLevelItem(create_item)
        # Build a mapping from full_tag to doc
        tag_map = {doc.get('full_tag', ''): doc for doc in docs}
        # Helper to find or create a child item
        def find_or_create_child(parent, text):
            for i in range(parent.childCount()):
                item = parent.child(i)
                if item.text(0) == text:
                    return item
            new_item = QTreeWidgetItem([text])
            parent.addChild(new_item)
            return new_item
        # Build the tree
        root_items = {}
        for doc in docs:
            full_tag = doc.get('full_tag', '')
            if not full_tag.startswith(collection + "."):
                continue
            tag_parts = full_tag.split('.')[1:]  # skip collection name
            parent = self.tree
            for i, part in enumerate(tag_parts):
                # Only add as top-level if parent is self.tree
                if parent is self.tree:
                    # Check if already exists as top-level
                    found = None
                    for j in range(self.tree.topLevelItemCount()):
                        item = self.tree.topLevelItem(j)
                        if item.text(0) == part:
                            found = item
                            break
                    if not found:
                        found = QTreeWidgetItem([part])
                        found.setData(0, Qt.ItemDataRole.UserRole, "doc")
                        self.tree.addTopLevelItem(found)
                    parent = found
                else:
                    found = find_or_create_child(parent, part)
                    found.setData(0, Qt.ItemDataRole.UserRole, "doc")
                    parent = found
        # Expand all items by default
        def expand_all_items(item: Optional[QTreeWidgetItem]) -> None:
            if item is None:
                return
            for i in range(item.childCount()):
                child = item.child(i)
                expand_all_items(child)
            item.setExpanded(True)
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            expand_all_items(item)