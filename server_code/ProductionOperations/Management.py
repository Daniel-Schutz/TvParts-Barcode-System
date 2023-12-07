import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from anvil.tables.query import greater_than, less_than, like, ilike, greater_than_or_equal_to, less_than_or_equal_to


from datetime import datetime
import pandas as pd

##############################################################
######################### Action Panel #######################
@anvil.server.callable
def get_needs_fixed_items():
  search_results = app_tables.items.search(status='Needs Fixed')
  if len(search_results) == 0:
    return None
  else:
    return search_results

@anvil.server.callable
def get_id_holding_count():
  setting_row = app_tables.management_settings.get(setting_title='Id Holding Count')
  return setting_row['num_response']

@anvil.server.callable
def set_id_holding_count(count):
  setting_row = app_tables.management_settings.get(setting_title='Id Holding Count')
  setting_row.update(num_response=count)


############# Helpers for resetting the open order/fulfillment tables (formerly order management) ###########
#Prevent getting obsolete orders
def cut_open_dfs_by_date(orders_df, fulfullments_df, days_away=7):
  now = datetime.datetime.now()
  cutoff = now - datetime.timedelta(days=days_away)
  orders_df = orders_df[orders_df['created'] >= cutoff]
  order_no_list = orders_df['order_no'].to_list()
  fulfillments_df = fulfullments_df[fulfullments_df['order_no'].isin(order_no_list)]
  return orders_df, fulfillments_df

def get_all_open_orders():
  def str_to_program_time(datetime_str):
    no_tz_str = '-'.join(datetime_str.split("-")[:3])
    return datetime.datetime.strptime(no_tz_str, '%Y-%m-%dT%H:%M:%S')
  open_orders = anvil.server.call('get_open_orders_from_shopify')
  order_records = []
  fulfillment_records = []
  for order in open_orders:
    this_order_dict = {}
    this_order_dict['order_no'] = order['order_number']
    this_order_dict['created'] = order['created_at']
    this_order_dict['status'] = 'New'
    this_order_dict['customer_name'] = order['shipping_address']['name'] if order['shipping_address'] else '(Not Provided)'
    this_order_dict['email'] = order['contact_email']
    this_order_dict['phone'] = order['billing_address']['phone']
    try:
      this_order_dict['address'] = ' '.join([order['shipping_address']['address1'], 
                                            order['shipping_address']['city'],
                                            order['shipping_address']['province_code'],
                                            order['shipping_address']['zip']])
    except:
      this_order_dict['address'] = '(Not Provided)'
    this_order_dict['table_no'] = '(Not Set)'
    this_order_dict['section'] = '(Not Set)'
    this_order_dict['total_price'] = float(order['current_total_price'])
    total_item_count = 0
    for line_item in order['line_items']:
      total_item_count += line_item['quantity']
    this_order_dict['total_items'] = total_item_count
    this_order_dict['reserved_status'] = 'Open'
    this_order_dict['reserved_by'] = ''
    this_order_dict['notes'] = ''
    order_records.append(this_order_dict)
    for line_item in order['line_items']:
      for i in range(line_item['quantity']):
        this_fulfillment_dict = {}
        this_fulfillment_dict['fulfillment_id'] = str(uuid.uuid4())
        this_fulfillment_dict['order_no'] = order['order_number']
        this_fulfillment_dict['status'] = 'New'
        this_fulfillment_dict['product_name'] = line_item['name']
        this_fulfillment_dict['sku'] = line_item['sku']
        this_fulfillment_dict['item_id'] = ''
        fulfillment_records.append(this_fulfillment_dict)
  orders_df = pd.DataFrame(order_records)
  fulfillments_df = pd.DataFrame(fulfillment_records)
  orders_df['created'] = orders_df['created'].apply(str_to_program_time)
  
  #TODO: Get rid of orders that will never be fulfilled - requires tvparts feedback
  orders_df, fulfillments_df = cut_open_dfs_by_date(orders_df, fulfillments_df)
  
  return orders_df, fulfillments_df


def remove_packed_orders():
  for row in app_tables.openorders.search(status='Packed'):
    row.delete()
  for row in app_tables.openfulfillments.search(status='Packed'):
    row.delete()


def get_existing_order_numbers():
  return [row['order_no'] for row in app_tables.openorders.search()]

###########################################################################

########## Reset Order & Fulfillment Tables ###############################
#This is the "Big Reset" at the beginning of each pick batch
@anvil.server.callable
def reset_open_tables():
  start_time = time.time()
  remove_packed_orders()
  print("removed Packed Orders")
  orders_df, fulfillments_df = get_all_open_orders()
  print("pandas magic")
  existing_orders = get_existing_order_numbers()
  orders_df = orders_df[~orders_df['order_no'].isin(existing_orders)]
  fulfillments_df = fulfillments_df[~fulfillments_df['order_no'].isin(existing_orders)]
  print('removed remaining orders')
  order_records = orders_df.to_dict('records')
  fulfillment_records = fulfillments_df.to_dict('records')
  anvil.server.launch_background_task('add_full_records_to_table', 
                    order_records, 
                    'openorders')
  anvil.server.launch_background_task('add_full_records_to_table', 
                    fulfillment_records, 
                    'openfulfillments')
  print("updated anvil datatables")
  end_time = time.time()
  print(f'big update success! required {round(end_time-start_time, 2)} seconds')
############################################################################

############# Purgatory #################################################
@anvil.server.callable
def get_purgatory_bins():
  results = app_tables.purgatory.search()
  if len(results) == 0:
    return None
  else:
    return results

@anvil.server.callable
def get_purgatory_items():
  results = app_tables.items.search(status='Purgatory')
  if len(results) == 0:
    return None
  else:
    return results

@anvil.server.callable
def remove_bin_only_from_purgatory(bin):
  delete_row = app_tables.purgatory.get(bin=bin)
  delete_row.delete()

@anvil.server.callable
def get_open_bins_dropdown():
  open_bin_rows = app_tables.bins.search(bin_status='open')
  if len(open_bin_rows) == 0:
    return [('No Empty Bins', 'No Empty Bins')]
  else:
    open_bin_rows = [(row['bin'], row['bin']) for row in open_bin_rows]
    open_bin_rows.append(('(Select Bin)', '(Select Bin)'))
    return open_bin_rows

@anvil.server.callable
def purg_all_items_to_new_bin(user, role, new_bin, primary_bin):
  purg_row = app_tables.purgatory.get(bin=primary_bin)
  sku = purg_row['sku']
  purg_row.delete()
  new_bin_row = app_tables.bins.get(bin=new_bin)
  new_bin_row.update(bin_status='filled', sku=sku)
  items_to_move = app_tables.items.search(sku=sku, status='Purgatory')
  for item_row in items_to_move:
    item_row.update(status='binned', stored_bin=new_bin, binned_on=datetime.now(), binned_by=user)
    anvil.server.launch_background_task('add_history_to_item_bk', item_row['item_id'], 'Binned', user, role)
  pass

@anvil.server.callable
def purg_toss_all_items(user, role, primary_bin):
  purg_row = app_tables.purgatory.get(bin=primary_bin)
  sku = purg_row['sku']
  purg_row.delete()
  items_to_toss = app_tables.items.search(sku=sku, status='Purgatory')
  for item_row in items_to_toss:
    anvil.server.call('toss_item', user, item_row, item_row['item_id'])

########################################################
########################################################

########################################################
########## Control Panel (Settings) ####################

@anvil.server.callable
def get_full_roles_dropdown():
  default_val = ('(Select Role)', '(Select Role)')
  all_role_rows = app_tables.roles.search()
  role_tups = [(row['role'], row['role']) for row in all_role_rows]
  role_tups.append(default_val)
  return role_tups

@anvil.server.callable
def get_users_dropdown():
  def get_full_name(row):
    return row['first_name'] + " " + row['last_name']
  default_val = ('(Select User)', '(Select User)')
  all_user_rows = app_tables.users.search()
  user_tups = [(get_full_name(row), row['email']) for row in all_user_rows]
  user_tups.append(default_val)
  return user_tups

@anvil.server.callable
def set_user_to_role(user_email, role): #email is what comes back from the selector. see above
  user_row = app_tables.users.get(email=user_email)
  user_row.update(role=role)

##### Bulk Order/Fulfillment Logic
def build_upload_records_bk(records, table_name):
  records = section_records
  batch_size = 50  # Adjust batch size as needed
  for start in range(0, len(records), batch_size):
    end = start + batch_size
    batch = records[start:end]
    anvil.server.call('import_full_table_to_anvil', table_name , batch)
    print(f"{end} records of {len(records)} uploaded.")

def get_open_orders_from_shopify():
  def str_to_program_time(datetime_str):
      no_tz_str = '-'.join(datetime_str.split("-")[:3])
      return datetime.datetime.strptime(no_tz_str, '%Y-%m-%dT%H:%M:%S')
  open_orders = anvil.server.call('get_open_orders_from_shopify')
  order_records = []
  fulfillment_records = []
  for order in open_orders:
    this_order_dict = {}
    this_order_dict['order_no'] = order['order_number'] #make order number a string here when rebuilding DBs
    this_order_dict['created'] = order['created_at']
    this_order_dict['status'] = 'New'
    this_order_dict['customer_name'] = order['shipping_address']['name'] if order['shipping_address'] else '(Not Provided)'
    this_order_dict['email'] = order['contact_email']
    this_order_dict['phone'] = order['billing_address']['phone']
    try:
      this_order_dict['address'] = ' '.join([order['shipping_address']['address1'], 
                                            order['shipping_address']['city'],
                                            order['shipping_address']['province_code'],
                                            order['shipping_address']['zip']])
    except:
      this_order_dict['address'] = '(Not Provided)'
    this_order_dict['table_no'] = '(Not Set)'
    this_order_dict['section'] = '(Not Set)'
    this_order_dict['total_price'] = float(order['current_total_price'])
    total_item_count = 0
    for line_item in order['line_items']:
      total_item_count += line_item['quantity']
    this_order_dict['total_items'] = total_item_count
    this_order_dict['reserved_status'] = 'Open'
    this_order_dict['reserved_by'] = ''
    order_records.append(this_order_dict)
    for line_item in order['line_items']:
      for i in range(line_item['quantity']):
        this_fulfillment_dict = {}
        this_fulfillment_dict['fulfillment_id'] = str(uuid.uuid4())
        this_fulfillment_dict['order_no'] = order['order_number']
        this_fulfillment_dict['status'] = 'New'
        this_fulfillment_dict['product_name'] = line_item['name']
        this_fulfillment_dict['sku'] = line_item['sku']
        this_fulfillment_dict['item_id'] = ''
        fulfillment_records.append(this_fulfillment_dict)
  orders_df = pd.DataFrame(order_records)
  fulfillments_df = pd.DataFrame(fulfillment_records)
  orders_df['created'] = orders_df['created'].apply(str_to_program_time)
  return orders_df, fulfillments_df

def refresh_pick_batch(orders_df, fulfillments_df):  
  #Step 1: Remove all orders/fulfillments that have been packed
  for row in app_tables.openorders.search(status='Packed'):
    row.delete()
  for row in app_tables.openfulfillments.search(status='Packed'):
    row.delete()
  #Step 2: Remove any Orders/fulfillments already in Anvil
  existing_orders = [row['order_no'] for row in app_tables.openorders.search()]
  added_orders_df = orders_df[~orders_df['order_no'].isin(existing_orders)]
  added_fulfillments_df = fulfillments_df[~fulfillments_df['order_no'].isin(existing_orders)]
  #Step 3: Add remaining Orders/fulfillments to Anvil
  added_order_records = added_orders_df.to_records()
  added_fulfillment_records = added_fulfillments_df.to_records()
  build_upload_records_bk(added_order_records, 'openorders')
  build_upload_records_bk(added_fulfillment_records, 'openfulfillments')

@anvil.server.background_task
def refresh_orders_and_fulfillments_bk():
  orders_df, fulfillments_df = get_open_orders_from_shopify()
  refresh_pick_batch(orders_df, fulfillments_df)

@anvil.server.callable
def refresh_orders_and_fulfillment():
  anvil.server.launch_background_task('refresh_orders_and_fulfillments_bk')

#easy delete module
@anvil.server.background_task
def clear_all_orders_fulfillments_bk():
  for row in app_tables.openorders.search():
    row.delete()
  for row in app_tables.openfulfillments.search():
    row.delete()

@anvil.server.callable
def clear_all_orders_fulfillments():
  anvil.server.launch_background_task('clear_all_orders_fulfillments_bk')

## Set Admin Pass Logic
@anvil.server.callable
def get_admin_passcode():
  settings_row = app_tables.management_settings.get(setting_title='Admin Passcode')
  return settings_row['text_response']

@anvil.server.callable
def set_admin_passcode(passcode):
  settings_row = app_tables.management_settings.get(setting_title='Admin Passcode')
  settings_row.update(text_response=passcode)

## Bin Mode Logic
@anvil.server.callable
def get_bin_stock_mode():
  settings_row = app_tables.management_settings.get(setting_title='Bin Stock Mode')
  return settings_row['text_response']  

@anvil.server.callable
def set_bin_stock_mode(mode):
  settings_row = app_tables.management_settings.get(setting_title='Bin Stock Mode')
  settings_row.update(text_response=mode) 
########################################################
########################################################

########################################################
########## Role Navigation Panel  ######################

# Nothing here!

########################################################
########################################################

########################################################
########## Edit datatables functions  ##################

@anvil.server.callable
def get_table_name_dropdown():
  table_names_rows = app_tables.table_registry.search()
  table_dropdown = [(row['table_display'], row['table_name']) for row in table_names_rows]
  table_dropdown.append(('(Select Table)', '(Select Table)'))
  return table_dropdown

def get_cols_from_table(table_name):
  table=getattr(app_tables, table_name)
  columns = table.list_columns()
  return columns

@anvil.server.callable
def get_table_len(table_name):
  table=getattr(app_tables, table_name, None)
  len_table = len(table.search())
  return len_table
  
@anvil.server.callable
def get_col_names_for_dd(table_name):
  columns = get_cols_from_table(table_name)
  cols_from_table = [(col['name'], col['name']) for col in columns]
  cols_from_table.append(('(Select Column)', '(Select Column)'))
  return cols_from_table

@anvil.server.callable
def get_col_type_dict_for_mapping(table_name):
  columns = get_cols_from_table(table_name)
  return {col['name']:col['type'] for col in columns}

@anvil.server.callable
def get_num_compare_dd():
  num_compare_dict = {
    'Greater Than': '>',
    'Equal To': '=',
    'Less Than': '<',
  }
  default_val = ('(Select Condition)', '(Select Condition)')
  cond_choices = list(num_compare_dict.keys())
  cond_tups = [(k,k) for k in cond_choices]
  cond_tups.append(default_val)
  return cond_tups

@anvil.server.callable
def get_string_compare_dd():
  string_compare_dict = {
    'Contains': 'contains',
    'Equal To': 'equals',
    #'Does Not Contain': 'does not contain',
    # 'Not Equal To': 'not equal to',
  }
  default_val = ('(Select Condition)', '(Select Condition)')
  cond_choices = list(string_compare_dict.keys())
  cond_tups = [(k,k) for k in cond_choices]
  cond_tups.append(default_val)
  return cond_tups

@anvil.server.callable
def query_test():
  query_dict = {'sku': ilike('%4%'), 'bin_type': ilike('standard')}
  return app_tables.bins.search(q.all_of(**query_dict))

@anvil.server.callable
def get_filtered_data(table_name, filters): #filters is a list of dicts with keys 'column_name', 'comparison', 'value'
  table=getattr(app_tables, table_name)
  query_conditions = []

  # Mapping of comparison methods to Anvil query functions
  comparison_methods = {
      'Greater Than': greater_than,
      'Greater or Equal To': greater_than_or_equal_to,
      'Less Than': less_than,
      'Less or Equal To': less_than_or_equal_to,
      'Equal To': ilike,
      'Contains': ilike,  # Using 'like' for 'contains' (for string columns)
  }
  
  
  # Construct query conditions
  query_dict = {}
  for filter_cond in filters:
    column_name = filter_cond.get('column_name')
    comparison = filter_cond.get('comparison')
    value = filter_cond.get('value')
    compare_func = comparison_methods[comparison]
    if comparison == 'Contains':
      query_dict[column_name] = compare_func(f"%{value}%")
    else:
      query_dict[column_name] = compare_func(value)

  result = table.search(**query_dict)
  return result