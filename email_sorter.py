from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QVBoxLayout

from typing import *

from internal.gui import setup_shortcuts, emailTabArea
from internal.config import load_config, programConfig

class mainSection(QFrame):
  def __init__(self: Self, window, config: programConfig):
    super().__init__()
    self.config = config
    self.layout = QVBoxLayout(self)
    self.email_lists = emailTabArea(window, global_config = self.config)
    self.layout.addWidget(self.email_lists)

  def refresh(self):
    self.email_lists.refresh()

  def hard_refresh(self: Self, config: programConfig):
    self.config = config
    # self.search_bar.hard_refresh(self.config.search)
    self.email_action_selector.hard_refresh(self.config.actions)
    self.email_lists.hard_refresh(self.config.outlook, self.config.tabs, self.config.actions)

class mainWindow(QMainWindow):
  def __init__(self: Self):
    super().__init__()
    config = load_config()
    self.main_section = mainSection(self, config)
    self.setCentralWidget(self.main_section)
    setup_shortcuts(
        self,
        quit_func = self.quit,
        refresh_func = self.refresh,
        hard_refresh_func = self.hard_refresh
        )
    self.setGeometry(600, 100, 1000, 900)
    self.setWindowTitle("Email Sorter v0.0.1")
    LINE_CLEAR = '\x1b[2K'
    print("",end=LINE_CLEAR)
    print("Ready to use")

  def refresh(self: Self):
    self.main_section.refresh()

  def hard_refresh(self: Self):
    config = load_config()
    self.main_section.hard_refresh(config)

  def quit(self: Self):
    print("Program is quitting.")
    print("Would clean up if there was anything to clean.")
    QApplication.instance().quit()

if __name__ == "__main__":
  app = QApplication([])
  window = mainWindow()
  window.show()
  app.exec()
