import anvil.secrets
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
  json_str = json.dumps(kwargs, indent=0)
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


@anvil.server.callable
def generate_product_qr_code(wait_time=0, **kwargs):
  json_str = json.dumps(kwargs, indent=0)
  api_url = 'https://quickchart.io/qr'
  params = {
  'text': json_str,
  'size': 150, #1 sq inch
  'centerImageUrl': 'https%3A%2F%2Fcdn.shopify.com%2Fs%2Ffiles%2F1%2F0799%2F7915%2F1633%2Ffiles%2F20231108_075153_clipped_rev_1.png%3Fv%3D1699452203',
  'centerImageSizeRatio':0.3
  }
  response = requests.get(api_url, params=params)
  if response.status_code == 200:
    return response.url
  else:
    wait_time += wait_time
    if wait_time > 3:
      raise Exception("Api Error at Generate QR Code.")


@anvil.server.callable
def add_qr_products_bk():
    products = app_tables.products.search()
    for product in products:
        raw_source_url = anvil.server.call('generate_qr_code', 
                                            sku=product['sku'])
        s3_obj_key = anvil.server.call('get_s3_obj_key', raw_source_url)
        s3_img_url = anvil.server.call('get_s3_image_url', s3_obj_key)
        print(s3_img_url)
        break


       