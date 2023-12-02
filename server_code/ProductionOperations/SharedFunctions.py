import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

from datetime import datetime

@anvil.server.callable
def get_next_order(user, table_no, search_status, new_status): 
  next_order = app_tables.openorders.search(table_no=table_no, 
                                            status=search_status)
  if len(next_order) > 0:
    next_order = next_order[0]
    next_order.update(reserved_status='Reserved', reserved_by=user, status=new_status)
  else:
    next_order = None
  return next_order

@anvil.server.callable
def set_f_status_by_item_id(item_id, status):
  f_row = app_tables.openfulfillments.get(item_id=item_id)
  f_row['status'] = status

@anvil.server.callable
def get_current_table(user):
  try:
    return app_tables.tables.get(current_user=user)['table'] #look at converting this so it returns the whole row. Might as well to be consistent
  except:
    return None

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
  row['status'] = status
  print('Assigned Table.')
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

@anvil.server.callable
def close_table(table_no, status):
  table_row = app_tables.tables.get(table=table_no)
  table_row.update(current_user='', status=status)
  section_rows = app_tables.table_sections.search(table=table_no)
  for row in section_rows:
    row['current_user'] = ''

@anvil.server.callable
def close_order_in_db(order_no, status):
  closed_order_row = app_tables.openorders.get(order_no=order_no)
  closed_order_row.update(reserved_by='', reserved_status='Pending', status=status)


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


############ Holding Areas ##############
@anvil.server.callable
def get_needs_attention_orders(holding_type, dept):
  search_results = app_tables.table_sections.search(type=holding_type, order=q.not_(''))
  if len(search_results) == 0:
    return None
  else:
    contained_orders = [int(row['order']) for row in search_results] #Need to update order d_type in shopify interface
    order_records = app_tables.openorders.search(order_no=q.any_of(*contained_orders))
    
    modified_records = []
    for record in order_records:
      # Convert the row to a dictionary and add the department
      record_dict = dict(record)
      record_dict['dept'] = dept
      modified_records.append(record_dict)
    return modified_records

@anvil.server.callable
def get_all_needs_attention_orders():
  search_results = app_tables.table_sections.search(type=q.any_of('Warehouse Hold', 'Testing Hold', 'Shipping Hold'), order=q.not_(''))
  if len(search_results) == 0:
    return None
  else:
    contained_orders = [int(row['order']) for row in search_results] #Need to update order d_type in shopify interface
    order_records = app_tables.openorders.search(order_no=q.any_of(*contained_orders))

@anvil.server.callable
def set_fulfillment_status(fulfillment_id, status):
  f_row = app_tables.openfulfillments.get(fulfillment_id=fulfillment_id)
  f_row['status'] = status

@anvil.server.callable
#current issue: This gets called after the deletion so there is no way to get the restock
def restock_linked_item(f_id, user, user_role):
  f_row = app_tables.openfulfillments.get(fulfillment_id=f_id)
  if f_row['item_id'] == '':
    return None
  else:
    item_row = app_tables.items.get(item_id=f_row['item_id'])
    
    #this line also unlinks from fulfillment
    f_row.update(item_id='', status='New')
    
    item_row.update(status='Binned', order_no='')
    anvil.server.launch_background_task('add_history_to_item_bk', 
                                        f_row['item_id'], 
                                        'Binned', 
                                        user, 
                                        user_role)
  return item_row['stored_bin']

@anvil.server.callable
def reset_order(order_no):
  order_row = app_tables.openorders.get(order_no=order_no)
  order_row.update(status='New', 
                   table_no='(Not Set)', 
                   section='(Not Set)', 
                   reserved_status='Open', 
                   reserved_by='')
  section_row = app_tables.table_sections.get(order=str(order_no)) #this might not be an appropriate state, we will see during testing
  section_row.update(order='', current_user='')

# fully removes the order and fulfillments from the system
@anvil.server.callable
def delete_order(order_no):
  section_row = app_tables.table_sections.get(order=str(order_no))
  section_row.update(order='', current_user='')
  #delete rows of orders and fulfillments
  anvil.server.launch_background_task('delete_rows_bk', 'openorders', 'order_no', order_no)
  anvil.server.launch_background_task('delete_rows_bk', 'openfulfillments', 'order_no', order_no)

#Removes a singular fulfillment from the system
@anvil.server.callable
def remove_fulfillment_by_item_id(item_id, user, user_role):
  anvil.server.call('delete_rows', 'openfulfillments', 'item_id', item_id)
  item_row = app_tables.items.get(item_id=item_id)
  item_row.update(status='Binned', order_no='')
  anvil.server.launch_background_task('add_history_to_item_bk', 
                                      f_row['item_id'], 
                                      'Binned', 
                                      user, 
                                      user_role)  

@anvil.server.callable
def get_sku_from_f_id(fulfillment_id):
  f_row = app_tables.openfulfillments.get(fulfillment_id=fulfillment_id)
  return f_row['sku']

@anvil.server.callable
def get_f_id_from_item_id(item_id):
  f_row = app_tables.openfulfillments.get(item_id=item_id)
  return f_row['fulfillment_id']

@anvil.server.callable
def set_f_status_from_item_id(item_id, status):
  f_row = app_tables.openfulfillments.get(item_id=item_id)
  f_row.update(status=status)

@anvil.server.callable
def replace_item_on_fulfillment(old_item_id, new_item_id, old_destiny, user, role, item_status):
  old_item_row = app_tables.items.get(item_id=old_item_id)
  f_row = app_tables.openfulfillments.get(item_id=old_item_id)
  f_row.update(item_id=new_item_id)
  if old_destiny == 'Fixed':
    old_item_row.update(status='Needs Fixed', order_no='')
    anvil.server.launch_background_task('add_history_to_item_bk', 
                                        old_item_id, 
                                        'Needs Fixed', 
                                        user, 
                                        role)
  elif old_destiny == 'Restocked':
    old_item_row.update(status='Binned', order_no='', binned_on=datetime.now(), binned_by=user)
    anvil.server.launch_background_task('add_history_to_item_bk', 
                                        old_item_id, 
                                        'Binned', 
                                        user, 
                                        role)    
  elif old_destiny == 'Tossed':
    old_item_row.update(status='Tossed', order_no='')
    anvil.server.launch_background_task('add_history_to_item_bk', 
                                        old_item_id, 
                                        'Tossed', 
                                        user, 
                                        role)
    #Add argument to subtract stock from Shopify & sync here
  new_item_row = app_tables.items.get(item_id=new_item_id)
  new_item_row.update(order_no=str(f_row['order_no']), 
                      status=item_status, 
                      picked_on=datetime.now(), 
                      picked_by=user)
  anvil.server.launch_background_task('add_history_to_item_bk', 
                                      new_item_id, 
                                      item_status, 
                                      user, 
                                      role)