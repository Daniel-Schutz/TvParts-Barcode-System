import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

import os
import json
import pandas as pd
import boto3
import requests
import time
from decimal import Decimal

class ShopifyInterface:
    
    def __init__(self):
        self.shop_url = 'tvpartstoday.com'
        self.access_key = shopify_admin_key
        self.api_version = '2023-10'
        self.base_url = f"https://{self.shop_url}/admin/api/{self.api_version}/"
        self.auth_headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_key
        }
        self.pagination_wait_time = 0.33 #Prevent rate limiting

        
########### Pagination Helper function ########################
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
######################################################################

