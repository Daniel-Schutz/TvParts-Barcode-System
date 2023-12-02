import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_needs_fixed_items():
  search_results = app_tables.items.search(status='Needs Fixed')
  if len(search_results) == 0:
    return None
  else:
    return search_results

@anvil.server.callable
def get_id_holding_count():
  setting_row = app_tables.management_settings.get(setting_title='ID Holding Count')
  return setting_row['num_response']

@anvil.server.callable
def set_id_holding_count(count):
  setting_row = app_tables.management_settings.get(setting_title='ID Holding Count')
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

################# End Reset Table Helpers #################################

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