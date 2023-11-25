import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

from datetime import datetime


@anvil.server.callable
def get_current_table(user):
  try:
    return app_tables.tables.get(current_user=user)['table']
  except:
    return None

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
  return claimed_order

@anvil.server.callable
def load_current_order(user):
  claimed_order = app_tables.openorders.get(reserved_by=user, status='Picking')
  return claimed_order
    
@anvil.server.callable
def load_current_fulfillments(order_no):
  # claimed_order = app_tables.openorders.get(reserved_by=user, status='Picking')
  # print("in server load current order - lookng at order")
  # print(entry for entry in claimed_order)
  # if not claimed_order:
  #   return None, None
  claimed_fulfillments = app_tables.openfulfillments.search(order_no=order_no)
  return claimed_fulfillments
  
  

@anvil.server.callable
def link_order_to_table_section(user, order, table):
  open_section = app_tables.table_sections.search(table=table, order='')[0] #reset order to '' after shipping
  if len(open_section) == 0:
    return None
  current_order = app_tables.openorders.get(reserved_status='Reserved', reserved_by=user)
  open_section.update(order=order, current_user=user)
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


@anvil.server.callable
def get_product_row_by_name(product_name):
  return app_tables.products.get(product_name=product_name)

@anvil.server.callable
def get_product_row_by_sku(in_sku):
  return app_tables.products.get(sku=in_sku)

@anvil.server.callable
def finish_order_in_db(order_no):
  closed_order_row = app_tables.openorders.get(order_no=order_no)
  closed_order_row.update(reserved_by='', reserved_status='Pending', status='Picked')
  #potentially do this if we want to lookup table sections directly by current user. Right now is extraneous
  # closed_section_row = app_tables.table_sections.get(order=order_no)
  # closed_section_row.update(current_user='')


@anvil.server.callable
def get_next_open_holding_area(type='Warehouse Holding'):
  open_holding_section = app_tables.table_sections.search(type=type, section='')[0]
  return open_holding_section['table'], open_holding_section['section']

@anvil.server.callable
def move_order_to_holding_area(order_no, holding_table, holding_section):
  old_table_row = app_tables.table_sections.get(order=order_no)
  new_table_row = app_tables.table_sections.get(table=holding_table, section=holding_section)
  order_row = app_tables.openorders.get(order_no=order_no)
  new_table_row.update(order=order_no)
  old_table_row.update(order='')
  order_row.update(reserved_status='Pending', reserved_by='', table_no=holding_table, section=holding_section)

@anvil.server.callable
def mark_no_stock(fulfillment_id):
  f_row = app_tables.openfulfillments.get(fulfillment_id=fulfillment_id)
  f_row.update(status='No Stock')
  hold_section, hold_table = get_next_open_holding_area()
  move_order_to_holding_area(f_row['order_no'], hold_table, hold_section)

@anvil.server.callable
def close_table(table_no):
  table_row = app_tables.tables.get(table=table_no)
  table_row.update(current_user='', status='Testing')

@anvil.server.callable
def link_item_to_fulfillment(fulfillment_id, item_id):
  f_row = app_tables.openfulfillments.get(fulfillment_id=fulfillment_id)
  f_row.update(item_id=item_id, status='Picked')
  order_no = f_row['order_no']
  anvil.server.launch_background_task('update_item_with_fulfillment', order_no, item_id)

@anvil.server.background_task
def update_item_with_fulfillment(order_no, item_id):
  item_row = app_tables.items.get(item_id=item_id)
  item_row.update(order_no=order_no, picked_by=user, picked_on=datetime.now(), status='Picked')
  anvil.server.launch_background_task('add_history_to_item_bk', item_id=item_id, item_status='Picked')
