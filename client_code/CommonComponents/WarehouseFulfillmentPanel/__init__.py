from ._anvil_designer import WarehouseFulfillmentPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class WarehouseFulfillmentPanel(WarehouseFulfillmentPanelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.switch_to_empty_view()
    self.product_dict = anvil.server.call('get_product_dict_by_name', 
                                          self.item['product_name'])
    self.link_base_content()
    # Any code you write here will run before the form opens.

##### Visibility ###################################  
  def switch_to_empty_view(self):
    self.item_id_panel.visible = False
    self.clear_item_btn.visible = False
    self.needs_attention_btn.visible = False
    self.item_scan_panel.visible = True
    self.no_stock_btn.visible = True

  def switch_to_scanned_view(self):
    self.item_id_panel.visible = True
    self.clear_item_btn.visible = True
    self.needs_attention_btn.visible = True
    self.item_scan_panel.visible = False
    self.no_stock_btn.visible = False

######### Link UI to object content ####################
  def link_base_content(self):
    self.bin_content.content = self.product_dict['bin']
    self.name_content.content = self.product_dict['product_name']
    self.sku_output.content = self.product_dict['sku']
    self.os_bin_output.content = self.product_dict['os_bins']
    self.crs_output.content = self.product_dict['cross_refs'] 