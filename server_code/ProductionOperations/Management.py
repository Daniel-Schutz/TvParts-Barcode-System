import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_needs_fixed_items():
  search_results = app_tables.items.search(status='Needs Fixed')
  if len(search_results) == 0:
    return None
  else:
    return search_results
