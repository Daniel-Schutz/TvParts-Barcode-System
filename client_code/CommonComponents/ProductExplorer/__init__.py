from ._anvil_designer import ProductExplorerTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

import math

class ProductExplorer(ProductExplorerTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.type_dropdown.items = anvil.server.call('get_type_dropdown')
    self.type_dropdown.selected_value = 'All Types'
    self.repeating_panel_1.set_event_handler('x-product-selected', self.select_product)
    self.page_size = 5
    self.current_page = 0
    self.max_pages = 0 #initialize
    self.ttl_pg_lbl.text = 0
    self.page_num_lbl.text = 0
    self.matching_products = [] #placeholder for return
    #self.load_page_data()
    #self.temp_items_from_db()

    # Any code you write here will run before the form opens.

  def search_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    product_name = self.product_name_txbx.text
    if self.name_contains_radio.selected:
      product_name_search_type = self.name_contains_radio.value #which is "Contains"
    elif self.name_exact_radio.selected:
      product_name_search_type = self.name_exact_radio.value #which is "Contains"
    
    sku = self.product_sku_txbx.text
    if self.sku_contains_radio.selected:
      sku_search_type = self.sku_contains_radio.value
    elif self.sku_exact_radio.selected:
      sku_search_type = self.sku_exact_radio.value


    if self.type_dropdown.selected_value:
      type = self.type_dropdown.selected_value
    else:
      type = None

    matching_products = anvil.server.call('run_product_explorer_query', 
                                          product_name, 
                                          product_name_search_type, 
                                          sku, 
                                          sku_search_type, 
                                          type)
    self.num_results_display.text = len(matching_products)
    self.matching_products = matching_products

    #Pagination variables
    self.max_pages = math.ceil(len(self.matching_products)/self.page_size)
    self.ttl_pg_lbl.text = self.max_pages
    self.load_page_data()

  def reset_search(self, **event_args):
    self.name_contains_radio.selected = True
    self.sku_contains_radio.selected = True
    self.type_dropdown.selected_value = 'All Types'
    self.product_name_txbx.text = None
    self.product_sku_txbx.text = None
    self.num_results_display.text = None


############# EVENTS #######################################  
  def main_submit_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  #helper for designing the repeater and pagination system
  def temp_items_from_db(self):
    self.repeating_panel_1.items = anvil.server.call('test_product_call')

############### Pagination ##################################
  def load_page_data(self):
    start_index = self.current_page * self.page_size
    end_index = start_index + self.page_size
    # Load data for the current page
    return_data = []
    for i, row in enumerate(self.matching_products):
      if i < start_index:
        pass
      elif i >= start_index and i < end_index:
        return_data.append(row)
      else:
        break
        
    self.repeating_panel_1.items = return_data
    #self.repeater_1.items = self.data_for_repeater

  def page_back_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.current_page <= 0:
      pass
    else:
      self.current_page -= 1
      self.page_num_lbl.text = self.current_page
      self.load_page_data()

  def page_next_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.current_page >= self.max_pages:
      pass
    else:
      self.current_page += 1
      self.page_num_lbl.text = self.current_page
      self.load_page_data()

######## Handle Product Selection ###################
  def select_product(self, product, **event_args):
    print("triggered the event")
    self.selected_sku.text = product['sku']
    #raising close alert event for modal operations
    self.raise_event('x-close-alert', value=product)