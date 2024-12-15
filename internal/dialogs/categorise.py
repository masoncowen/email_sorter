from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtWidgets import (
    QDialog, QCheckBox, QVBoxLayout, QDialogButtonBox,
    QScrollArea, QWidget, QPushButton, QLineEdit, QCompleter,
    QComboBox
)

from typing import *

from ..config import searchConfig, categoryConfig, programConfig
from ..objects import Email
from ..sql import SQLDriver

class entitySearchBar(QLineEdit):
  def __init__(self: Self, config: searchConfig):
    super().__init__()
    self.config = config
    self.completer = QCompleter()
    self.completer.setCaseSensitivity(Qt.CaseInsensitive)
    self.completer.setFilterMode(Qt.MatchContains)
    if self.config.placeholder_text is not None:
      self.setPlaceholderText(self.config.placeholder_text)
    self.refresh()

  def refresh(self):
    sql_driver = SQLDriver(self.config.db_file)
    sql_driver.row_factory = lambda cursor, row: row[0]
    str_list = sql_driver.query(self.config.query())

    model = QStringListModel()
    model.setStringList(str_list)
    self.completer.setModel(model)
    self.setCompleter(self.completer)

  def hard_refresh(self: Self, config: searchConfig):
    self.config = config
    if self.config.placeholder_text is not None:
      self.setPlaceholderText(self.config.placeholder_text)
    self.refresh()

  def entityid(self) -> Optional[int]:
    if ":" not in self.text():
      return None
    return int(self.text().split(':')[0])

class emailCategorySelector(QComboBox):
  def __init__(self: Self, category_configs: list[categoryConfig]):
    super().__init__()
    self.categories = category_configs
    self.addItems([category_config.text for category_config in self.categories])

  def get_selected_action_config(self: Self):
    return self.categories[self.currentIndex()]

  def hard_refresh(self: Self, categories: list[categoryConfig]):
    self.categories = categories
    self.clear()
    self.addItems([category_config.text for category_config in categories])

class EmailCategoriser(QDialog):
  def __init__(self, email: Email, global_config: programConfig):
    super().__init__()
    self.setGeometry(600, 100, 300, 300)
    self.email = email
    self.global_config = global_config
    # self.response: Response = None
    self.setup_dialog()

  def setup_dialog(self: Self):
    self.widg = QWidget()
    self.widg_layout = QVBoxLayout(self)
    self.entity_selector = entitySearchBar(self.global_config.search)
    self.widg_layout.addWidget(self.entity_selector)
    self.category_selector = emailCategorySelector(self.global_config.categories)
    self.widg_layout.addWidget(self.category_selector)
    self.widg.setLayout(self.widg_layout)
    self.scroll = QScrollArea()
    self.scroll.setWidget(self.widg)
    self.scroll.setWidgetResizable(True)
    self.layout = QVBoxLayout(self)
    self.layout.addWidget(self.scroll)

    btns = QDialogButtonBox.Cancel
    # addSPIDButton = QPushButton("New Project")
    # addSPIDButton.clicked.connect(self.create_new_project)
    buttons = QDialogButtonBox(btns)
    # buttons.addButton(addSPIDButton, QDialogButtonBox.ActionRole)
    buttons.rejected.connect(self.reject)
    self.layout.addWidget(buttons)
    self.setLayout(self.layout)

  def select(self: Self) -> bool:
    return True if self.exec_() else False
