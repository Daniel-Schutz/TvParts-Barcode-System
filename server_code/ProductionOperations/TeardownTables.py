import anvil.secrets
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

@anvil.server.callable
def get_supplier_dropdown():
  results = app_tables.suppliers.search()
  return [(row['supplier_name'], row['supplier_name']) for row in results]

@anvil.server.callable
def get_unique_trucks():
  results = results_tables.mocktrucks.search()
  return list(set([row['truck_ID'] for row in results]))

@anvil.server.callable
def create_truck(truck_id, truck_created):
  app_tables.mocktrucks.add_row(truck_id = truck_id, truck_created=truck_created)
