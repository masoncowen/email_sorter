import win32com.client as win32
import dateutil.parser as dateparser

from typing import *

from ..objects import Email
from ..config import programConfig

class EmailBuilder():
  def __init__(self: Self, global_config: programConfig):
    self.global_config = global_config

  def from_outlook_item(self: Self, oEmailItem) -> Email:
    time_str = str(oEmailItem.ReceivedTime)
    r_time = dateparser.parse(time_str).replace(tzinfo=None)
    email = Email(contents = oEmailItem,
                  subject = oEmailItem.Subject,
                  sender_address = oEmailItem.SenderEmailAddress,
                  categories = oEmailItem.Categories,
                  received_time = r_time,
                  global_config = self.global_config)
    return email

  def from_entryid(self: Self, entryid) -> Optional[Email]:
    o = win32.Dispatch("Outlook.Application")
    mapi = o.GetNamespace("MAPI")
    try:
      oEmailItem = mapi.Session.GetItemFromID(entryid)
      return self.from_outlook_item(oEmailItem)
    except:
      return None
