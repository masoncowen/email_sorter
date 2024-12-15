import sqlite3

import logging
from typing import *

class SQLDriver():
  def __init__(self: Self, dbfile: str):
    self.logger = logging.getLogger(__name__)
    self.dbfile = dbfile
    self.row_factory = None

  def connect(self: Self):
    connection = sqlite3.connect(self.dbfile, timeout = 20)
    if self.row_factory is not None:
      connection.row_factory = self.row_factory
    return connection

  def sql_str(self: Self, text: Any) -> str:
    text = str(text)
    sql_text = text.replace("'","''")
    return "'{}'".format(sql_text)

  def select(self: Self, table_name: str, column_names: List[str], where: Optional[str] = None):
    connection = self.connect()
    query = f"SELECT {','.join(column_names)} FROM {table_name}"
    if where is not None:
      query += f" WHERE {where}"
    query += ";"
    print(query)
    cur = connection.cursor()
    cur.execute(query)
    connection.commit()
    rows = cur.fetchall()
    cur.close()
    connection.close()
    return rows

  def update(self: Self, table_name: str, column_names: List[str], values: List[str], where: str):
    connection = self.connect()
    update_sql = f"""UPDATE {table_name}
    SET ({','.join(column_names)}) = ({','.join(values)})
    WHERE {where};"""
    cur = connection.cursor()
    cur.execute(update_sql)
    connection.commit()
    cur.close()
    connection.close()
    return

  def insert(self: Self, table: str, columns: list[str], values: list[str]) -> int:
    sql_query = f"""INSERT INTO {table} ({','.join(columns)})
    VALUES ({','.join(values)});"""
    print(sql_query)
    connection = self.connect()
    connection.row_factory = lambda cursor, row: row[0]
    cur = connection.cursor()
    cur.execute(sql_query)
    connection.commit()
    value = cur.lastrowid
    cur.close()
    connection.close()
    print(value)
    return value

  def query(self: Self, query: str):
    print(query)
    connection = self.connect()
    cur = connection.cursor()
    cur.execute(query)
    connection.commit()
    rows = cur.fetchall()
    cur.close()
    connection.close()
    return rows

  def single_value(self: Self, query: str):
    print(query)
    connection = self.connect()
    cur = connection.cursor()
    cur.execute(query)
    connection.commit()
    value = cur.fetchone()
    cur.close()
    connection.close()
    return value
