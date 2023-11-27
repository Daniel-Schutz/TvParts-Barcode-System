import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server




@anvil.server.callable
def get_current_table(user):
  try:
    return app_tables.tables.get(current_user=user)['table']
  except:
    return None

# @anvil.server.callable
# def get_open_tables():
#   response = app_tables.tables.search(status="Open")
#   open_tables = [(row['table'], row['table']) for row in response]
#   open_tables.append(('(Select Table)', '(Select Table)'))
#   return open_tables


@anvil.server.callable
def fetch_new_order(user):
  user_current_table = app_tables.tables.get(current_user=user)
  claimed_order = app_tables.openorders.search(reserved_status='Open')[0]
  claimed_order.update(reserved_status = 'Reserved', reserved_by = user)
  # claimed_order['reserved_by'] = user
  return claimed_order

# @anvil.server.callable
# def load_current_order(user):
#   claimed_order = app_tables.openorders.get(reserved_by=user, status='Picking')
#   return claimed_order
  



@anvil.server.callable
def link_order_to_table_section(user, order, table):
  open_section = get_next_open_section(table)
  if not open_section:
    return None
  else:
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
  order_no = str(order_no)
  old_table_row = app_tables.table_sections.get(order=order_no)
  new_table_row = app_tables.table_sections.get(table=holding_table, section=holding_section)
  order_row = app_tables.openorders.get(order_no=int(order_no)) #need to fix this in the shopify handler
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
def link_item_to_fulfillment(fulfillment_id, item_id, user):
  f_row = app_tables.openfulfillments.get(fulfillment_id=fulfillment_id)
  f_row.update(item_id=item_id, status='Picked')
  order_no = f_row['order_no']
  anvil.server.launch_background_task('update_item_with_fulfillment', order_no, item_id, user)

@anvil.server.background_task
def update_item_with_fulfillment(order_no, item_id, user):
  item_row = app_tables.items.get(item_id=item_id)
  item_row.update(order_no=str(order_no), picked_by=user, picked_on=datetime.now(), status='Picked')
  anvil.server.launch_background_task('add_history_to_item_bk', item_id=item_id, item_status='Picked')

########## Needs attention handling ######################
@anvil.server.callable
def get_needs_attention_items(holding_type='Warehouse Hold'):
  search_results = app_tables.table_sections.search(type=holding_type, order=q.not_(''))
  if len(search_results) == 0:
    return None
  else:
    contained_orders = [int(row['order']) for row in search_results] #Need to update order d_type in shopify interface
    order_records = app_tables.openorders.search(order_no=q.any_of(*contained_orders))
    return order_records

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
def get_f_id_from_item_id(item_id):
  f_row = app_tables.openfulfillments.get(item_id=item_id)
  return f_row['fulfillment_id']

@anvil.server.callable
def replace_item_on_fulfillment(old_item_id, new_item_id, old_destiny, user, role):
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
  new_item_row.update(order_no=f_row['order_no'], 
                      status='Picked', 
                      picked_on=datetime.now(), 
                      picked_by=user)
  anvil.server.launch_background_task('add_history_to_item_bk', 
                                      new_item_id, 
                                      'Picked', 
                                      user, 
                                      role)

@anvil.server.callable
def get_open_trays_for_dd():
  open_tray_rows = app_tables.tables.search(type='Tray', status="Open")
  default_val = ("(Select Tray), (Select Tray)")
  open_tray_tup_list = [(row['table'], row['table']) for row in open_tray_rows]
  open_tray_tup_list.append(default_val)
  return open_tray_tup_list

@anvil.server.callable
def move_order_to_tray(order_no, tray):
  old_section_row = app_tables.table_sections.get(order=order_no)
  old_section_row.update(current_user='', order=order_no)
  tray_table_row = app_tables.tables.get(table=tray)
  tray_table_row['status'] = 'Picking'
  new_section_row = app_tables.table_sections.search(table=tray)[0] #we are assuming trays are 1 item entities now
  new_section_row.update(order=order_no)

####### Trays above tables logic ############
# @anvil.server.callable
# def get_pending_pick_trays():
#   pending_trays = app_tables.tables.search(type='Tray', status='Picking')
#   if len(pending_trays) == 0:
#     return None
#   else:
#     default = ("Select Table", "Select Table")
#     pending_trays_vals = [(row['table'], row['table']) for row in pending_trays]
#     pending_trays_vals.append(default)
#     return pending_trays
  
@anvil.server.callable
def reserve_tray(tray, user):
  tray_section_row = app_tables.table_sections.get(table=tray)
  tray_section_row.update(current_user=user)
  tray_table_row = app_tables.tables.get(table=tray)
  tray_table_row.update(current_user=user)

@anvil.server.callable
def tray_complete(order_no):
  f_rows = app_tables.openfulfillments.search(order_no=order_no)
  for fulfillment in f_rows:
    f_status = fulfillment['status']
    if f_status != "Picked":
      return False
  return True