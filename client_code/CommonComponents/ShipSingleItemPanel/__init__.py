from ._anvil_designer import ShipSingleItemPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ShipSingleItemPanel(ShipSingleItemPanelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.set_event_handler('x-item_scanned', self.on_item_scanned)
    self.init_components(**properties)
    self.item_id_label.text = self.item['item_id']

    # Any code you write here will run before the form opens.

# Raise event for needs attention
  def needs_attention_btn_click(self, **event_args):
    self.parent.raise_event('x-ship-needs-attention', 
                            item_id=self.item['item_id'], 
                            fulfillment_id=self.item['fulfillment_id'])

# Change display on the panel when the right item is scanned
  def on_item_scanned(self, item_id, **event_args):
    if item_id == self.item['item_id']:
      print("Setting fulfillment to Packed.")
      self.waiting_label.visible = False
      self.ready_label.visible = True
      self.main_card.background = '#EEEEEE'
      anvil.server.call_s('set_f_status_by_item_id', item_id, "Packed")
      # Take care of item updates from the main form to capture user and role 
      # (we are doing this instead of adding the user and role to the repeater.items
      self.parent.raise_event('x-update-item-in-bk', item_id=item_id)