from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QFrame, QLabel, QGroupBox, QHBoxLayout, QTabWidget, QPushButton, QGridLayout
import win32com.client as win32
import pydantic

from datetime import datetime, timedelta
from enum import Enum
from typing import *
from functools import cached_property

from ..config import outlookConfig, tabConfig, actionConfig, programConfig
from ..objects import Email, emailFlags
from ..builders import EmailBuilder, CommandBuilder

class emailTabArea(QTabWidget):
  def __init__(self: Self, window, global_config: programConfig):
    super().__init__()
    self.window = window
    self.last_loaded = None
    self.emails = []
    self.global_config = global_config
    self.setup_emails()
    self.setup_tabs()

  def setup_tabs(self: Self):
    if self.global_config.tabs is None:
      return
    for i, tab_config in enumerate(self.global_config.tabs):
      scroll = emailScrollArea(self.window, tab_config, self.emails, self.global_config)
      self.addTab(scroll, f"{tab_config.name} ({len(scroll.emails)})")

  def refresh_tabs(self: Self):
    for i in range(self.count()):
      self.widget(i).refresh(emails=self.emails)
      self.setTabText(i, f"{self.global_configs.tabs[i].name} ({len(self.widget(i).emails)})")

  def refresh(self):
    self.setup_emails(partial_load=True)
    self.refresh_tabs()

  def hard_refresh(self: Self, global_config: programConfig):
    self.global_config = global_config
    self.setup_emails()
    for i in reversed(range(self.count())):
      self.widget(i).deleteLater()
    self.setup_tabs()

  def connect_to_inbox(self) -> bool:
    if self.global_config.outlook is None:
      return False
    outlook = win32.Dispatch("Outlook.Application")
    MAPI = outlook.GetNamespace("MAPI")
    self.inbox = MAPI.Folders(self.global_config.outlook.account).Folders(self.global_config.outlook.folder)
    return True

  def setup_emails(self, partial_load=False):
    if partial_load:
      previous_emails = self.emails
    self.emails = []
    try:
      print(f"Setting up emails ({len(self.inbox.Items)})", end='', flush=True)
    except:
      if not self.connect_to_inbox():
        return
    build = EmailBuilder(self.global_config)
    LINE_CLEAR = '\x1b[2K'
    for inbox_item in self.inbox.Items:
      email = build.from_outlook_item(inbox_item)
      print("",end=LINE_CLEAR)
      print("Loading email: ", email.subject, end='\r', flush=True)
      try:
        if self.last_loaded is not None:
          if email.received_time < self.last_loaded and partial_load:
            break
      except Exception as e:
        print(e)
        print("Error on email age check")
      self.emails.append(email)
    if partial_load:
      self.emails.extend(previous_emails)
    self.last_loaded = datetime.now()

class emailScrollArea(QScrollArea):
  def __init__(self, window, tab_config: tabConfig, initial_emails: list[Email], global_config: programConfig):
    super().__init__()
    self.window = window
    self.config = tab_config
    self.global_config = global_config
    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.setWidgetResizable(True)

    self.widget = QWidget()
    self.layout = QVBoxLayout()

    self.all_emails = initial_emails
    self.emails = []
    self.setup_emails()
    self.widget.setLayout(self.layout)
    self.setWidget(self.widget)

  def refresh(self, emails):
    self.all_emails = emails
    for i in reversed(range(self.layout.count())):
      self.layout.itemAt(i).widget().deleteLater()
    self.emails = []
    print("Refreshing email entries")
    self.setup_emails()

  def setup_emails(self):
    LINE_CLEAR = '\x1b[2K'
    print("",end=LINE_CLEAR)
    print("Setting up a tab: ", self.config.name, end='\r', flush=True)
    for email in self.all_emails:
      if self.config.maximum_age is not None and \
        email.received_time < datetime.now() - timedelta(days = self.config.maximum_age):
        break
      if self.config.minimum_age is not None and \
          email.received_time > datetime.now() - timedelta(days = self.config.minimum_age):
        continue
      email_cats = email.categories
      contains_filtered_cats = any([cat in email_cats for cat in self.config.filtered_categories]) or self.config.filtered_categories == ()
      contains_filtered_actions = any([f"Next Action: {action}" in email_cats for action in self.config.filtered_actions]) or self.config.filtered_actions == ()
      contains_filtered_types = any([f"Type: {email_type}" in email_cats for email_type in self.config.filtered_types]) or self.config.filtered_types == ()
      contains_filtered_targets = contains_filtered_cats and contains_filtered_actions and contains_filtered_types
      contains_blocked_categories = any([cat in email_cats for cat in self.config.blocked_categories])
      contains_blocked_types = any([email_type in email_cats for email_type in self.config.blocked_types])
      contains_blocked_targets = contains_blocked_categories or contains_blocked_types

      if contains_blocked_targets or not contains_filtered_targets:
        continue
      entry = emailEntry(email, self.window, self.global_config)
      self.layout.addWidget(entry)
      self.emails.append(email)

class btnEmailAction(QPushButton):
  def __init__(self, config: actionConfig, email, parent, global_config: programConfig):
    super().__init__(config.text)
    self.setFixedSize(200,40)
    self.config = config
    self.global_config = global_config
    self.command = CommandBuilder().from_command_text(self.config.command, self.global_config)
    self.email = email
    self.parent = parent

  def mousePressEvent(self, QMouseEvent):
    if self.command is None:
      raise NotImplementedError
    try:
      print(self.command)
      print(self.command.function)
      adjustments = self.command.function(self.email, self.global_config)
    except Exception as e:
      print("Email action failed")
      print(e)
      return
    self.email.apply_email_information(adjustments)
    if self.email.Archived in self.email.flags:
      self.parent.deleteLater()
    if emailFlags.NewCategories in self.email.flags:
      self.parent.refresh()

class emailEntry(QGroupBox):
  def __init__(self, email: Email, window, global_config):
    super().__init__(email.subject)
    # self.setMaximumHeight(100)
    self.window = window
    self.email = email
    self.global_config = global_config
    self.action_configs = global_config.actions

    self.setStyleSheet(
        """
        QGroupBox{border: 1px solid black;
        background-color: lightGray;}
        """
        )

    grid = QGridLayout(self)
    left_frame = QFrame(self)
    grid.addWidget(left_frame, 0, 0, alignment=Qt.AlignLeft)
    layers = QVBoxLayout(left_frame)

    self.categories_label = QLabel(self.email.categories)
    self.categories_label.setWordWrap(True)
    self.categories_label.setFixedSize(600, 35)
    layers.addWidget(self.categories_label)

    email_preview = QLabel(email.preview)
    email_preview.setWordWrap(True)
    layers.addWidget(email_preview)

    action_frame = QFrame()
    self.action_layout = QVBoxLayout(action_frame)
    grid.addWidget(action_frame, 0, 1, alignment=Qt.AlignRight)
    self.setup_actions()

  def setup_actions(self: Self):
    if self.email.categories == '':
      if self.action_configs is not None:
        action_button = btnEmailAction(self.action_configs[0], self.email, self, self.global_config)
      else:
        action_button = btnEmailAction(actionConfig(text="Initial Categorisation",
                                                    command="initial_categorise"),
                                       self.email, self, self.global_config)
      self.action_layout.addWidget(action_button)
    cats = self.email.categories.split(',')
    for cat in cats:
      if 'Next Action:' not in cat:
        continue
      action_text = cat[len('Next Action: '):]
      action = actionConfig(text = action_text, command = 'unrecognised')
      for possible_action in self.action_configs:
        if possible_action.text == action_text:
          action = possible_action
      action_button = btnEmailAction(action, self.email, self, self.global_config)
      self.action_layout.addWidget(action_button)

  def refresh(self: Self):
    self.categories_label.setText(self.email.categories)
    for i in reversed(range(self.action_layout.count())):
      self.action_layout.itemAt(i).widget().deleteLater()
    self.setup_actions()
