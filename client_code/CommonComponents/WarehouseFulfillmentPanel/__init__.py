from ._anvil_designer import WarehouseFulfillmentPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

import json
from .. import CommonFunctions as cf

class WarehouseFulfillmentPanel(WarehouseFulfillmentPanelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.current_user = anvil.server.call_s('get_user_full_name')
    self.current_role = anvil.server.call_s('get_user_role')
    if self.item['status'] == 'New':
      self.switch_to_empty_view()
    else:
      self.switch_to_scanned_view()
    self.product_dict = anvil.server.call('get_product_row_by_sku', 
                                  self.item['sku'])
    self.link_base_content()

##### Visibility ###################################  
  def switch_to_empty_view(self):
    self.picked_indicator.visible = False
    self.item_id_panel.visible = False
    self.clear_item_btn.visible = False
    self.needs_attention_btn.visible = False
    self.item_scan_panel.visible = True
    self.no_stock_btn.visible = True
    self.bin_panel.visible = True
    self.name_panel.visible = True
    self.master_flow_card.background = '#ffffff'
    self.product_img_output.visible = True
    self.os_crs_panel.visible = True
    # self.item_scan_input.focus()

  def switch_to_scanned_view(self):
    self.picked_indicator.visible = True
    self.item_id_panel.visible = True
    self.clear_item_btn.visible = True
    self.needs_attention_btn.visible = True
    self.item_scan_panel.visible = False
    self.no_stock_btn.visible = False
    self.bin_panel.visible = False
    self.name_panel.visible = False
    self.product_img_output.visible = False
    self.os_crs_panel.visible = False
    self.master_flow_card.background = '#96ff96'
    

######### Link UI to object content ####################
  def link_base_content(self):
    self.bin_content.content = self.product_dict['bin']
    self.name_content.content = self.product_dict['product_name']
    self.sku_output.content = self.product_dict['sku']
    self.os_bin_output.content = self.product_dict['os_bins']
    self.crs_output.content = self.product_dict['cross_refs']
    self.product_img_output.source = self.product_dict['img_source_url']


######### EVENTS ####################################
  def item_scan_pressed_enter(self, **event_args):
    item_id = json.loads(self.item_scan_input.text)['item_id']
    item_sku = item_id.split("__")[0]
    if item_sku != self.sku_output.content:
      confirm = anvil.alert(f"WARNING: Scanned sku does not match order sku. Ok to proceed?", 
                  title='SKU Mismatch Notice', buttons=['LINK ITEM', 'CANCEL'], large=True)
      if confirm != 'LINK ITEM':
        self.item_scan_input.text = None
        return
    self.item_id_output.content = item_id
    fulfillment_id = self.item['fulfillment_id']
    anvil.server.call_s('link_item_to_fulfillment', 
                      fulfillment_id,
                      item_id, 
                        self.current_user, 
                        self.current_role)
    #cf.add_event_to_item_history(item_id, 'Picked', self.current_user, self.current_role)
    self.switch_to_scanned_view()
    self.parent.raise_event('x-change-focus-to-next', sku=self.sku_output.content)

  def clear_item_btn_click(self, **event_args):
    self.item_scan_input = self.name_content
    self.switch_to_empty_view()

  def no_stock_btn_click(self, **event_args):
    self.parent.raise_event('x-wh-no-stock', 
                            sku=self.sku_output.content, 
                            fulfillment_id = self.item['fulfillment_id'])
    print("raised event in no stock")
    #Note - we take care of datatable manipulation at the order level. Subs just throw events.

  def needs_attention_btn_click(self, **event_args):
    self.parent.raise_event('x-wh-needs-attention', 
                            sku=self.sku_output.content, 
                            fulfillment_id = self.item['fulfillment_id'])