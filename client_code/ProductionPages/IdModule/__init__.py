from ._anvil_designer import IdModuleTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import js
import anvil.media

from ...CommonComponents.ProductExplorer import ProductExplorer
from ...CommonComponents import CommonFunctions as cf

import datetime
import time
import json
import random
import string
import uuid

class IdModule(IdModuleTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.make_dropdown.items = anvil.server.call('get_make_dropdown')
    self.year_dropdown.items = anvil.server.call('get_year_dropdown')
    self.size_dropdown.items = anvil.server.call('get_size_dropdown')
    self.selected_product = None


######## Helpers ######################################
  def generate_unique_item_id(self, sku, len=6):
    chars = string.ascii_letters + string.digits
    code = ''.join(random.choice(chars) for _ in range(len))
    return sku + "__" + code

  def generate_unique_box_id(self, len=6):
    pass



######### COMPONENT EVENTS ############################
  def on_truck_code_enter(self, **event_args):
    truck_code = self.truck_code_input.text
    supplier, truck = anvil.server.call('get_supplier_truck_from_code', truck_code)
    self.supplier_scan_output.content = supplier
    self.truck_scan_output.content = truck
    self.truck_code_input.enabled = False

  def lock_box_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.make_dropdown.enabled = False
    self.model_input_bx.enabled = False
    self.year_dropdown.enabled = False
    self.size_dropdown.enabled = False
    self.box_id = str(uuid.uuid4()) #Maye make this a datetime + serial

  def reset_bx_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.truck_code_input.text = None
    self.truck_code_input.enabled = True
    self.supplier_scan_output.content = None
    self.truck_scan_output.content = None
    self.make_dropdown.enabled = True
    self.make_dropdown.selected_value = None
    self.model_input_bx.text = None
    self.model_input_bx.enabled = True
    self.year_dropdown.enabled = True
    self.year_dropdown.selected_value = None
    self.size_dropdown.enabled = True
    self.size_dropdown.selected_value = None

  def launch_pdt_explr_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    product_explorer = ProductExplorer()
    self.selected_product = alert(product_explorer, 
                            title="Select Product", 
                            large=True)
    self.selected_product_display.text = self.selected_product['sku']

  def create_item_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.create_item_btn.enabled = False
    current_time = datetime.datetime.now()

    item_info_dict = {
      'product_name': self.selected_product['product_name'],
      'item_id': self.generate_unique_item_id(self.selected_product_display.text),
      'sku': self.selected_product_display.text,
      'img_source': self.selected_product['img_source_url'],
      'primary_bin': self.selected_product['bin'],
      'stored_bin': 'price',
      'status': "New",
      'location': 'Id Table',
      'os_bins': self.selected_product['os_bins'],
      'cross_refs': self.selected_product['cross_refs'],
      #Set all other information for item DB entry
      'supplier': self.supplier_scan_output.content,
      'truck': self.truck_scan_output.content,
      'box_id': self.box_id,
      'make': self.make_dropdown.selected_value,
      'model': self.model_input_bx.text,
      'year': self.year_dropdown.selected_value,
      'size': self.size_dropdown.selected_value,
      'identified_on': current_time,
      'identified_by': anvil.server.call('get_user_full_name'),
      'verified_by': '',
      'verified_on': datetime.datetime(1900, 1, 1), #placeholder date
      'binned_by': '',
      'binned_on': datetime.datetime(1900, 1, 1),
      'picked_by': '',
      'picked_on': datetime.datetime(1900, 1, 1),
      'tested_by': '',
      'tested_on': datetime.datetime(1900, 1, 1),
      'packed_by': '',
      'packed_on': datetime.datetime(1900, 1, 1),
      'order_id': '',
      's3_object_key': '',
      'history': '',
      'sale_price': self.selected_product['']
    }

    #Create the qr_code with only important information
    item_id = item_info_dict['item_id']
    bin = item_info_dict['bin']
    os_bins = item_info_dict['os_bins']
    cross_refs = item_info_dict['cross_refs']
    item_status = 'New'
    
    #Image Url directly from qr maker.
    raw_source_url = anvil.server.call('generate_qr_code', 
                                      item_id=item_id, 
                                      bin=bin, 
                                      os_bins=os_bins,
                                      cross_refs=cross_refs)
    self.qr_image.source = raw_source_url
    self.system_id_display.text = item_id

    #Add the item to the datatable
    anvil.server.call('process_new_item', 
                      item_info_dict, 
                      raw_source_url)

    #Update history
    history_update_task = cf.add_event_to_item_history(item_id, item_status)

    self.create_item_btn.enabled = True
    
    

