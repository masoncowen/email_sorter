import pydantic

from typing import *
import os
import json
import pathlib
import re

class outlookConfig(pydantic.BaseModel):
  account: str
  folder: str
  archive: Optional[str] = None

class tabConfig(pydantic.BaseModel):
  name: str
  minimum_age: Optional[int] = None
  maximum_age: Optional[int] = None
  filtered_categories: tuple[str] = ()
  blocked_categories: tuple[str] = ()
  filtered_actions: tuple[str] = ()
  filtered_types: tuple[str] = ()
  blocked_types: tuple[str] = ()

class categoryConfig(pydantic.BaseModel):
  text: str
  jobs: list[str] = []
  new_types: list[str] = []
  next_actions: list[str] = []

class searchConfig(pydantic.BaseModel):
  db_file: str
  placeholder_text: Optional[str] = None
  primary_column: str
  primary_column_type: Literal["integer", "text"] = "integer"
  information_text: str = ""
  table_joins: str

  def query(self):
    concat = re.sub("}(.*){", r",'\1',", self.information_text)
    concat = re.sub("^(.*){", r"'\1',", concat)
    concat = re.sub("}(.*)$", r",'\1'", concat)
    return "SELECT CONCAT(" + self.primary_column + ",': '," + concat + ') FROM ' + self.table_joins + ";"

class actionConfig(pydantic.BaseModel):
  text: str
  command: str

class programConfig(pydantic.BaseModel):
  search: Optional[searchConfig] = None
  outlook: Optional[outlookConfig] = None
  tabs: list[tabConfig] = []
  categories: list[categoryConfig] = []
  actions: list[actionConfig] = []

def get_config_path() -> Optional[pathlib.Path]:
  config_path = os.environ.get('PY_OUTLOOK_SORTER_PATH')
  if config_path is not None:
    config = pathlib.Path(config_path)
    if config.exists() and not config.is_dir():
      return config
  config_dir_path = os.environ.get('XDG_CONFIG_HOME')
  if config_dir_path is not None:
    config_dir = pathlib.Path(config_dir_path)
    config = config_dir / 'pyOutlookSorter' / 'config.json'
    if config.exists() and not config.is_dir():
      return config
  default_config_path = pathlib.Path.home() / '.pyOutlookSorter' / 'config.json'
  if config.exists() and not config.is_dir():
    return config
  return None

def load_config() -> programConfig:
  config_path = get_config_path()
  config = programConfig()
  if config_path is None:
    return config
  with open(config_path) as config_data:
    data = json.load(config_data)
  if "search" in data:
    required_columns = ('db_file', 'primary_column', "table_joins")
    if any([col not in data["search"] for col in required_columns]):
      for col in required_columns:
        if col not in data["search"]:
          print(col)
      print(data["search"])
      raise KeyError
    config.search = searchConfig(db_file = data["search"]["db_file"],
                          primary_column = data["search"]["primary_column"],
                          table_joins = data["search"]["table_joins"])
    for key, value in data["search"].items():
      if key in required_columns:
        continue
      try:
        setattr(config.search, key, value)
      except ValueError as e:
        print(e)
        continue
  if "outlook" in data:
    required_columns = ('account', 'folder')
    if any([col not in data["outlook"] for col in required_columns]):
      for col in required_columns:
        if col not in data["outlook"]:
          print(col)
      print(data["outlook"])
      raise KeyError
    config.outlook = outlookConfig(account = data["outlook"]["account"],
                                   folder = data["outlook"]["folder"])
    for key, value in data["outlook"].items():
      if key in required_columns:
        continue
      try:
        setattr(config.outlook, key, value)
      except ValueError as e:
        print(e)
        continue
  if "tabs" in data:
    for tab in data["tabs"]:
      required_columns = ("name",)
      if any([col not in tab for col in required_columns]):
        continue
      tab_conf = tabConfig(name = tab["name"])
      for key, value in tab.items():
        if key in required_columns:
          continue
        try:
          setattr(tab_conf, key, value)
        except ValueError as e:
          print(e)
          continue
      config.tabs.append(tab_conf)
  if "categories" in data:
    for category in data["categories"]:
      required_columns = ("text", "jobs")
      if any([col not in category for col in required_columns]):
        continue
      category_conf = categoryConfig(text = category["text"],
                                     jobs = category["jobs"])
      for key, value in category.items():
        if key in required_columns:
          continue
        try:
          setattr(category_conf, key, value)
        except ValueError as e:
          print(e)
          continue
      config.categories.append(category_conf)
  if "actions" in data:
    for action in data["actions"]:
      required_columns = ("text", "command")
      if any([col not in action for col in required_columns]):
        continue
      action_conf = actionConfig(text = action["text"],
                                 command = action["command"])
      for key, value in action.items():
        if key in required_columns:
          continue
        try:
          setattr(action_conf, key, value)
        except ValueError as e:
          print(e)
          continue
      config.actions.append(action_conf)
  return config
