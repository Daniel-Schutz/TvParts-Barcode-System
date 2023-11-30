import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_next_order(user):
  user_current_table = app_tables.tables.get(current_user=user)
  next_order = app_tables.openorders.search(table_no=user_current_table['table'], 
                                            status='Picked')
  if len(next_order > 0):
    next_order = next_order[0]
    next_order.update(reserved_status='Reserved', reserved_by=user, status='Testing')
  else:
    next_order = None
  return next_order



