import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

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
