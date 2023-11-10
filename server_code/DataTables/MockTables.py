import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_supplier_dropdown():
  results = app_tables.mocksuppliers.search()
  return [(row['supplier_ID'], row['supplier_name']) for row in results]
