from ._anvil_designer import ProductExplorerTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ProductExplorer(ProductExplorerTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

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

    if self.vendor_dropdown.selected_value:
      vendor = self.vendor_dropdown.selected_value
    else:
      vendor = None

    if self.type_dropdown.selected_value:
      type = self.type_dropdown.selected_value
    else:
      type = None

    matching_products = anvil.server.call('run_product_explorer_query', 
                                          product_name, 
                                          product_name_search_type, 
                                          sku, 
                                          sku_search_type, 
                                          vendor, 
                                          type)
    self.num_results_display.text = len(matching_products)

  def reset_search(self):
    new_form = self.__class__()
    open_form(new_form)
