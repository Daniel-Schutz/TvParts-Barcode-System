import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

import json
import datetime
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from .CommonComponents import Module1
#
#    Module1.say_hello()

def add_event_to_item_history(item_id, item_status, user_full_name, user_role):
  print("Adding item to history from background function (client common call)")
  return anvil.server.call('add_history_to_item', 
                           item_id, 
                           item_status, 
                           user_full_name, 
                           user_role)

def get_sku_from_scan(item_id):
  table_name = "items"
  sku = anvil.server.call('get_sku_from_scan',table_name, item_id)
  return sku

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