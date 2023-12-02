import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def claim_selected_table(user, table_no):
  table_row = app_tables.tables.get(table=table_no)
  table_row.update(current_user=user)
  return table_row['table']

@anvil.server.callable
def get_img_source_from_sku(sku):
  product_row = app_tables.products.get(sku=sku)
  return product_row['img_source_url']



