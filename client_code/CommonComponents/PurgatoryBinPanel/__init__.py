from ._anvil_designer import PurgatoryBinPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class PurgatoryBinPanel(PurgatoryBinPanelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.bin_content.content = self.item['bin']
    self.purg_count_content.content = self.item['purgatory_count']
    self.name_content.content = self.item['product_name']
    self.sku_content.content = self.item['sku']
    self.os_bin_output.content = self.item['os_bins']
    self.crs_output.content = self.item['cross_refs']

    # Any code you write here will run before the form opens.

#Raise events for button presses, we don't deal with logic in here
  def remove_from_purgatory_btn_click(self, **event_args):
    self.parent.raise_event('x-purg-remove-bin-only', bin=self.item(bin))

  def move_all_to_bin_btn_click(self, **event_args):
    self.parent.raise_event('x-purg-move-all-items', bin=self.item(bin))

  def toss_all_items_btn_click(self, **event_args):
    self.parent.raise_event('x-purg-toss-all-items', bin=self.item(bin))