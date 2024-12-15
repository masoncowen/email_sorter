from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

from .email import *

def setup_shortcuts(self, quit_func = None, refresh_func = None, hard_refresh_func = None):
  if quit_func is not None:
    QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(quit_func)
  if refresh_func is not None:
    QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(refresh_func)
  if hard_refresh_func is not None:
    QShortcut(QKeySequence("Ctrl+Shift+R"), self).activated.connect(hard_refresh_func)
