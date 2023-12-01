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
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

# Raise event for needs attention
  def needs_attention_btn_click(self, **event_args):
    self.raise_event('x-ship-needs-attention', item_id=self.item['item_id'])