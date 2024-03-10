import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import re
import os
import json
import pandas as pd
import boto3
import requests
import time
from decimal import Decimal


@anvil.server.callable
def clean_up_skus():
  empty_rows = app_tables.products.search(sku=q.any_of('', None))
  return empty_rows

@anvil.server.background_task
def clean_up_skus_bk():
  empty_rows = app_tables.products.search(sku=q.any_of('', None))

#This takes in 1 for increase, -1 for decrease
@anvil.server.callable
def adjust_inventory_by_product_id(product_id, adjustment):
  shop_key = anvil.secrets.get_secret('shopify_admin_key')
  shop = ShopifyInterface(shop_key)
  response_json = shop.adjust_inventory_by_product_id(product_id, adjustment)
  return response_json
  

@anvil.server.callable
def import_new_products():
  anvil.server.launch_background_task('import_new_products_bk')

@anvil.server.background_task
def import_new_products_bk():
  def html_to_raw(html_string):
    html_string = str(html_string)
    text = re.sub(r'<[^>]+>', '', html_string)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('\xa0', ' ')
    return text
  def shop_to_db_convert(shop_record):
    db_record = {
        'bin': '0' if 'bin' in shop_record else None,
        'cross_refs': '' if 'cross_refs' in shop_record else None,
        'description': html_to_raw(shop_record['body_html']) if 'body_html' in shop_record else None,
        'img_source_url': shop_record['images'][0]['src'] if 'images' in shop_record and shop_record['images'] else None,
        'os_bins': '' if 'os_bins' in shop_record else None,
        'price': float(shop_record['variants'][0]['price']) if 'variants' in shop_record and shop_record['variants'] else None,
        'product_id': str(shop_record['id']) if 'id' in shop_record else None,
        'product_name': shop_record['title'] if 'title' in shop_record else None,
        's3_object_key': '' if 's3_object_key' in shop_record else None,
        'shopify_qty': shop_record['variants'][0]['inventory_quantity'] if 'variants' in shop_record and shop_record['variants'] else None,
        'sku': shop_record['variants'][0]['sku'] if 'variants' in shop_record and shop_record['variants'] else None,
        'type': shop_record['product_type'] if 'product_type' in shop_record else None,
        'vendor': shop_record['vendor'] if 'vendor' in shop_record else None
    }
    return db_record
  shop_key = anvil.secrets.get_secret('shopify_admin_key')
  shop = ShopifyInterface(shop_key)
  all_products = shop.get_all_products(True)
  skus = []
  for product in all_products:
    product_id = str(product['id'])
    row = app_tables.products.search(product_id=product_id)
    if len(row) == 0:
      kwargs = shop_to_db_convert(product)
      app_tables.products.add_row(**kwargs)
      sku = product['variants'][0]['sku']
      skus.append(sku)
  anvil.server.call('create_message', 
                        'New products Bot',
                       'Management',
                       'Management',
                       f'The skus of the new products added are:{skus}',
                       '')



@anvil.server.callable
def get_open_orders_from_shopify():
  shop_key = anvil.secrets.get_secret('shopify_admin_key')
  shop = ShopifyInterface(shop_key)
  raw_open_orders = shop.get_all_open_orders(paginate=True)
  return raw_open_orders

@anvil.server.callable
def get_part_info_from_shopify(product_id):
  shop_key = anvil.secrets.get_secret('shopify_admin_key')
  shop = ShopifyInterface(shop_key)
  part_info = shop.get_product_details(product_id)
  return part_info


@anvil.server.callable
def update_product_inventory_quantity(product_id, new_inventory_quantity):
  shop_key = anvil.secrets.get_secret('shopify_admin_key')
  shop = ShopifyInterface(shop_key)
  shop.update_product_inventory_quantity(product_id, new_inventory_quantity)

@anvil.server.callable
def get_all_products(paginate=True):
  shop_key = anvil.secrets.get_secret('shopify_admin_key')
  shop = ShopifyInterface(shop_key)
  all_products = shop.get_all_products(paginate)
  return all_products

@anvil.server.callable
def get_shopify_product_qty(product_id):
  shop_key = anvil.secrets.get_secret('shopify_admin_key')
  shop = ShopifyInterface(shop_key)
  product_info = shop.get_product_details(product_id)
  return product_info['variants'][0]['inventory_quantity']

@anvil.server.callable
def get_product_metafields(product_id):
  shop_key = anvil.secrets.get_secret('shopify_admin_key')
  shop = ShopifyInterface(shop_key)
  product_metafields = shop.get_product_metafields(product_id)
  return product_metafields
  


class ShopifyInterface:
    
    def __init__(self, shop_key):
        self.shop_url = 'tv-parts-today.myshopify.com'
        self.access_key = shop_key
        self.api_version = '2024-01'
        self.base_url = f"https://{self.shop_url}/admin/api/{self.api_version}/"
        self.auth_headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_key
        }
        self.pagination_wait_time = 0.33 #Prevent rate limiting

       
 ########## Pagination Helper function ########################
    def paginate_through_shopify(self, url, headers):
        items = []

        while url:
            response = requests.get(url, headers=headers)
            if response.ok:
                data = response.json()
                items.extend(data[next(iter(data))])  # Extend with the first list in the response
                next_page_info = response.links.get('next', {}).get('url')
                url = next_page_info if next_page_info else None
                time.sleep(self.pagination_wait_time)
            else:
                print(f"Error during pagination: {response.text}")
                break

        return items
        
########### PAGINATED Interfaces ###############################    
    def get_all_orders(self, paginate=False, items_per_page=250):
        url = self.base_url + f'orders.json?limit={items_per_page}'
        if paginate:
            return self.paginate_through_shopify(url, self.auth_headers)
        else:
            response = requests.get(url, headers=self.auth_headers)
            return response.json()['orders'] if response.ok else None

    
    def get_all_open_orders(self, paginate=False, items_per_page=250):
        url = self.base_url + f'orders.json?fulfillment_status=unshipped&limit={items_per_page}'
        if paginate:
            return self.paginate_through_shopify(url, self.auth_headers)
        else:
            response = requests.get(url, headers=self.auth_headers)
            return response.json()['orders'] if response.ok else None
        
    def get_all_products(self, paginate=False, items_per_page=250):
        url = self.base_url + f'products.json?limit={items_per_page}'
        if paginate:
            return self.paginate_through_shopify(url, self.auth_headers)
        else:
            response = requests.get(url, headers=self.auth_headers)
            return response.json()['products'] if response.ok else None
######################################################################

########### Detail Interfaces ########################################
    def get_order_details(self, order_id):
        url = self.base_url + f'orders/{order_id}.json'
        response = requests.get(url, headers=self.auth_headers)
        if response.ok:
            return response.json()['order']
        else:
            print(f"Error getting order details: {response.text}")
            return None
        
    def get_product_details(self, product_id):
        url = self.base_url + f'products/{product_id}.json'
        response = requests.get(url, headers=self.auth_headers)
        if response.ok:
            return response.json()['product']
        else:
            print(f"Error getting product details: {response.text}")
            return None
        
    def get_product_metafields(self, product_id):
        url = self.base_url + f'products/{product_id}/metafields.json'
        response = requests.get(url, headers=self.auth_headers)
        if response.status_code == 200:
            metafields = response.json().get('metafields', [])
            return metafields
        else:
            print(response.status_code)
            print(f"Failed to retrieve metafields: {response.text}")
            return None

    def get_bin_number(self, product_id):
        metadata = self.get_product_metafields(product_id)
        for metafield in metadata:
            if metafield['key'] == 'bin_number':
                return metafield['value']
        return "(No Bin Assigned)"
    
    def get_inventory_id_by_product_id(self, product_id):
        product_json = self.get_product_details(product_id)
        inventory_id = product_json['variants'][0]['inventory_item_id']
        return inventory_id
    
    def get_location_id(self):
        url = f"{self.base_url}locations.json"
        headers = {"Content-Type": "application/json", **self.auth_headers}
        response = requests.get(url, headers=headers)
        return response.json()['locations'][0]['id']
    
    def set_inventory_by_product_id(self, product_id, available):
        location_id = self.get_location_id()
        inventory_item_id = self.get_inventory_id_by_product_id(product_id)
        url = f"{self.base_url}inventory_levels/set.json"
        payload={
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            'available': available
        }
        headers = {"Content-Type": "application/json", **self.auth_headers}
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    
    def adjust_inventory_by_product_id(self, product_id, adjustment_amount):
        url = f"{self.base_url}inventory_levels/adjust.json"
        headers = {"Content-Type": "application/json", **self.auth_headers}
        inventory_id = self.get_inventory_id_by_product_id(product_id)
        location_id = self.get_location_id()
        payload = {
            "location_id": location_id,
            "inventory_item_id": inventory_id,
            "available_adjustment": adjustment_amount
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    
    def get_inventory_by_product_id(self, product_id):
        location_id = self.get_location_id()
        inventory_item_id = self.get_inventory_id_by_product_id(product_id)
        url = f"{self.base_url}inventory_levels.json"
        params={
            "location_ids": location_id,
            "inventory_item_ids": inventory_item_id
        }
        headers = {"Content-Type": "application/json", **self.auth_headers}
        response = requests.get(url, params=params, headers=headers)
        return response.json()

    def update_product_inventory_quantity(self, product_id, new_inventory_quantity):
        url = f"{self.base_url}products/{product_id}.json"
        headers = {"Content-Type": "application/json", **self.auth_headers}

        # Get current product data
        response = requests.get(url, headers=headers)

        if response.ok:
            product_data = response.json().get("product", {})
            variant_id = product_data['variants'][0]['id']
            print(product_data)
            print(new_inventory_quantity)
            payload = {
            "variant": {
                "id": variant_id,
                "inventory_quantity": new_inventory_quantity
            }
        }


            # Send updated data
            endpoint = f"{self.base_url}variants/{variant_id}"
            response = requests.put(endpoint, json=payload, headers=headers)

            if response.ok:
                print(f"Inventory quantity updated successfully for product {product_id}")
                return

        print(f"Failed to update inventory quantity for product {product_id}: {response.text}")


######################################################################


