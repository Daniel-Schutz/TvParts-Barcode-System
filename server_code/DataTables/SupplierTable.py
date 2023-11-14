import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

from . import Common

@anvil.server.callable
def add_new_supplier(**kwargs):
  Common.add_row_to_table('suppliers', **kwargs)