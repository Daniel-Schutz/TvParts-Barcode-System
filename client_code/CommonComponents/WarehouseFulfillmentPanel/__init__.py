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

    # Any code you write here will run before the form opens.

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