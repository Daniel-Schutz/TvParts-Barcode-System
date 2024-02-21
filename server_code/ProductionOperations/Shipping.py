import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

from datetime import datetime

@anvil.server.callable
def remove_order_from_table(order_no):
  anvil.server.launch_background_task('remove_order_from_table_bk', order_no)

@anvil.server.background_task
def remove_order_from_table_bk(order_no):
  table_sec_row = app_tables.table_sections.get(order=str(order_no))
  table_sec_row.update(order='')
  order_row = app_tables.openorders.get(order_no=order_no)
  order_row.update(reserved_by='', reserved_status='Finished', table_no='', section='')

@anvil.server.callable
def pack_order_and_fulfillments(user, role, order_no): #probably an opp to save time here with bk tasks
  #get order row, set status to packed
  order_row = app_tables.openorders.get(order_no=order_no)
  order_row.update(status='Sold', reserved_by=user, reserved_status='Finished', table_no='', section='') #finished status used for deletion when table completes
  #get all fulfillment rows
  f_rows = app_tables.openfulfillments.search(order_no=order_no)
  #for each fulfillment row, set fulfillment to packed, and item status to packed
  for row in f_rows:
    row.update(status='Packed')
    item_id = row['item_id']
    anvil.server.launch_background_task('update_items_sold_bk', 
                                        user, 
                                        role, 
                                        item_id)
  #add history for each item
  pass

@anvil.server.background_task
def update_items_sold_bk(user, role, item_id):
  item_row = app_tables.items.get(item_id=item_id)
  item_row.update(packed_on=datetime.now(), packed_by=user, status='Sold')


@anvil.server.callable
def close_table_and_remove_orders(table_no, status, user):
  order_rows = app_tables.openorders.search(reserved_status='Finished', table_no=table_no)
  order_no_list = [row['order_no'] for row in order_rows]
  anvil.server.launch_background_task('remove_packed_orders_from_system_bk', user, order_no_list)
  table_row = app_tables.tables.get(table=table_no)
  table_row.update(current_user='', status=status)
  section_rows = app_tables.table_sections.search(table=table_no)
  for row in section_rows:
    row['current_user'] = ''

# @anvil.server.callable
# def remove_packed_orders_from_system(user): 
#   #we use user to make sure only orders on the table they packed get deleted
#   #we also make this background process so it doesn't affect UX
#   anvil.server.launch_background_task('remove_packed_orders_from_system_bk')

@anvil.server.background_task
def remove_packed_orders_from_system_bk(user, order_no_list):
  for order_no in order_no_list:
    anvil.server.call('delete_rows', 'openfulfillments', 'order_no', order_no)
    anvil.server.call('delete_rows', 'openorders', 'order_no', order_no)
    