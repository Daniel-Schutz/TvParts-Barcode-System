import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_admin_settings():
  admin_pull = app_tables.adminsettings.search()
  admin_settings_dict = [row for row in admin_pull][0]
  return admin_settings_dict

@anvil.server.callable
def get_full_item(item_id):
  return anvil.server.call('get_row_from_dynamo', 
                           'unique_item', 
                           item_id)

@anvil.server.callable
def update_item(item_id, col_name, value):
  return anvil.server.call('set_value_in_dynamo', 
                           'unique_item', 
                           item_id, 
                           col_name, 
                           value)

@anvil.server.callable
def import_full_table_to_anvil(table_name, records):
    table = getattr(app_tables, table_name)
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
