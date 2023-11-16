import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

import json

@anvil.server.callable
def get_make_dropdown():
  results = app_tables.tv_makes.search()
  return [(row['make'], row['make']) for row in results]

@anvil.server.callable
def get_year_dropdown():
  results = app_tables.years.search()
  return [(str(row['year']), row['year']) for row in results]

@anvil.server.callable
def get_size_dropdown():
  results = app_tables.tv_sizes.search()
  return [(row['size'], row['size']) for row in results]

########## Data Retrievals from Page Interactions #############
@anvil.server.callable
def get_supplier_truck_from_code(truck_code):
  truck_code = json.loads(truck_code)
  truck_id = truck_code['truck']
  results = app_tables.trucks.search(truck_id=truck_id)
  row = [item for item in results][0]
  supplier = row['supplier_name']
  truck = row['truck_id']
  return supplier, truck
