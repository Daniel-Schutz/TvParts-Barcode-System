import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

import requests
import json
import time

# Use of kwargs allows for all 3 barcode types to be passed to the function.
# KEY ORDER:
# Barcode Type 1: Supplier, Truck
# Barcode Type 2: Supplier, Truck, Make, Model, Size, Year, Product UUID, Item UUID
# Barcode Type 3: Bin

@anvil.server.callable
def generate_qr_code(wait_time=0, **kwargs):
  json_str = json.dumps(kwargs, indent=4)
  api_url = 'https://quickchart.io/qr'
  params = {
  'text': json_str,
  'size': 150 #1 sq inch
  }
  response = requests.get(api_url, params=params)
  if response.status_code == 200:
    return response.url
  else:
    wait_time += wait_time
    if wait_time > 3:
      raise Exception("Api Error at Generate QR Code.")
    generate_qr_code(item_info_json, wait_time=wait_time)
