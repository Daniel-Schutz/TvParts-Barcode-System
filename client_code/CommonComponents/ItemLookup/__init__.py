from ._anvil_designer import ItemLookupTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

import json
from ..SingleProductListing import SingleProductListing

class ItemLookup(ItemLookupTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

########## Helpers ###################################
  def display_all_values(self, this_item):
    self.product_name_output.content = this_item['product_name']
    self.img_output.source = this_item['img_source']
    self.item_id_output.content = this_item['item_id']
    self.stored_bin_output.content = this_item['stored_bin']
    self.lifecycle_status_output.content = this_item['lifecycle_status']
    self.testing_status_output.content = this_item['testing_status']
    self.order_output.content = this_item['order_id']
    self.supplier_output.content = this_item['supplier']
    self.truck_output.content = this_item['truck']
    self.make_output.content = this_item['make']
    self.year_output.content = this_item['year']
    self.size_output.content = this_item['size']
    self.created_on_output.content = this_item['created_date']
    self.created_by_output.content = this_item['created_by']
    self.verified_on_output.content = this_item['verified_date']
    self.verified_by_output.content = this_item['verified_by']
    self.picked_on_output.content = this_item['picked_date']
    self.picked_by_output.content = this_item['picked_by']
    self.tested_on_output.content = this_item['tested_date']
    self.tested_by_output.content = this_item['tested_by']
    self.packed_on_output.content = this_item['packed_date']
    self.tested_by_output.content = this_item['packed_by']

  def clear_all_values(self):
    self.product_name_output.content = None
    self.item_id_output.content = None
    self.img_output.source = None
    self.stored_bin_output.content = None
    self.lifecycle_status_output.content = None
    self.testing_status_output.content = None
    self.order_output.content = None
    self.supplier_output.content = None
    self.truck_output.content = None
    self.make_output.content = None
    self.year_output.content = None
    self.size_output.content = None
    self.created_on_output.content = None
    self.created_by_output.content = None
    self.verified_on_output.content = None
    self.verified_by_output.content = None
    self.picked_on_output.content = None
    self.picked_by_output.content = None
    self.tested_on_output.content = None
    self.tested_by_output.content = None
    self.packed_on_output.content = None
    self.tested_by_output.content = None

  

########### EVENTS ###################################
  def scanned_item_input_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    self.lookup_by_id_input.enabled = False
    self.scanned_item_input.enabled = False
    input_dict = json.loads(self.scanned_item_input.text)
    item_id = input_dict['item_id']
    self.scanned_item_input.text = item_id
    item_dict = anvil.server.call('get_row_from_dynamo', 
                                  'unique_item', 
                                  item_id)
    self.display_all_values(item_dict)

  def id_lookup_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.lookup_by_id_input.enabled = False
    self.scanned_item_input.enabled = False
    item_id = self.lookup_by_id_input.text
    item_dict = anvil.server.call('get_row_from_dynamo', 
                                  'unique_item', 
                                  item_id)
    if not item_dict:
      anvil.alert("Item id does not exists. Please check and try again")
    else:
      self.display_all_values(item_dict)

  def reset_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.lookup_by_id_input.enabled = True
    self.scanned_item_input.enabled = True
    self.clear_all_values()

  def view_product_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    product_sku = self.item_id_output.content.split("__")[0] #assumes __ as id separator
    product_dict = anvil.server.call('get_product_by_sku')

    #Need to reform single product modal for this to work - see gpt
    single_product_modal = SingleProductListing(item=product_dict)
