from ._anvil_designer import WarehouseStockModuleTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
import random
import string
import uuid
from ...CommonComponents import CommonFunctions as cf
from ...CommonComponents.SelectBinModal import SelectBinModal
from datetime import datetime
import time

class WarehouseStockModule(WarehouseStockModuleTemplate):
  def __init__(self, current_user, current_role, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.current_user = current_user
    self.current_role = current_role
    self.mode = 'verify'
    self.verify_part_btn.enabled = False
    self.place_part_card.visible=False
    self.create_item_card.visible=False
    self.purgatory_bins = anvil.server.call_s('get_bins_in_purgatory')
    self.card_4.visible=False
    self.create_item_btn_copy.enabled = False
    #If disabled, assumes that items are placed in their primary bin location upon placement scan
    self.require_bin_to_place = False #come back and edit this when looking at full functionality
    self.verify_item_id = None
    self.place_item_id = None
    
    self.disable_verify_buttons()
    self.item_code_input.focus()
    # Any code you write here will run before the form opens.


############ Helpers ###################################
  def disable_verify_buttons(self):
    self.mis_id_button.enabled = False
    self.verified_btn.enabled = False
    self.mis_id_button.tooltip = "You must scan an item first."
    self.verified_btn.tooltipe = "You must scan an item first."

  def reset_selection(self):
    self.disable_verify_buttons()
    self.product_name_output.content = None
    self.product_img.source = None
    self.sku_output.content = None
    self.bin_output.content = None
    self.type_output.content = None
    self.inventory_output.content = None
    self.os_bins_output.content = None
    self.crs_output.content = None
    self.item_code_input.text = None
    self.verify_item_id = None #reset item_id    
    self.item_code_input.enabled = True
    
############ Change View Events #############################

  def verify_part_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.verify_part_btn.enabled = False
    self.place_part_btn.enabled = True
    self.verify_part_btn.role = 'secondary-color'
    self.place_part_btn.role = 'primary-color'
    self.verify_part_card.visible = True
    self.place_part_card.visible = False
    self.create_item_btn.role = 'secondary-color'
    self.create_item_card.visible = False

  def place_part_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.verify_part_btn.enabled = True
    self.place_part_btn.enabled = False
    self.verify_part_btn.role = 'primary-color'
    self.place_part_btn.role = 'secondary-color'
    self.verify_part_card.visible = False
    self.place_part_card.visible = True
    self.create_item_btn.role = 'secondary-color'
    self.create_item_card.visible = False
    self.reset_place_part_visibility()
    # if not self.require_bin_to_place:
    #   self.bin_panel.visible = False
    # else:
    #   self.bin_code_place_input.enabled = False
    #   #TODO, add conditional to the shopify placement logic based on this setting

####### EVENTS - Verify Part ###################
  def item_code_input_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    time.sleep(1)
    self.item_code_input.enabled = False
    item_scan = json.loads(self.item_code_input.text)
    item_id = item_scan.get('item_id')
    product_sku = cf.get_sku_from_scan(item_id)
    self.verify_item_id = item_id #saving for item update calls
    product_dict = anvil.server.call('get_product_by_sku', 
                                     product_sku)
    self.product_name_output.content = product_dict['product_name']
    self.product_img.source = product_dict['img_source_url']
    self.sku_output.content = product_dict['sku']
    self.bin_output.content = product_dict['bin']
    self.type_output.content = product_dict['type']
    self.inventory_output.content = product_dict['shopify_qty']
    self.os_bins_output.content = product_dict['os_bins']
    self.crs_output.content = product_dict['cross_refs']
    self.mis_id_button.enabled = True
    self.verified_btn.enabled = True
    self.mis_id_button.tooltip = None
    self.verified_btn.tooltipe = None
    self.item_code_input.focus()

  def clear_scan_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.reset_selection()


  def mis_id_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    #This effectively renders this barcode dead. A new code will need to be printed for this item
    current_user = self.current_user
    current_time = datetime.now()
    item_status = "Misidentified"
    anvil.server.call('update_item_on_misid', 
                      self.current_user, 
                      self.current_role, 
                      self.verify_item_id) #note that this also updates history
    
    #Console log for developer
    print(f"Item {self.verify_item_id} marked as misidentified")

    #Notice for Warehouse Employee
    n = Notification(f"Item {self.verify_item_id} has been denoted as misidentified. Please set item aside for management.", 
                     style='danger', title='Part Misidentified')
    n.show()
    
    #Message for management
    message_body = f'AUTOMATED NOTICE: Part {self.verify_item_id} marked as misidentified by warehouse.'
    anvil.server.call('create_message', 
                      current_user, 
                      'Warehouse', 
                      'Management', 
                      message_body, 
                      self.verify_item_id)
    
    self.reset_selection()

  def verified_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    current_user = self.current_user
    current_time = datetime.now()
    status = anvil.server.call('update_item_on_verify', 
                      self.current_user, 
                      self.current_role, 
                      self.verify_item_id) #updates history as well

    #Console log for developer
    print(f"Item {self.verify_item_id} marked as Verified.")

    if status == 'Needs Fixed':
      n = Notification(f"Item {self.verify_item_id} Needs Fixed! Put the item on the needs fixed table", 
                     style='success', title='Needs Fixed', timeout=1)
      n.show()
    else:
    #Notice for Warehouse Employee
      n = Notification(f"Item {self.verify_item_id} verified!", 
                     style='success', title='Part Verified', timeout=1)
      n.show()
    
    product = anvil.server.call('get_product_by_sku', self.sku_output.content)
    inventory_return = anvil.server.call('adjust_inventory_by_product_id', product['product_id'], 1)
    new_inventory_count = inventory_return['inventory_level']['available']
    anvil.server.call('update_rows', 'products', 'sku', self.sku_output.content, 'shopify_qty', new_inventory_count)
    self.reset_selection()


# ######### Place Part Visibility Settings ###########
  def reset_place_part_visibility(self):
    self.other_bins_dd.items = [('(No Other Bins)', '(No Other Bins)')]
    self.other_bins_dd.selected_value = '(No Other Bins)'
    self.place_item_id = None
    self.item_code_place_input.text = None
    self.item_code_place_input.enabled = True
    self.primary_bin_output.content = None
    self.scan_item_panel.visible = True
    self.primary_bin_panel.visible = False
    self.other_bins_panel.visible = False 
    
  def primary_bin_visibility(self):
    self.scan_item_panel.visible = True
    self.primary_bin_panel.visible = True
    self.other_bins_panel.visible = False

  def other_bin_visibility(self):
    self.scan_item_panel.visible = True
    self.primary_bin_panel.visible = False
    self.other_bins_panel.visible = True
    if self.other_bins_dd.selected_value == '(Select Bin)':
      self.place_other_bin_btn.enabled = False
    else:
      self.place_other_bin_btn.enabled = True

  
# ######### Place Part Events ########################
# Helper for major update events
  def _place_item_updates(self, bin):
    print('HERE is the BIN: ', bin)
    anvil.server.call('update_item_on_binned', 
                      user=self.current_user, 
                      role=self.current_role,
                      item_id=self.place_item_id, 
                      bin=bin)
    n = Notification(f"{item_id} added to stock in bin {bin}. Inventory Updated!", style='success')
    n.show()
    #Update inventory (additive)
    #anvil.server.call('update_inv_qty_by_item', self.place_item_id)
  
  def item_code_place_input_pressed_enter(self, **event_args):
    time.sleep(1)
    self.item_code_place_input.enabled = False
    
    #get the primary bin location  & purgatory rows
    purgatory_bins = self.purgatory_bins
    item_scan = json.loads(self.item_code_place_input.text)
    self.place_item_id = item_scan.get('item_id')
    
    #maybe add validation at this row for item scans later on
    primary_bin = anvil.server.call('get_primary_bin_from_item_scan', 
                                    self.place_item_id)

    #Purgatory Handling
    if primary_bin in purgatory_bins:
      n = Notification(f"Bin {primary_bin} is in purgatory. Please place item in purgatory area.", 
                       title="Place Item In Purgatory", style='warning', timeout=10)
      n.show()
      anvil.server.call('add_item_to_purgatory', 
                        user=self.current_user, 
                        role=self.current_role,
                        bin=primary_bin,
                        item_id=self.place_item_id)
      self.reset_place_part_visibility()
      
    else:
      self.primary_bin_output.content = primary_bin
      self.primary_bin_visibility()
      self.other_bins_dd.items = anvil.server.call('get_other_bins_dd', primary_bin)
      self.other_bins_dd.selected_value = '(Select Bin)'
    
    
  def clear_place_input_btn_click(self, **event_args):  
    #get the primary bin location
    self.reset_place_part_visibility()

  def add_to_stock_primary_btn_click(self, **event_args):
    bin = self.primary_bin_output.content
    self._place_item_updates(bin)
    self.reset_place_part_visibility()

  def place_other_bin_btn_click(self, **event_args):
    bin = self.other_bins_dd.selected_value
    self._place_item_updates(bin)
    self.reset_place_part_visibility()

  def on_other_bin_dd_change(self, **event_args):
    if self.other_bins_dd.selected_value == '(Select Bin)':
      self.place_other_bin_btn.enabled = False
    else:
      self.place_other_bin_btn.enabled = True

  def other_bins_btn_click(self, **event_args):
    self.other_bin_visibility()
      
  def back_to_primary_btn_click(self, **event_args):
    self.primary_bin_visibility()

  def new_bin_btn_click(self, **event_args):
    #Can put an admin code here too if needed
    primary_bin = self.primary_bin_output.content
    selected_bin = anvil.alert(SelectBinModal(primary_bin=primary_bin, mode='open_bins'), 
                               large=True, 
                               buttons=[])
    if selected_bin:
      part_number = self.place_item_id.split('__')[0]
      anvil.server.call('add_new_bin_for_item', 
                        self.place_item_id, 
                        selected_bin)
      n = Notification(f"New OS Bin for part number: {part_number}!",
                       style='Success', timeout=4, title='New OS Bin Activated')
      n.show()
      self.reset_place_part_visibility()


  def purg_primary_bin_btn_click(self, **event_args):
    primary_bin = self.primary_bin_output.content
    confirm = anvil.alert(f"Confirm add bin {primary_bin} to Purgatory?", 
                          title=f"Add {primary_bin} to Purgatory?", 
                          large=True, buttons=['SEND TO PURGATORY', 'CANCEL'])
    if confirm == 'SEND TO PURGATORY':
      n = Notification('Sending Bin and Item to Purgatory, just a moment...', 
                       title=f'Sending {primary_bin} to Purgatory', 
                       style='warning',
                       timeout=4)
      n.show()
      anvil.server.call('add_bin_to_purgatory', 
                        user=self.current_user, 
                        role=self.current_role, 
                        bin=primary_bin, 
                        item_id=self.place_item_id)
      self.purgatory_bins = anvil.server.call('get_bins_in_purgatory')
      n_2 = Notification('Bin added to purgatory!', style='success')
      n_2.show()
      self.reset_place_part_visibility()

  def pick_mode_button_click(self, **event_args):
      """This method is called when the button is clicked"""
      from ..WarehousePickModule import WarehousePickModule
        
      get_open_form().content_panel.clear()
      get_open_form().content_panel.add_component(WarehousePickModule(current_user=self.current_user, current_role=self.current_role),
                                        full_width_row=True)

  def create_item_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.verify_part_btn.enabled = True
    self.place_part_btn.enabled = True
    self.verify_part_btn.role = 'secondary-color'
    self.place_part_btn.role = 'secondary-color'
    self.create_item_btn.role = 'primary-color'
    self.verify_part_card.visible = False
    self.place_part_card.visible = False
    self.create_item_card.visible = True
    pass

  def product_code_input_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    self.product_code_input.enabled = False
    product_scan = json.loads(self.product_code_input.text)
    product_dict = anvil.server.call('get_product_by_sku', 
                                     product_scan['sku'])
    self.product_name_output_copy.content = product_dict['product_name']
    self.product_img_copy.source = product_dict['img_source_url']
    self.sku_output_copy.content = product_dict['sku']
    self.bin_output_copy.content = product_dict['bin']
    self.type_output_copy.content = product_dict['type']
    self.inventory_output_copy.content = product_dict['shopify_qty']
    self.os_bins_output_copy.content = product_dict['os_bins']
    self.crs_output_copy.content = product_dict['cross_refs']

    self.create_item_btn_copy.enabled = True
    self.create_item_btn_copy.tooltipe = None
    self.product_code_input.focus()


  def generate_unique_item_id(self, sku, len=6):
      chars = string.ascii_letters + string.digits
      code = ''.join(random.choice(chars) for _ in range(len))
      return sku + "__" + code

  def create_item_btn_copy_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.create_item_btn_copy.enabled = False
    current_time = datetime.now()
    date_1900 = datetime(1900, 1, 1) 
    date_1900_with_timezone =  date_1900
    product_scan = json.loads(self.product_code_input.text)
    selected_product = anvil.server.call('get_product_by_sku', 
                                     product_scan['sku'])
    item_info_dict = {
      'product_name': selected_product['product_name'],
      'item_id': self.generate_unique_item_id(product_scan['sku']),
      'sku': product_scan['sku'],
      'img_source': selected_product['img_source_url'],
      'primary_bin': selected_product['bin'],
      'stored_bin': '',
      'status': "New",
      'os_bins': selected_product['os_bins'],
      'cross_refs': selected_product['cross_refs'],
      #Set all other information for item DB entry
      'supplier': '',
      'truck':'',
      'box_id':'',
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
      'sale_price': selected_product['price']
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
    self.card_4.visible=True
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
    n = Notification("Item Created!", style='success', timeout=1)
    n.show()

  def print_barcode_click(self, **event_args):
    print("Image URL:", self.qr_img_url)
    js.call('printPage', self.qr_img_url)



  def clear_scan_btn_copy_click(self, **event_args):
    self.product_code_input.enabled = True
    self.product_code_input.text = None
    self.product_name_output_copy.content = None
    self.product_img_copy.source = None
    self.sku_output_copy.content = None
    self.bin_output_copy.content = None
    self.type_output_copy.content = None
    self.inventory_output_copy.content = None
    self.os_bins_output_copy.content = None
    self.crs_output_copy.content = None
    self.card_4.visible = False
    self.create_item_btn_copy.enabled = False


    
      




    