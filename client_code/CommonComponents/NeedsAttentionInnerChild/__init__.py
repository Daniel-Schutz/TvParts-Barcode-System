from ._anvil_designer import NeedsAttentionInnerChildTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class NeedsAttentionInnerChild(NeedsAttentionInnerChildTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.sku_output.content = self.item['sku']
    self.product_name_output.content = self.item['product_name']
    self.linked_item_id_output.content = self.item['item_id']
    self.status_output.content = self.item['status']

    # Any code you write here will run before the form opens.

  def remove_item_btn_click(self, **event_args):
    #All we do is raise events. Resolve Modal logic handles the events
    self.parent.raise_event('x-remove-item-btn', 
                     fulfillment_id=self.item['fulfillment_id'])

  def replace_item_btn_click(self, **event_args):
    #All we do is raise events. Resolve Modal logic handles the events
    self.parent.raise_event('x-replace-item-btn', 
                     item_id=self.item['item_id'], 
                     fulfillment_id=self.item['fulfillment_id'])