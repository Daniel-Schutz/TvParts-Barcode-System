from ._anvil_designer import NeedFixedItemPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ... import CommonComponents #might need to figure out why I can't get the modal in here

class NeedFixedItemPanel(NeedFixedItemPanelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.item_id_output.content = self.item['item_id']
    self.primary_bin_output.content = self.item['primary_bin']

    # Any code you write here will run before the form opens.

# Move an item to a bin after being fixed
  def move_to_bin_click(self, **event_args):
    print('read move_to_bin click in NF')
    self.parent.raise_event('x-nf-move-to-bin', 
                            primary_bin=self.item['primary_bin'], 
                            item_id=self.item['item_id'])

# Toss an item
  def toss_btn_click(self, **event_args):
    print('read toss_item click in NF')
    self.parent.raise_event('x-nf-toss-item', 
                            item_id=self.item['item_id'])
  