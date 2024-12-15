from functools import partial
from typing import *
from enum import Enum
import subprocess
import shlex

from ..config import programConfig, searchConfig
from ..objects import Command, Email
from ..dialogs import EmailCategoriser

def not_implemented():
  raise NotImplementedError("Whatever command you clicked, hasn't been implemented yet")

def initial_categorise(email: Email, global_config: programConfig):
  response = EmailCategoriser(email, global_config).select()
  raise NotImplementedError("Initial Categorisation has not been created yet")

def shell(email: Email, command: list[str]):
  process = subprocess.Popen(command)

class AvailableCommands(Enum):
  not_implemented = not_implemented
  initial_categorise = initial_categorise
  shell = shell

class CommandBuilder():
  def from_command_text(self: Self, text: str, global_config: programConfig) -> Optional[Command]:
    args =  shlex.split(text)
    print(args)
    primary_command = args[0]
    match primary_command:
      case "unrecognised":
        return Command(name = primary_command, function = AvailableCommands.not_implemented)
      case "initial_categorise":
        return Command(name = primary_command, function = AvailableCommands.initial_categorise)
      case "shell":
        if len(substrings) < 2:
          raise Exception("Shell command needs more arguments")
        function = partial(AvailableCommands.shell, command = args[1:])
        return Command(name = primary_command, function = function)
    return None
