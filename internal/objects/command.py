import pydantic

from typing import *

class Command(pydantic.BaseModel):
  name: str
  function: Callable
