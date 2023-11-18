from ._anvil_designer import WarehouseStockModuleTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...CommonComponents import CommonFunctions as cf
from datetime import datetime

class WarehouseStockModule(WarehouseStockModuleTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.mode = 'verify'
    self.verify_part_btn.enabled = False
    self.place_part_card.visible=False
    admin_settings = anvil.server.call('get_admin_settings')
    self.item_id = None #setting as property not saved on screen

    #If disabled, assumes that items are placed in their primary bin location upon placement scan
    self.require_bin_to_place = admin_settings['require_bin_verify']
    
    self.disable_verify_buttons()
    # Any code you write here will run before the form opens.


############ Helpers ###################################
  def disable_verify_buttons(self):
    self.mis_id_button.enabled = False
    self.verified_btn.enabled = False
    self.mis_id_button.tooltip = "You must scan an item first."
    self.verified_btn.tooltipe = "You must scan an item first."

  def reset_selection(self):
    self.disale_verify_button()
    self.product_name_output.content = None
    self.product_img.source = None
    self.sku_output.content = None
    self.bin_output.content = None
    self.type_output.content = None
    self.inventory_output.content = None
    self.os_bins_output.content = None
    self.crs_output.content = None
    self.item_code_input.text = None
    self.item_id = None #reset item_id    
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

  def place_part_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.verify_part_btn.enabled = True
    self.place_part_btn.enabled = False
    self.verify_part_btn.role = 'primary-color'
    self.place_part_btn.role = 'secondary-color'
    self.verify_part_card.visible = False
    self.place_part_card.visible = True
    if not self.require_bin_to_place:
      self.bin_panel.visible = False
      #TODO, add conditional to the shopify placement logic based on this setting

####### EVENTS - Verify Part ###################
  def item_code_input_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    self.item_code_input.enabled = False
    product_sku = cf.get_id_from_scan(self.item_code_input.text)
    item_id = cf.get_id_from_scan(self.item_code_input.text, mode='item')
    self.item_id = item_id #saving for item update calls
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

  def clear_scan_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.reset_selection()


  def mis_id_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    #This effectively renders this barcode dead. A new code will need to be printed for this item
    current_user = anvil.server.call('get_user_full_name')
    current_time = datetime.now()
    update_lifecycle_status = anvil.server.call('update_item', 
                                                self.item_id, 
                                                'lifecycle_status', 
                                                'Misidentified')
    update_verfied_by = anvil.server.call('update_item', 
                                          self.item_id, 
                                          'verified_by', 
                                          current_user)
    update_verfied_date = anvil.server.call('update_item', 
                                          self.item_id, 
                                          'verified_date', 
                                          current_time)
    
    #Console log for developer
    print(f"Item {self.item_id} marked as misidentified")

    #Notice for Warehouse Employee
    n = Notification(f"Item {self.item_id} has been denoted as misidentified. Please set item aside for management.", 
                     style='danger', title='Part Misidentified')
    n.show()
    
    #Message for management
    message_body = f'AUTOMATED NOTICE: Part {self.item_id} marked as misidentified by warehouse.'
    anvil.server.call('create_message', 
                      current_user, 
                      'Warehouse', 
                      'Management', 
                      message_body, 
                      self.item_id)
    
    self.reset_selection()

  def verified_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    current_user = anvil.server.call('get_user_full_name')
    current_time = datetime.now()
    update_lifecycle_status = anvil.server.call('update_item', 
                                                self.item_id, 
                                                'lifecycle_status', 
                                                'Misidentified')
    update_verfied_by = anvil.server.call('update_item', 
                                          self.item_id, 
                                          'verified_by', 
                                          current_user)
    update_verfied_date = anvil.server.call('update_item', 
                                          self.item_id, 
                                          'verified_date', 
                                          current_time)
    

########## Place Part Events ########################


    
    
    
