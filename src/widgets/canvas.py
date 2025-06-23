"""
Canvas widget for displaying form cards.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QListWidgetItem, QTableWidgetItem, QPushButton, QMessageBox, QDialog, QMenu
from PyQt6.QtCore import Qt, QPoint, QRect
from typing import Optional, List, Dict, Any
from .org_chart_box import OrgChartBox
from .org_chart_lines import OrgChartLines
from models.pydantic_models import DocumentModel_Base, DocumentModel_Race
from widgets.new_dialog import NewDialog
from widgets.update_dialog import UpdateDialog
from widgets.delete_dialog import DeleteDialog
from utils.helpers import refresh_app
from PyQt6.QtGui import QContextMenuEvent

class Canvas(QWidget):
    """Canvas widget that displays an org chart for the selected collection."""
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self.label = QLabel("No collection selected", self)
        self._layout.addWidget(self.label)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.chart_widget = QWidget()
        self.scroll_area.setWidget(self.chart_widget)
        self._layout.addWidget(self.scroll_area)
        self.setLayout(self._layout)
        self.documents: List[Dict[str, Any]] = []
        self.collection: Optional[str] = None
        self.lines_widget: Optional[OrgChartLines] = None

    def update_documents(self, collection: str, documents: List[Dict[str, Any]]) -> None:
        self.label.setText(f"Documents in {collection}")
        self.documents = documents
        self.collection = collection
        self._draw_org_chart()

    def _draw_org_chart(self):
        # Remove old chart
        for child in self.chart_widget.children():
            child.setParent(None)
        self.chart_widget.deleteLater()
        self.chart_widget = QWidget()
        self.scroll_area.setWidget(self.chart_widget)
        # Build tree structure from full_tag
        nodes = {}
        children_map = {}
        roots = []
        for doc in self.documents:
            full_tag = doc.get('full_tag', '')
            nodes[full_tag] = doc
            parent_tag = '.'.join(full_tag.split('.')[:-1]) if '.' in full_tag else None
            if parent_tag and parent_tag in nodes:
                children_map.setdefault(parent_tag, []).append(full_tag)
            else:
                roots.append(full_tag)
        # --- New layout logic ---
        from typing import Tuple
        BOX_SIZE = 120
        H_SPACING = 40
        V_SPACING = 60
        box_widgets: dict[str, OrgChartBox] = {}
        positions: dict[str, Tuple[int, int]] = {}
        def calc_subtree_width(tag: str) -> int:
            children: list[str] = children_map.get(tag, [])
            if not children:
                return BOX_SIZE
            width = 0
            for child in children:
                width += calc_subtree_width(child)
            width += H_SPACING * (len(children) - 1) if len(children) > 1 else 0
            return max(width, BOX_SIZE)
        def place_boxes(tag: str, x: int, y: int) -> None:
            children: list[str] = children_map.get(tag, [])
            subtree_width = calc_subtree_width(tag)
            box = OrgChartBox(nodes[tag].get('displayName',''), nodes[tag].get('full_tag',''), nodes[tag].get('description',''), self.chart_widget)
            box.move(int(x + subtree_width/2 - BOX_SIZE/2), y)
            box.show()
            box_widgets[tag] = box
            positions[tag] = (int(x + subtree_width/2 - BOX_SIZE/2), y)
            # Connect double-click signal
            box.boxDoubleClicked.connect(self.on_box_double_clicked)
            # Connect right-click context menu actions
            box.boxActionRequested.connect(self.on_box_action_requested)
            if children:
                total_width = 0
                for child in children:
                    child_width = calc_subtree_width(child)
                    child_x = x + total_width
                    place_boxes(child, child_x, y + BOX_SIZE + V_SPACING)
                    total_width += child_width + H_SPACING
        # Place all roots
        x = 40
        y = 40
        for root in roots:
            width = calc_subtree_width(root)
            place_boxes(root, x, y)
            x += width + H_SPACING
        # Set minimum size for chart widget
        max_x = max((pos[0] for pos in positions.values()), default=0) + BOX_SIZE + 40
        max_y = max((pos[1] for pos in positions.values()), default=0) + BOX_SIZE + 40
        self.chart_widget.setMinimumSize(max_x, max_y)
        # Draw lines (parent to children)
        if self.lines_widget:
            self.lines_widget.setParent(None)
        self.lines_widget = OrgChartLines(box_widgets, children_map, self.chart_widget)
        self.lines_widget.resize(self.chart_widget.size())
        self.lines_widget.lower()  # Draw lines below boxes
        self.lines_widget.show()

    def on_item_double_clicked(self, item: QListWidgetItem) -> None:
        doc = item.data(256)
        if not doc:
            return
        collection = doc.get('full_tag', '').split('.')[0]
        if collection == "Race":
            model_cls = DocumentModel_Race
        else:
            model_cls = DocumentModel_Base
        dialog = NewDialog(collection, model_cls, self)
        # Fill dialog fields with doc data
        dialog.setWindowTitle(f"Edit {doc.get('displayName', doc.get('tag', 'Document'))}")
        dialog.display_name_edit.setText(doc.get('displayName', ''))
        dialog.tag_edit.setText(doc.get('tag', ''))
        dialog.full_tag_edit.setText(doc.get('full_tag', ''))
        dialog.icon_edit.setText(doc.get('iconPath', ''))
        dialog.desc_edit.setPlainText(doc.get('description', ''))
        dialog.granted_tags_edit.setPlainText("\n".join(doc.get('grantedTags', [])))
        # Fill stats table
        stats = doc.get('grantStats', {}) or {}
        dialog.stats_table.setRowCount(0)
        for k, v in stats.items():
            row = dialog.stats_table.rowCount()
            dialog.stats_table.insertRow(row)
            dialog.stats_table.setItem(row, 0, QTableWidgetItem(str(k)))
            dialog.stats_table.setItem(row, 1, QTableWidgetItem(str(v)))
        # Fill abilities table
        abilities = doc.get('grantAbilities', {}) or {}
        dialog.abilities_table.setRowCount(0)
        for k, v in abilities.items():
            row = dialog.abilities_table.rowCount()
            dialog.abilities_table.insertRow(row)
            dialog.abilities_table.setItem(row, 0, QTableWidgetItem(str(k)))
            dialog.abilities_table.setItem(row, 1, QTableWidgetItem(str(v)))
        # Race mesh
        if collection == "Race" and hasattr(dialog, 'mesh_edit'):
            dialog.mesh_edit.setText(doc.get('meshPath', ''))
        # Remove the create logic and replace with update logic
        def accept():
            data = {
                'displayName': dialog.display_name_edit.text(),
                'tag': dialog.tag_edit.text(),
                'full_tag': dialog.full_tag_edit.text(),
                'iconPath': dialog.icon_edit.text(),
                'description': dialog.desc_edit.toPlainText(),
                'grantedTags': [t.strip() for t in dialog.granted_tags_edit.toPlainText().splitlines() if t.strip()],
            }
            stats = {}
            for row in range(dialog.stats_table.rowCount()):
                stat = dialog.stats_table.item(row, 0)
                value = dialog.stats_table.item(row, 1)
                if stat and value:
                    try:
                        stats[stat.text()] = float(value.text())
                    except ValueError:
                        stats[stat.text()] = 0.0
            data['grantStats'] = stats
            abilities = {}
            for row in range(dialog.abilities_table.rowCount()):
                ability = dialog.abilities_table.item(row, 0)
                req_level = dialog.abilities_table.item(row, 1)
                if ability and ability.text().strip():
                    try:
                        abilities[ability.text().strip()] = int(req_level.text()) if req_level and req_level.text().strip() else 1
                    except ValueError:
                        abilities[ability.text().strip()] = 1
            data['grantAbilities'] = abilities
            if collection == "Race" and hasattr(dialog, 'mesh_edit'):
                data['meshPath'] = dialog.mesh_edit.text()
            try:
                doc_obj = model_cls(**data)
                parent_app = self.parent()
                while parent_app and not hasattr(parent_app, 'db_handler'):
                    parent_app = parent_app.parent()
                if parent_app and hasattr(parent_app, 'db_handler'):
                    db_handler = parent_app.db_handler # type: ignore
                    # Find and update the document in the database
                    result, msg = db_handler.update_document(collection, doc.get('_id'), doc_obj.model_dump()) # type: ignore
                    if result:
                        QMessageBox.information(self, "Success", f"{collection} updated successfully.")
                        dialog.accept()
                        # Call refresh after update
                        refresh_parent = self.parent()
                        while refresh_parent and not hasattr(refresh_parent, 'refresh'):
                            refresh_parent = refresh_parent.parent()
                        if refresh_parent and hasattr(refresh_parent, 'refresh'):
                            refresh_parent.refresh()
                    else:
                        QMessageBox.warning(self, "Database Error", str(msg)) # type: ignore
                else:
                    QMessageBox.warning(self, "Error", "Database handler not found.")
            except Exception as e:
                QMessageBox.warning(self, "Validation Error", str(e))
        # Find OK button and connect
        for btn in dialog.findChildren(QPushButton):
            if btn.text().lower() == "ok":
                try:
                    btn.clicked.disconnect()
                except Exception:
                    pass
                btn.clicked.connect(accept)
                break
        dialog.exec()

    def on_box_double_clicked(self, full_tag: str) -> None:
        # Find the document by full_tag
        doc = next((d for d in self.documents if d.get('full_tag') == full_tag), None)
        if not doc:
            return
        collection = doc.get('full_tag', '').split('.')[0]
        if collection == "Race":
            model_cls = DocumentModel_Race
        else:
            model_cls = DocumentModel_Base
        def on_update(updated_data):
            parent_app = self.parent()
            while parent_app and not hasattr(parent_app, 'db_handler'):
                parent_app = parent_app.parent()
            if parent_app and hasattr(parent_app, 'db_handler'):
                db_handler = parent_app.db_handler # type: ignore
                result, msg = db_handler.update_document(collection, doc.get('_id'), updated_data) # type: ignore
                return result
            return False
        dialog = UpdateDialog(collection, model_cls, document=doc, on_update=on_update, parent=self)
        dialog.exec()

    def on_box_action_requested(self, full_tag: str, action: str) -> None:
        doc = next((d for d in self.documents if d.get('full_tag') == full_tag), None)
        if not doc:
            return
        collection = doc.get('full_tag', '').split('.')[0]
        if action == 'edit':
            self.on_box_double_clicked(full_tag)
        elif action == 'create_child':
            # Pre-fill tag for child: remove collection and period, add period if needed
            tag_path = doc.get('full_tag', '')
            if tag_path.startswith(collection + "."):
                tag_path = tag_path[len(collection)+1:]
            if tag_path and not tag_path.endswith('.'):
                tag_path += '.'
            # Open CreateNewDialog with tag pre-filled
            if collection == "Race":
                model_cls = DocumentModel_Race
            else:
                model_cls = DocumentModel_Base
            dialog = NewDialog(collection, model_cls, self)
            dialog.tag_edit.setText(tag_path)
            dialog.full_tag_edit.setText(f"{collection}.{tag_path}")
            dialog.setWindowTitle(f"Create Child for {doc.get('displayName', doc.get('tag', 'Document'))}")
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Refresh after creation
                parent_app = self.parent()
                while parent_app and not hasattr(parent_app, 'refresh'):
                    parent_app = parent_app.parent()
                if parent_app and hasattr(parent_app, 'refresh'):
                    parent_app.refresh()
        elif action == 'delete':
            doc = next((d for d in self.documents if d.get('full_tag') == full_tag), None)
            if not doc:
                return
            # Gather all descendants (including self)
            to_delete = []
            def gather_descendants(tag):
                d = next((d for d in self.documents if d.get('full_tag') == tag), None)
                if d:
                    to_delete.append(d)
                for child_tag in [d2.get('full_tag') for d2 in self.documents if d2.get('full_tag','').startswith(tag + '.')]:
                    gather_descendants(child_tag)
            gather_descendants(full_tag)
            # Remove duplicates
            to_delete = list({d['full_tag']: d for d in to_delete}.values())
            def on_delete():
                parent_app = self.parent()
                while parent_app and not hasattr(parent_app, 'db_handler'):
                    parent_app = parent_app.parent()
                if parent_app and hasattr(parent_app, 'db_handler'):
                    db_handler = parent_app.db_handler # type: ignore
                    for d in to_delete:
                        db_handler.delete_document(self.collection, d.get('_id')) # type: ignore
            dialog = DeleteDialog(self, on_delete=on_delete, documents=to_delete)
            dialog.exec()

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        # Check if click is on a box
        pos = event.pos()
        for child in self.chart_widget.children():
            if isinstance(child, OrgChartBox):
                if child.geometry().contains(self.chart_widget.mapFromParent(pos)):
                    # Let the box handle its own context menu
                    return
        # Not on a box: show Create New menu
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
        create_action = menu.addAction("Create New")
        action = menu.exec(event.globalPos())
        if action == create_action and self.collection:
            # Open CreateNewDialog for the current collection
            if self.collection == "Race":
                model_cls = DocumentModel_Race
            else:
                model_cls = DocumentModel_Base
            dialog = NewDialog(self.collection, model_cls, self)
            dialog.created.connect(self._handle_created)
            dialog.exec()

    def _handle_created(self):
        parent_app = self.parent()
        while parent_app and not hasattr(parent_app, 'refresh'):
            parent_app = parent_app.parent()
        if parent_app and hasattr(parent_app, 'refresh'):
            parent_app.refresh()
