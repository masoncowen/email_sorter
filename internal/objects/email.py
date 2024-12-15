import pydantic
import win32com.client as win32

import enum
from typing import *
from functools import cached_property
from datetime import datetime

from ..config import programConfig

class emailFlags(enum.Flag):
  Nothing = 0
  Archived = enum.auto()
  NewCategories = enum.auto()
  NewStatus = enum.auto()
  Saved = enum.auto()

class emailInformation(pydantic.BaseModel):
  categories_to_add: List[str] = []
  categories_to_remove: List[str] = []
  actions_to_add: List[str] = []
  actions_to_remove: List[str] = []
  flags: emailFlags = emailFlags.Nothing

  def __add__(self: Self, other: Self) -> Self:
    for category_to_add in other.categories_to_add:
      if category_to_add in self.categories_to_add:
        continue
      if category_to_add in self.categories_to_remove:
        continue
      self.categories_to_add.append(category_to_add)

    for category_to_remove in other.categories_to_remove:
      if category_to_remove in self.categories_to_remove:
        continue
      self.categories_to_remove.append(category_to_remove)

    for action_to_add in other.actions_to_add:
      if action_to_add in self.actions_to_add:
        continue
      if action_to_add in self.actions_to_remove:
        continue
      self.actions_to_add.append(action_to_add)

    for action_to_remove in other.actions_to_remove:
      if action_to_remove in self.actions_to_remove:
        continue
      self.actions_to_remove.append(action_to_remove)

    self.flags |= other.flags
    return self

class Email(pydantic.BaseModel):
  contents: Any
  flags: emailFlags = emailFlags.Nothing
  subject: str
  sender_address: str
  categories: str = ''
  received_time: datetime
  global_config: programConfig

  @pydantic.computed_field
  @cached_property
  def preview(self: Self) -> str:
    return self.contents.Body.replace('\n',' ')[:150]

  def update_categories(self: Self, new_cat: str) -> bool:
    self.refresh_categories() #Ensure categories variable is reflective of actual email Categories.
    if self.categories == new_cat:
      return False
    self.contents.Categories = new_cat
    self.refresh_categories()
    return True

  def refresh_categories(self: Self) -> None:
    self.categories = self.contents.Categories
    return

  def save(self: Self) -> None:
    try:
      self.contents.Save()
    except Exception as err:
      print("Tried to save, but failed")
      print(err)

  def mark_as_read(self: Self, read_status: bool = True) -> None:
    self.contents.Unread = not read_status
    return

  def display(self: Self) -> None:
    self.contents.Display(False)
    return

  def apply_information_new_categories(self: Self, adjustments: emailInformation):
    email_categories = email.categories.split(", ")
    categories = []
    actions = []
    for category in email_categories:
      if category == "Actionable":
        continue
      if category[:12] == "Next Action:":
        actions.append(category[13:])
        continue
      categories.append(category)
    
    for category in adjustments.categories_to_add:
      if category in categories:
        continue
      categories.append(category)

    for category in adjustments.categories_to_remove:
      if category not in categories:
        continue
      categories.remove(category)

    for action in adjustments.actions_to_add:
      if action in actions:
        continue
      actions.append(action)

    for action in adjustments.actions_to_remove:
      if action not in actions:
        continue
      actions.remove(action)

    returned_categories = []
    if len(categories) != 0:
      returned_categories.append(", ".join(categories))

    if len(actions) != 0:
      if all(["Awaiting" not in cat for cat in categories]):
        returned_categories.append("Actionable")
      returned_categories.append(", ".join(["Next Action: %s" % action for action in actions]))
    email.categories =  ", ".join(returned_categories)

  def archive(self: Self) -> None: #TODO: Remove hard coded Archive
    o = win32.Dispatch("Outlook.Application")
    MAPI = o.GetNamespace("MAPI")
    account = MAPI.Folders(self.global_config.outlook.account)
    archive_name = "Archive"
    if potential_archive_name := self.global_config.outlook.archive is not None:
      archive_name = potential_archive_name
    archive = account.Folders(archive_name)
    self.mark_as_read()
    self.contents.Move(archive)
  
  def apply_email_information(self: Self, adjustments: emailInformation):
    self.flags = adjustments.flags
    self.apply_information_new_categories(adjustments)
    if self.update_categories(new_categories):
      self.flags |= emailFlags.NewCategories
      if "Actionable," not in self.categories:
        self.mark_as_read()
    self.save()
    if emailFlags.Archived in self.flags:
      self.archive()
