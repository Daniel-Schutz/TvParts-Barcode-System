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
from ...CommonComponents.RecallItemModal import RecallItemModal

import datetime
import time
import json
import random
import string
import uuid

class IdModule(IdModuleTemplate):
  def __init__(self, current_user, current_role, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.current_user = current_user
    self.current_role = current_role
    self.make_dropdown.items = anvil.server.call('get_make_dropdown')
    self.make_dropdown.selected_value = '(Select Make)'
    self.year_dropdown.items = anvil.server.call('get_year_dropdown')
    self.year_dropdown.selected_value = '(Select Year)'
    self.size_dropdown.items = anvil.server.call('get_size_dropdown')
    self.size_dropdown.selected_value = '(Select Size)'
    self.needs_fixed_skus = anvil.server.call('get_auto_fixes_by_sku')
    self.launch_pdt_explr_btn.enabled = False
    self.create_item_btn.enabled = False
    self.update_holding_area_count()
    self.selected_product = None
    self.id_hold_count_output.content = anvil.server.call('get_id_holding_count')
    self.nf_label_panel.visible = False
    self.nf = False
    self.box_id = None
    self.qr_img_url = None


######## Helpers ######################################
  def generate_unique_item_id(self, sku, len=6):
    chars = string.ascii_letters + string.digits
    code = ''.join(random.choice(chars) for _ in range(len))
    return sku + "__" + code

  def generate_unique_box_id(self, len=4):
    import pytz
    chars = string.ascii_letters + string.digits
    code = ''.join(random.choice(chars) for _ in range(len))
    current_time = datetime.datetime.now()
    desired_timezone = pytz.timezone('US/Central')  # Fuso horário central dos EUA
    current_time = current_time.astimezone(desired_timezone)
    today = current_time.strftime('%m-%d-%Y')
    return today + "__" + code

  def check_nf_list(self):
    needs_fixed_skus = self.needs_fixed_skus
    if self.selected_product['sku'] in needs_fixed_skus:
      self.nf_label_panel.visible = True
      return True
    else:
      self.nf_label_panel.visible = False
      return False



######### COMPONENT EVENTS ############################
  def on_truck_code_enter(self, **event_args):
    truck_code = self.truck_code_input.text
    supplier, truck = anvil.server.call('get_supplier_truck_from_code', truck_code)
    self.supplier_scan_output.content = supplier
    self.truck_scan_output.content = truck
    self.truck_code_input.enabled = False

  def box_defined(self):
    if not self.truck_code_input.text:
      return False
    elif not self.supplier_scan_output.content:
      return False
    elif not self.truck_code_input.text:
      return False
    elif self.make_dropdown.selected_value == '(Select Make)':
      return False
    elif not self.model_input_bx.text:
      return False
    elif self.year_dropdown.selected_value == '(Select Year)':
      return False
    elif self.size_dropdown.selected_value == '(Select Size)':
      return False
    else:
      return True

  def lock_box_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.box_defined():
      self.make_dropdown.enabled = False
      self.model_input_bx.enabled = False
      self.year_dropdown.enabled = False
      self.size_dropdown.enabled = False
      if not self.box_id:
        self.box_id = self.generate_unique_box_id() #make this its own table
      self.launch_pdt_explr_btn.enabled = True
    else:
      anvil.alert('All Truck and TV fields must be filled out before generating labels.', 
                  buttons=['CLOSE'], title="All Fields Required.")

  def reset_bx_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.truck_code_input.text = None
    self.truck_code_input.enabled = True
    self.supplier_scan_output.content = None
    self.truck_scan_output.content = None
    self.make_dropdown.enabled = True
    self.make_dropdown.selected_value = '(Select Make)'
    self.model_input_bx.text = None
    self.model_input_bx.enabled = True
    self.year_dropdown.enabled = True
    self.year_dropdown.selected_value = '(Select Year)'
    self.size_dropdown.enabled = True
    self.size_dropdown.selected_value = '(Select Size)'
    self.box_id = None

  def recall_box_btn_click(self, **event_args):
    item_id = anvil.alert(RecallItemModal(), 
                          dismissible=False, 
                          large=True, buttons=[])
    if item_id:
      if type(item_id) != bool:
        item_dict = anvil.server.call('get_item_row_by_item_id', item_id)
        self.truck_code_input.text = "(Retrieved from Recall)"
        self.truck_code_input.enabled = False
        self.supplier_scan_output.content = item_dict['supplier']
        self.truck_scan_output.content = item_dict['truck']
        self.make_dropdown.selected_value = item_dict['make']
        self.model_input_bx.text = item_dict['model']
        self.year_dropdown.selected_value = item_dict['year']
        self.size_dropdown.selected_value = item_dict['size']
        self.box_id = item_dict['box_id']
        self.lock_box_btn_click()

  def launch_pdt_explr_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.qr_image.source = None
    self.selected_product_display.text = None
    product_explorer = ProductExplorer()
    self.selected_product = alert(product_explorer, 
                            title="Select Product", 
                            large=True)
    if not self.selected_product:
      self.create_item_btn.enabled = False
      self.create_barcode_button.enabled = False
    else:
      self.selected_product_display.text = self.selected_product['sku']
      self.create_item_btn.enabled = True
      self.create_barcode_button.enabled = True
      self.nf = self.check_nf_list()
      
      

  
  def create_item_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    import pytz
    self.create_item_btn.enabled = False
    current_time = datetime.datetime.now()
    desired_timezone = pytz.timezone('US/Central') 
    current_time = current_time.astimezone(desired_timezone)
  
    date_1900 = datetime.datetime(1900, 1, 1) 
    date_1900_with_timezone = desired_timezone.localize(date_1900)

    item_info_dict = {
      'product_name': self.selected_product['product_name'],
      'item_id': self.generate_unique_item_id(self.selected_product_display.text),
      'sku': self.selected_product_display.text,
      'img_source': self.selected_product['img_source_url'],
      'primary_bin': self.selected_product['bin'],
      'stored_bin': '',
      'status': "New",
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
      'identified_by': self.current_user,
      'verified_by': '',
      'verified_on': date_1900_with_timezone, #placeholder date
      'binned_by': '',
      'binned_on': date_1900_with_timezone,
      'picked_by': '',
      'picked_on': date_1900_with_timezone,
      'tested_by': '',
      'tested_on': date_1900_with_timezone,
      'packed_by': '',
      'packed_on': date_1900_with_timezone,
      'order_no': '',
      's3_object_key': '',
      'history': '',
      'sale_price': self.selected_product['price']
    }

    #Create the qr_code with only important information
    item_id = item_info_dict['item_id']
    bin = item_info_dict['primary_bin']
    os_bins = item_info_dict['os_bins']
    cross_refs = item_info_dict['cross_refs']
    item_status = 'New'
    
    #Image Url directly from qr maker.
    raw_source_url = anvil.server.call('generate_qr_code', 
                                      item_id=item_id)
    self.qr_img_url = raw_source_url
    self.qr_image.source = raw_source_url
    self.system_id_display.text = item_id

    #Add the item to the datatable
    anvil.server.call('process_new_item', 
                      item_info_dict, 
                      raw_source_url)

    #Update history
    history_update_task = cf.add_event_to_item_history(item_id, 
                                                       item_status, 
                                                       self.current_user, 
                                                       self.current_role)

    self.create_item_btn.enabled = True
    if self.nf:
      anvil.alert("""Item must be fixed before stocking. 
      Please label this item, then move it to the Needs Fixed Area""", buttons=['OK'], 
                  title= 'Item Needs Fixed Before Stocking!')
      #set item to Needs fixed
      anvil.server.call_s('set_item_to_needs_fixed', item_id)
      
      #Update history
      history_update_task = cf.add_event_to_item_history(item_id, 
                                                        'Needs Fixed', 
                                                        'ItemFixBySku', 
                                                        'SYSTEM BOT')
      self.nf = False
    else:
      n = Notification("Item Created!", style='success', timeout=1)
      n.show()


  def create_item_btn_copy_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.create_item_btn.enabled = False
    current_time = datetime.datetime.now()
  
    date_1900 = datetime.datetime(1900, 1, 1) 
    date_1900_with_timezone = date_1900 

    item_info_dict = {
      'item_id': self.generate_unique_item_id(self.model_input_bx_copy.text),
      'sku':self.model_input_bx_copy.text,
      'img_source': '',
      'primary_bin': '',
      'stored_bin': '',
      'status': "New",
      'os_bins':'',
      'cross_refs': '',
      #Set all other information for item DB entry
      'supplier': '',
      'truck': '',
      'box_id': '',
      'make': '',
      'model': '',
      'year': None,
      'size': '',
      'identified_on': current_time,
      'identified_by': self.current_user,
      'verified_by': '',
      'verified_on': date_1900_with_timezone, #placeholder date
      'binned_by': '',
      'binned_on': date_1900_with_timezone,
      'picked_by': '',
      'picked_on': date_1900_with_timezone,
      'tested_by': '',
      'tested_on': date_1900_with_timezone,
      'packed_by': '',
      'packed_on': date_1900_with_timezone,
      'order_no': '',
      's3_object_key': '',
      'history': '',
      'sale_price': None
    }

    #Create the qr_code with only important information
    item_id = item_info_dict['item_id']
    item_status = 'New'
    
    #Image Url directly from qr maker.
    raw_source_url = anvil.server.call('generate_qr_code', 
                                      item_id=item_id)
    self.qr_img_url = raw_source_url
    self.qr_image.source = raw_source_url
    self.system_id_display.text = item_id

    #Add the item to the datatable
    anvil.server.call('process_new_item', 
                      item_info_dict, 
                      raw_source_url)

    #Update history
    history_update_task = cf.add_event_to_item_history(item_id, 
                                                       item_status, 
                                                       self.current_user, 
                                                       self.current_role)

    self.create_item_btn.enabled = True
    if self.nf:
      anvil.alert("""Item must be fixed before stocking. 
      Please label this item, then move it to the Needs Fixed Area""", buttons=['OK'], 
                  title= 'Item Needs Fixed Before Stocking!')
      #set item to Needs fixed
      anvil.server.call_s('set_item_to_needs_fixed', item_id)
      
      #Update history
      history_update_task = cf.add_event_to_item_history(item_id, 
                                                        'Needs Fixed', 
                                                        'ItemFixBySku', 
                                                        'SYSTEM BOT')
      self.nf = False
    else:
      n = Notification("Item Created!", style='success', timeout=1)
      n.show()

    self.create_barcode_button.enabled = True
      

  def print_barcode_click(self, **event_args):
    print("Image URL:", self.qr_img_url)
    js.call('printPage', self.qr_img_url)
    


##### Holding Area Logic (and events) #############
  def update_holding_area_count(self):
    hold_area_count = anvil.server.call_s('get_id_holding_count')
    self.id_hold_count_output.content = hold_area_count
    
  def move_item_to_holding_btn_click(self, **event_args):
    confirm = anvil.alert("Add Item to Holding area? Note that this is only for unlabeled parts. Leave held parts in their original box",
                         title="Pre-Id Holding?", large=True,
                         buttons=["MOVE TO HOLDING", 'CANCEL'])
    if confirm == 'MOVE TO HOLDING':
      set_num = int(self.id_hold_count_output.content) + 1
      anvil.server.call('set_id_holding_count', 
                        count=set_num)
      n = Notification(f'Id holding count has been set to {set_num}', 
                  title='Holding Count Updated!', 
                  style='success', timeout=2)
      n.show()
      self.qr_image.source = None
      self.update_holding_area_count()

