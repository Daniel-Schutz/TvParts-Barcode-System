import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

from datetime import datetime

@anvil.server.callable
def get_open_tables(status):
  response = app_tables.tables.search(status=status)
  open_tables = [(row['table'], row['table']) for row in response]
  open_tables.append(('(Select Table)', '(Select Table)'))
  return open_tables

@anvil.server.callable
def claim_table(user, status):
  new_table_dict = app_tables.tables.search(status=status)[0] #might need to break this out if it doesn't return a dict
  row = app_tables.tables.get(table=new_table_dict['table'])
  row['current_user'] = user
  row['status'] = 'Picking'
  anvil.server.launch_background_task('update_user_on_section_rows', new_table_dict['table'], user)
  return row['table']

@anvil.server.callable
def load_current_order(user, status):
  claimed_order = app_tables.openorders.get(reserved_by=user, status=status)
  return claimed_order

@anvil.server.callable
def load_current_fulfillments(order_no):
  claimed_fulfillments = app_tables.openfulfillments.search(order_no=order_no)
  return claimed_fulfillments

@anvil.server.callable
def get_next_open_section(table):
  open_search = app_tables.table_sections.search(table=table, order='') #reset order to '' after shipping
  if len(open_search) == 0:
    return None
  else:
    return open_search[0]


####### Trays above tables logic ############
@anvil.server.callable
def get_pending_trays(status):
  pending_trays = app_tables.tables.search(type='Tray', status=status)
  if len(pending_trays) == 0:
    return None
  else:
    default = ("Select Table", "Select Table")
    pending_trays_vals = [(row['table'], row['table']) for row in pending_trays]
    pending_trays_vals.append(default)
    return pending_trays