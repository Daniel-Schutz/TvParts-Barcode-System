import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

from datetime import datetime
import json



############################################################
########### Warehouse - Stock ##############################

@anvil.server.callable
def get_primary_bin_from_item_scan(item_scan_str, item_id_delimiter='__'):
  item_id = item_scan_str
  sku = item_id.split(item_id_delimiter)[0]
  prod_row = app_tables.products.get(sku=sku)
  return prod_row['bin']

@anvil.server.callable
def update_item_on_binned(user, role, item_id, bin):
  anvil.server.launch_background_task('update_item_on_binned_bk', user, role, item_id, bin)

@anvil.server.background_task
def update_item_on_binned_bk(user, role, item_id, bin):
  print("THIS IS THE BIN FROM Backgroud:", bin)
  item_row = app_tables.items.get(item_id=item_id)
  current_time = datetime.now()

  item_row.update(status='Binned', 
                  stored_bin=bin, 
                  binned_by=user, 
                  binned_on=current_time)
  anvil.server.launch_background_task('add_history_to_item_bk', 
                                      item_id=item_id, 
                                      item_status='Binned', 
                                      user_full_name=user, 
                                      user_role=role)

@anvil.server.callable
def update_inv_qty_by_item(item_id):
  anvil.server.launch_background_task('update_inv_qty_by_item_bk', item_id)
  pass

@anvil.server.background_task
def update_inv_qty_by_item_bk(item_id):
  item_row = app_tables.items.get(item_id=item_id)
  #Update Inventory Quantity in Shopify
  product_row = app_tables.products.get(sku=item_row['sku'])
  current_inv = anvil.server.call('get_shopify_product_qty', product_id=product_row['product_id'])
  new_inv = int(current_inv) + 1
  anvil.server.call('update_product_inventory_quantity', product_row['product_id'], new_inv)

@anvil.server.callable
def update_item_on_misid(user, role, item_id):
  anvil.server.launch_background_task('update_item_on_misid_bk', user, role, item_id)

@anvil.server.background_task
def update_item_on_misid_bk(user, role, item_id):
  item_row = app_tables.items.get(item_id=item_id)
  current_time = datetime.now()
  item_row.update(status='Misidentified', 
                  verified_by=user, 
                  verified_on=current_time)
  anvil.server.launch_background_task('add_history_to_item_bk', 
                                      item_id=item_id, 
                                      item_status='Misidentified', 
                                      user_full_name=user, 
                                      user_role=role)

@anvil.server.callable
def update_item_on_verify(user, role, item_id):
  sku_needs_fixed_list =  [
    "A2094419A",
    "BN44-00787A",
    "A2229070A",
    "BN44-00874C",
    "A2072545A",
    "BN44-00874D",
    "A-5042-804-A",
    "BN44-00874E",
    "A2094434A",
    "BN44-00874F",
    "A2170503A",
    "BN94-11439A",
    "A2170502A",
    "LT-70MAW795-POWER",
    "A2072564C",
    "100012588-power",
    "A2094368A",
    "A2072555C",
    "A2165797A"
  ]
  item_row = app_tables.items.get(item_id=item_id)
  if item_row['sku'] in sku_needs_fixed_list:
    status = 'Needs Fixed'
    item_status = 'Needs Fixed'
  else:
    status='Verified'
    item_status='Verified'
  current_time = datetime.now()
  item_row.update(status=status, 
                  verified_by=user, 
                  verified_on=current_time)
  anvil.server.launch_background_task('add_history_to_item_bk', 
                                      item_id=item_id, 
                                      item_status=item_status, 
                                      user_full_name=user, 
                                      user_role=role)
  return status



@anvil.server.callable
def get_other_bins_dd(primary_bin):
  other_bins_list = anvil.server.call('get_all_bins_from_primary', primary_bin)
  default_val = ("(Select Bin)", "(Select Bin)")
  if not other_bins_list:
    return [default_val]
  bin_tups = [(bin, bin) for bin in other_bins_list]
  bin_tups.append(default_val)
  return bin_tups

@anvil.server.callable
def add_new_bin_for_item(item_id, new_bin, item_id_delimiter="__"):
  sku = item_id.split(item_id_delimiter)[0]
  bin_row = app_tables.bins.get(bin=new_bin)
  product_row = app_tables.products.get(sku=sku)
  bin_row.update(sku=sku, bin_status='filled', product_id=product_row['product_id'])
  old_os_bins = product_row['os_bins']
  product_row.update(os_bins = old_os_bins + f", {new_bin}")

@anvil.server.callable
def add_bin_to_purgatory(user, role, bin, item_id, item_id_delimiter="__"):
  sku = item_id.split(item_id_delimiter)[0]
  product_row = app_tables.products.get(sku=sku)
  bin_row = app_tables.bins.get(bin=bin)
  app_tables.purgatory.add_row(bin=bin, 
                               cross_refs=product_row['cross_refs'], 
                               os_bins=product_row['os_bins'], 
                               product_name=product_row['product_name'], 
                               purgatory_count=0, 
                               sku=sku)
  add_item_to_purgatory(user, role, bin, item_id)

@anvil.server.callable
def add_item_to_purgatory(user, role, bin, item_id, item_id_delimiter="__"):
  item_row = app_tables.items.get(item_id=item_id)
  purg_row = app_tables.purgatory.get(bin=bin)
  purg_row['purgatory_count'] += 1
  item_row.update(status='Purgatory')
  anvil.server.launch_background_task('add_history_to_item_bk', 
                                      item_id=item_id, 
                                      item_status='Purgatory', 
                                      user_full_name=user, 
                                      user_role=role)

@anvil.server.callable
def get_bins_in_purgatory():
  purg_rows = app_tables.purgatory.search()
  return[row['bin'] for row in purg_rows]

############################################################
############################################################




############################################################
########### Warehouse - Pick ##############################

@anvil.server.callable
def fetch_new_order(user):
  user_current_table = app_tables.tables.get(current_user=user)
  claimed_order = app_tables.openorders.search(reserved_status='Open')[0]
  claimed_order.update(reserved_status = 'Reserved', reserved_by = user)
  # claimed_order['reserved_by'] = user
  return claimed_order

@anvil.server.callable
def link_order_to_table_section(user, order, table):
  open_section = anvil.server.call('get_next_open_section', table)
  if not open_section:
    return None
  else:
    current_order = app_tables.openorders.get(reserved_status='Reserved', reserved_by=user)
    # current_order = current_order[0]
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

def revert_order_to_new(order_no):
  order_row = app_tables.openorders.get(order_no=order_no)
  order_row.update(status='New', reserved_by='', reserved_status='Open', table_no='', section='')
  section_row = app_tables.table_sections.get(order=str(order_no))
  section_row.update(order='')

@anvil.server.callable
def force_close_pick_table(user):
  picking_row = app_tables.openorders.get(reserved_by=user)
  if picking_row:
    order_no = picking_row['order_no']
    revert_order_to_new(order_no)
  


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
def link_item_to_fulfillment(fulfillment_id, item_id, user, role):
  f_row = app_tables.openfulfillments.get(fulfillment_id=fulfillment_id)
  f_row.update(item_id=item_id, status='Picked')
  order_no = f_row['order_no']
  anvil.server.launch_background_task('update_item_with_fulfillment', order_no, item_id, user, role)

@anvil.server.background_task
def update_item_with_fulfillment(order_no, item_id, user, role): #need to add the user and role everywhere this is called
  item_row = app_tables.items.get(item_id=item_id)
  current_time = datetime.now()
  item_row.update(order_no=str(order_no), picked_by=user, picked_on=current_time, status='Picked')
  anvil.server.launch_background_task('add_history_to_item_bk', 
                                      item_id=item_id, 
                                      item_status='Picked', 
                                      user_full_name=user, 
                                      user_role=role)

#Needs attention handling moved to SharedFunctions

@anvil.server.callable
def get_open_trays_for_dd():
  open_tray_rows = app_tables.tables.search(type='Tray', status="Open")
  default_val = ("(Select Tray)", "(Select Tray)")
  open_tray_tup_list = [(row['table'], row['table']) for row in open_tray_rows]
  open_tray_tup_list.append(default_val)
  return open_tray_tup_list

@anvil.server.callable
def move_order_to_tray(order_no, tray, status):
  old_section_row = app_tables.table_sections.get(order=str(order_no))
  old_section_row.update(current_user='', order='')
  tray_table_row = app_tables.tables.get(table=tray)
  tray_table_row['status'] = status
  order_row = app_tables.openorders.get(order_no=order_no)
  order_row.update(table_no=tray, section='A') #always "A", because Trays are 1-item entities
  new_section_row = app_tables.table_sections.search(table=tray)[0]
  new_section_row.update(order=str(order_no))

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

@anvil.server.callable
def get_all_fulfillments():
  return app_tables.openfulfillments.search()

@anvil.server.callable
def get_f_row_by_f_id(f_id):
  return app_tables.openfulfillments.get(fulfillment_id=f_id)