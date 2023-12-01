import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_next_order(user, table_no):
  next_order = app_tables.openorders.search(table_no=table_no, 
                                            status='Picked')
  if len(next_order) > 0:
    next_order = next_order[0]
    next_order.update(reserved_status='Reserved', reserved_by=user, status='Testing')
  else:
    next_order = None
  return next_order

@anvil.server.callable
def claim_selected_table(user, table_no):
  table_row = app_tables.tables.get(table=table_no)
  table_row.update(current_user=user)
  return table_row['table']

@anvil.server.callable
def get_img_source_from_sku(sku):
  product_row = app_tables.products.get(sku=sku)
  return product_row['img_source_url']



