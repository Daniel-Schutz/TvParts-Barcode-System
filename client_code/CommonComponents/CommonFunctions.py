import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

import json
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from .CommonComponents import Module1
#
#    Module1.say_hello()
#
def get_id_from_scan(scan_input_str, mode='product'):
  scan_dict = json.loads(scan_input_str)
  if mode == 'product':
    sku = scan_dict['sku']
    return sku
  elif mode == 'item':
    item_id = scan_dict['item_id']
    return item_id
  else:
    print('Error in C.CommonFunctions - mode for get_id_from_scan must be "product" or "item". Returned None.')
    return None

def get_full_product_from_scan(scan_input_str):
  sku = get_id_from_scan(scan_input_str, mode='product')
  raw_product_call = anvil.server.call('search_rows', 
                                       'products', 
                                       'sku', 
                                       sku)
  product_dict = [row.to_dict() for row in raw_product_call][0]
  return product_dict

def get_full_item_from_scan(scan_input_str):
  item_id = get_id_from_scan(scan_input_str, mode='item')
  item_dict = anvil.server.call('get_full_item')
  return item_dict

def update_item(item_id, col_name, value):
  return anvil.server.call('set_value_in_dynamo', 
                           'unique_item', 
                           item_id, 
                           col_name, 
                           value)