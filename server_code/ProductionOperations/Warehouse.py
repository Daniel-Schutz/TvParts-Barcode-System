import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


@anvil.server.callable
def get_current_table(user):
   return app_tables.tables.get(current_user=user)

@anvil.server.callable
def get_open_tables():
  response = app_tables.tables.search(status="Open")
  open_tables = [(row['table'], row['table']) for row in response]
  open_tables.append(('(Select Table)', '(Select Table)'))
  return open_tables

@anvil.server.callable
def claim_table(user):
  new_table_dict = app_tables.tables.search(status="Open")[0] #might need to break this out if it doesn't return a dict
  row = app_tables.tables.get(table=new_table_dict['table'])
  row['current_user'] = user
  row['status'] = 'Picking'
  anvil.server.launch_background_task('update_user_on_section_rows')
  return row['table']

@anvil.server.callable
def fetch_new_order(user):
  user_current_table = app_tables.tables.get(current_user=user)
  claimed_order = app_tables.openorders.search(reserved_status='Open')[0]
  claimed_order.update(reserved_status = 'Reserved', reserved_by = user)
  # claimed_order['reserved_by'] = user
  claimed_fulfillments = app_tables.openfulfillments.search(order_no=claimed_order)
  return claimed_order, claimed_fulfillments

@anvil.server.callable
def load_current_order(user):
  claimed_order = app_tables.openorders.get(reserved_by=user, status='Picking')
  claimed_fulfillments = app_tables.openorders.search(order_no=claimed_order['order_no'])
  return claimed_order, claimed_fulfillments
  
  

@anvil.server.callable
def link_order_to_table_section(user, order, table):
  open_section = app_tables.table_sections.search(table=table, order='')[0] #make sure we set order to '' when moving out
  current_order = app_tables.openorders.get(reserved_status='Reserved', reserved_by=user)
  open_section.update(order=order)
  current_order.update(table_no=table, section=open_section['section'])
  return open_section['section']

@anvil.server.callable
def set_order_status(order, status):
  order_row = app_tables.openorders.get(order_no=order)
  order_row['status'] = status
  

@anvil.server.background_task
def update_user_on_section_rows(table_name, user):
  this_table_sections = app_tables.table_sections.search(table=table_name)
  for row in this_table_sections:
    row['current_user'] = user
  
