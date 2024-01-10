import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

from ..DataTables import Common

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



@anvil.server.callable
def update_item_count():
  anvil.server.launch_background_task('update_item_count_bk')

@anvil.server.background_task
def update_item_count_bk():
  truck_ids = app_tables.trucks.search()
  for row in truck_ids:
    truck_id = row['truck_id']
    result_rows = app_tables.items.search(truck=truck_id)
    item_system_count = len(result_rows)
    item_sold_count = len([item for item in result_rows if item['status'] == 'Sold'])
    item_return_count = len([item for item in result_rows if item['status'] == 'Returned'])
    item_defect_count = len([item for item in result_rows if 'Needs Fixed' in item['history']])
    item_tossed_count = len([item for item in result_rows if item['status'] == 'Returned'])
  
    truck_row = app_tables.trucks.get(truck_id=truck_id)

    if truck_row is not None:
      truck_row['item_system_count'] = item_system_count
      truck_row['item_sold_count'] = item_sold_count
      truck_row['item_return_count'] = item_return_count
      truck_row['item_defect_count'] = item_defect_count
      truck_row['item_tossed_count'] = item_tossed_count
      truck_row.update()
    else:
      print(f" {truck_id} not found on table 'trucks'")

    