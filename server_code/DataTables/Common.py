import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import datetime
import time
import pandas as pd
import json

#Note: Get s3 Image URL (presigned url from oject key) already exists in AWSInterface
@anvil.server.callable
def get_all_rows_from_bins():
    return app_tables.bins.search()

@anvil.server.callable
def get_all_rows_from_products():
    return app_tables.products.search()

@anvil.server.callable
def get_item_from_scan(scan_json_str):
  scan_dict = json.loads(scan_json_str)
  item_id = scan_dict['item_id']
  item_row = app_tables.items.get(item_id=item_id)
  return item_row

@anvil.server.callable
def get_item_row_by_item_id(item_id):
  return app_tables.items.get(item_id=item_id)

@anvil.server.callable
def get_truck_from_scan(truck_json_str):
  scan_dict = json.loads(scan_json_str)
  truck_id = scan_dict['truck_id']
  truck_row = app_tables.trucks.get(truck_id=truck_id)
  return truck_row

@anvil.server.background_task
def add_full_records_to_table(records, table_name):
  # records = df.to_dict('records')
  batch_size = 50  # Adjust batch size as needed
  for start in range(0, len(records), batch_size):
      end = start + batch_size
      batch = records[start:end]
      anvil.server.call('import_full_table_to_anvil', table_name, batch)
      print(f"{end} records of {len(records)} uploaded to {table_name}.")

@anvil.server.callable
def add_history_to_item(item_id, item_status, user_full_name, user_role):
  print("inside the add history callable")
  anvil.server.launch_background_task('add_history_to_item_bk', 
                                      item_id, 
                                      item_status, 
                                      user_full_name, 
                                      user_role)

@anvil.server.background_task
def add_history_to_item_bk(item_id, item_status, user_full_name, user_role):
  current_time = datetime.datetime.now()
  human_date_str = current_time.strftime("%m/%d/%Y")
  human_time_str = current_time.strftime("%I:%M:%S %p %Z")
  time.sleep(1) #All other processing to finish, may not be necessary
  current_user = user_full_name
  current_role = user_role
  current_item = app_tables.items.get(item_id=item_id)
  current_history = current_item['history']
  new_message = f"{current_user} ({current_role}) updated item status to {item_status} on {human_date_str} at {human_time_str}."
  if current_history == "":
    current_item['history'] = new_message
  else:
    new_history  = current_history + "\n\n" + new_message
    current_item['history'] = new_history


@anvil.server.callable
def import_full_table_to_anvil(table_name, records):
    table = getattr(app_tables, table_name)
    print(records)
    for record in records:
        table.add_row(**record)

@anvil.server.callable
def add_row_to_table(table_name, **kwargs):
  table = getattr(app_tables, table_name)
  table.add_row(**kwargs)

@anvil.server.callable
def search_rows(table_name, column_name, value):
    """
    Return rows where column_name equals value.
    """
    table = getattr(app_tables, table_name)
    return table.search(**{column_name: value})

@anvil.server.callable
def update_rows(table_name, search_column, search_value, target_column, new_value):
    """
    Set all values of target_column to new_value where search_column equals search_value.
    """
    anvil.server.launch_background_task('update_rows_bk',table_name, 
                                        search_column, 
                                        search_value, 
                                        target_column, 
                                        new_value)

@anvil.server.background_task
def update_rows_bk(table_name, search_column, search_value, target_column, new_value):
    """
    Set all values of target_column to new_value where search_column equals search_value.
    """
    table = getattr(app_tables, table_name)
    for row in table.search(**{search_column: search_value}):
        row[target_column] = new_value

@anvil.server.callable
def delete_rows(table_name, column_name, value):
    """
    Delete rows where column_name equals value.
    """
    table = getattr(app_tables, table_name)
    for row in table.search(**{column_name: value}):
        row.delete()

@anvil.server.background_task
def delete_rows_bk(table_name, column_name, value):
    """
    Delete rows where column_name equals value.
    """
    table = getattr(app_tables, table_name)
    for row in table.search(**{column_name: value}):
        row.delete()

@anvil.server.callable
def get_sku_from_scan(table_name, item_id):
    """
     get_sku_from_scan.
    """
    table = getattr(app_tables, table_name)
    row = table.get(item_id=item_id)
    if row:
      sku_value = row['sku']
      return sku_value
    else:
      return None
