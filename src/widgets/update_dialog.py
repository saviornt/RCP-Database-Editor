"""
Dialog for updating an existing document in the active collection.
"""
from typing import Callable, Optional, Any, Dict, Type
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QPlainTextEdit, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QFileDialog, QLabel
)
from PyQt6.QtCore import Qt
import os
from utils.helpers import refresh_app

class TabTableWidget(QTableWidget):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.setTabKeyNavigation(True)
    def keyPressEvent(self, e: Any):
        if e.key() == Qt.Key.Key_Tab:
            current_row = self.currentRow()
            current_col = self.currentColumn()
            if current_row == self.rowCount() - 1 and current_col == self.columnCount() - 1:
                self.insertRow(self.rowCount())
                self.setCurrentCell(self.rowCount() - 1, 0)
            else:
                super().keyPressEvent(e)
        else:
            super().keyPressEvent(e)

class TabMultiLineEdit(QPlainTextEdit):
    def keyPressEvent(self, e: Any):
        if e.key() == Qt.Key.Key_Tab and not (e.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.focusNextChild()
        elif e.key() == Qt.Key.Key_Tab and (e.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.focusPreviousChild()
        else:
            super().keyPressEvent(e)

class UpdateDialog(QDialog):
    def __init__(
        self,
        collection: str,
        model_cls: Type[Any],
        document: Optional[Dict[str, Any]] = None,
        on_update: Optional[Callable[[Dict[str, Any]], bool]] = None,
        parent: Optional[QWidget] = None,
        *args,
        **kwargs
    ):
        super().__init__(parent, *args, **kwargs)
        self.setWindowTitle(f"Update {collection}")
        self.on_update = on_update
        self._refresh_parent = parent
        self.document = document or {}
        self.fields = {}
        layout = QFormLayout(self)
        # Name (displayName)
        self.display_name_edit = QLineEdit(self.document.get('displayName', ''))
        layout.addRow("Name", self.display_name_edit)
        self.fields['displayName'] = self.display_name_edit
        # Tag (tag)
        self.tag_edit = QLineEdit(self.document.get('tag', ''))
        layout.addRow("Tag", self.tag_edit)
        self.fields['tag'] = self.tag_edit
        # Full Tag (full_tag, read-only, italic, greyed out, not focusable)
        self.full_tag_edit = QLineEdit(self.document.get('full_tag', ''))
        self.full_tag_edit.setReadOnly(True)
        self.full_tag_edit.setStyleSheet("font-style: italic; color: grey;")
        self.full_tag_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.full_tag_edit.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addRow("Full Tag", self.full_tag_edit)
        # Icon (iconPath) with ... button
        icon_layout = QHBoxLayout()
        self.icon_edit = QLineEdit(self.document.get('iconPath', ''))
        self.icon_button = QPushButton("...", self)
        icon_layout.addWidget(self.icon_edit)
        icon_layout.addWidget(self.icon_button)
        icon_widget = QWidget(self)
        icon_widget.setLayout(icon_layout)
        layout.addRow("Icon", icon_widget)
        self.fields['iconPath'] = self.icon_edit
        def find_content_folder(start_path: str) -> str:
            path = os.path.abspath(start_path)
            while True:
                candidate = os.path.join(path, "Content")
                if os.path.isdir(candidate):
                    return candidate
                new_path = os.path.dirname(path)
                if new_path == path:
                    break
                path = new_path
            for root, dirs, _ in os.walk(os.path.abspath(start_path)):
                if "Content" in dirs:
                    return os.path.join(root, "Content")
            return os.path.abspath(start_path)
        def get_relative_to_content(full_path: str, content_folder: str) -> str:
            try:
                return os.path.relpath(full_path, content_folder)
            except ValueError:
                return full_path
        def file_picker(content_folder: str, title: str) -> str:
            if os.path.basename(content_folder) != "Content" or not os.path.isdir(content_folder):
                for root, dirs, _ in os.walk(content_folder):
                    if "Content" in dirs:
                        content_folder = os.path.join(root, "Content")
                        break
            file, _ = QFileDialog.getOpenFileName(self, title, content_folder)
            if file and os.path.commonpath([file, content_folder]) == content_folder:
                return get_relative_to_content(file, content_folder)
            return ""
        def open_icon_picker():
            content_folder = find_content_folder(os.getcwd())
            rel_path = file_picker(content_folder, "Select Icon")
            if rel_path:
                self.icon_edit.setText(rel_path)
        self.icon_button.clicked.connect(open_icon_picker)
        # Race-specific fields: Character Mesh (meshPath) with ... button (move here)
        if collection == "Race":
            mesh_layout = QHBoxLayout()
            self.mesh_edit = QLineEdit(self.document.get('meshPath', ''))
            self.mesh_button = QPushButton("...", self)
            mesh_layout.addWidget(self.mesh_edit)
            mesh_layout.addWidget(self.mesh_button)
            mesh_widget = QWidget(self)
            mesh_widget.setLayout(mesh_layout)
            layout.addRow("Character Mesh", mesh_widget)
            self.fields['meshPath'] = self.mesh_edit
            def open_mesh_picker():
                content_folder = find_content_folder(os.getcwd())
                rel_path = file_picker(content_folder, "Select Mesh")
                if rel_path:
                    self.mesh_edit.setText(rel_path)
            self.mesh_button.clicked.connect(open_mesh_picker)
        # Description (description, multi-line)
        self.desc_edit = TabMultiLineEdit(self)
        self.desc_edit.setPlainText(self.document.get('description', ''))
        layout.addRow("Description", self.desc_edit)
        self.fields['description'] = self.desc_edit
        # Additional Tags (grantedTags, multi-line)
        self.granted_tags_edit = QPlainTextEdit(self)
        granted_tags = self.document.get('grantedTags', [])
        if isinstance(granted_tags, list):
            self.granted_tags_edit.setPlainText("\n".join(granted_tags))
        else:
            self.granted_tags_edit.setPlainText(str(granted_tags))
        layout.addRow("Additional Tags", self.granted_tags_edit)
        self.fields['grantedTags'] = self.granted_tags_edit
        # Grants Stats (grantStats): key-value pairs with + and - buttons
        self.stats_table = TabTableWidget(0, 2, self)
        self.stats_table.setHorizontalHeaderLabels(["Stat", "Value"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.stats_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.add_stat_btn = QPushButton("+", self)
        self.remove_stat_btn = QPushButton("-", self)
        def add_stat_row():
            row = self.stats_table.rowCount()
            self.stats_table.insertRow(row)
            self.stats_table.setItem(row, 0, QTableWidgetItem(""))
            self.stats_table.setItem(row, 1, QTableWidgetItem("0.0"))
            self.stats_table.setCurrentCell(row, 0)
        def remove_stat_row():
            row = self.stats_table.currentRow()
            if row >= 0:
                self.stats_table.removeRow(row)
        self.add_stat_btn.clicked.connect(add_stat_row)
        self.remove_stat_btn.clicked.connect(remove_stat_row)
        stats_btn_layout = QVBoxLayout()
        stats_btn_layout.addWidget(self.add_stat_btn)
        stats_btn_layout.addWidget(self.remove_stat_btn)
        stats_btn_layout.addStretch()
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(self.stats_table)
        stats_layout.addLayout(stats_btn_layout)
        stats_widget = QWidget(self)
        stats_widget.setLayout(stats_layout)
        layout.addRow("Grants Stats", stats_widget)
        self.fields['grantStats'] = self.stats_table
        # Pre-fill stats table
        stats = self.document.get('grantStats', {})
        if isinstance(stats, dict):
            for stat, value in stats.items():
                row = self.stats_table.rowCount()
                self.stats_table.insertRow(row)
                self.stats_table.setItem(row, 0, QTableWidgetItem(str(stat)))
                self.stats_table.setItem(row, 1, QTableWidgetItem(str(value)))
        # Grants Abilities (grantAbilities): Ability, Req. Level
        self.abilities_table = TabTableWidget(0, 2, self)
        self.abilities_table.setHorizontalHeaderLabels(["Ability", "Req. Level"])
        self.abilities_table.horizontalHeader().setStretchLastSection(True)
        self.abilities_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.abilities_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.add_ability_btn = QPushButton("+", self)
        self.remove_ability_btn = QPushButton("-", self)
        def add_ability_row():
            row = self.abilities_table.rowCount()
            self.abilities_table.insertRow(row)
            self.abilities_table.setItem(row, 0, QTableWidgetItem(""))
            self.abilities_table.setItem(row, 1, QTableWidgetItem("1"))
            self.abilities_table.setCurrentCell(row, 0)
        def remove_ability_row():
            row = self.abilities_table.currentRow()
            if row >= 0:
                self.abilities_table.removeRow(row)
        self.add_ability_btn.clicked.connect(add_ability_row)
        self.remove_ability_btn.clicked.connect(remove_ability_row)
        abilities_btn_layout = QVBoxLayout()
        abilities_btn_layout.addWidget(self.add_ability_btn)
        abilities_btn_layout.addWidget(self.remove_ability_btn)
        abilities_btn_layout.addStretch()
        abilities_layout = QHBoxLayout()
        abilities_layout.addWidget(self.abilities_table)
        abilities_layout.addLayout(abilities_btn_layout)
        abilities_widget = QWidget(self)
        abilities_widget.setLayout(abilities_layout)
        layout.addRow("Grants Abilities", abilities_widget)
        self.fields['grantAbilities'] = self.abilities_table
        # Pre-fill abilities table
        abilities = self.document.get('grantAbilities', {})
        if isinstance(abilities, dict):
            for ability, req_level in abilities.items():
                row = self.abilities_table.rowCount()
                self.abilities_table.insertRow(row)
                self.abilities_table.setItem(row, 0, QTableWidgetItem(str(ability)))
                self.abilities_table.setItem(row, 1, QTableWidgetItem(str(req_level)))
        # Update full_tag as tag changes
        def update_full_tag():
            tag_parts = [collection]
            tag_value = self.tag_edit.text()
            if tag_value:
                tag_parts.append(tag_value)
            self.full_tag_edit.setText(".".join(tag_parts))
        self.tag_edit.textChanged.connect(update_full_tag)
        update_full_tag()
        # Accept logic
        btn_ok = QPushButton("Save", self)
        btn_cancel = QPushButton("Cancel", self)
        btn_ok.setDefault(True)
        btn_ok.setAutoDefault(True)
        btn_ok.setMinimumWidth(100)
        btn_cancel.setMinimumWidth(100)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_layout.addWidget(btn_ok)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addStretch(1)
        layout.addRow(btn_layout)
        self.setLayout(layout)
        def accept():
            data: dict[str, Any] = {
                'displayName': self.display_name_edit.text(),
                'tag': self.tag_edit.text(),
                'full_tag': self.full_tag_edit.text(),
                'iconPath': self.icon_edit.text(),
                'description': self.desc_edit.toPlainText(),
                'grantedTags': [t.strip() for t in self.granted_tags_edit.toPlainText().splitlines() if t.strip()],
            }
            # Gather grantStats
            stats = {}
            for row in range(self.stats_table.rowCount()):
                stat = self.stats_table.item(row, 0)
                value = self.stats_table.item(row, 1)
                if stat and value:
                    try:
                        stats[stat.text()] = float(value.text())
                    except ValueError:
                        stats[stat.text()] = 0.0
            data['grantStats'] = stats
            # Gather grantAbilities
            abilities = {}
            for row in range(self.abilities_table.rowCount()):
                ability = self.abilities_table.item(row, 0)
                req_level = self.abilities_table.item(row, 1)
                if ability and ability.text().strip():
                    try:
                        abilities[ability.text().strip()] = int(req_level.text()) if req_level and req_level.text().strip() else 1
                    except ValueError:
                        abilities[ability.text().strip()] = 1
            data['grantAbilities'] = abilities
            if collection == "Race":
                data['meshPath'] = self.mesh_edit.text()
            success = False
            if callable(self.on_update):
                success = self.on_update(data)
            parent = self.parent()
            while parent and not hasattr(parent, 'db_handler'):
                parent = parent.parent()
            if success and parent:
                refresh_app(parent)
            info_box = QMessageBox(self)
            if success:
                info_box.setIcon(QMessageBox.Icon.Information)
                info_box.setWindowTitle("Update Successful")
                info_box.setText("Document updated successfully.")
                info_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                info_box.buttonClicked.connect(self.accept)
            else:
                info_box.setIcon(QMessageBox.Icon.Critical)
                info_box.setWindowTitle("Update Failed")
                info_box.setText("Failed to update document.")
                info_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                info_box.buttonClicked.connect(self.reject)
            info_box.exec()
            if not success:
                self.reject()
        btn_ok.clicked.connect(accept)
        btn_cancel.clicked.connect(self.reject)
