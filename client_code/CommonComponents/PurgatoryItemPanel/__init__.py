from ._anvil_designer import PurgatoryItemPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class PurgatoryItemPanel(PurgatoryItemPanelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.item_id_output.content = self.item['item_id']
    self.primary_bin_output.content = self.item['bin']

    # Any code you write here will run before the form opens.

# Raise events for buttons - we don't do logic in here
  def move_to_bin_btn_click(self, **event_args):
    self.parent.raise_event('x-purg-move-single-item', 
                            primary_bin=self.item['bin'], 
                            item_id=item['item_id'])

  def toss_btn_click(self, **event_args):
    self.parent.raise_event('x-purg-toss-single-item',
                            item_id=item['item_id'])