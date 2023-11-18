from ._anvil_designer import WarehouseStockModuleTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...CommonComponents import CommonFunctions as cf

class WarehouseStockModule(WarehouseStockModuleTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.mode = 'verify'
    self.verify_part_btn.enabled = False
    self.place_part_card.visible=False
    admin_settings = anvil.server.call('get_admin_settings')
    self.require_bin_to_place = admin_settings['require_bin_verify']
    # Any code you write here will run before the form opens.


############ Change View Events #############################

  def verify_part_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.verify_part_btn.enabled = False
    self.place_part_btn.enabled = True
    self.verify_part_btn.role = 'secondary-color'
    self.place_part_btn.role = 'primary-color'
    self.verify_part_card.visible = True
    self.place_part_card.visible = False

  def place_part_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.verify_part_btn.enabled = True
    self.place_part_btn.enabled = False
    self.verify_part_btn.role = 'primary-color'
    self.place_part_btn.role = 'secondary-color'
    self.verify_part_card.visible = False
    self.place_part_card.visible = True
    if not self.require_bin_to_place:
      
    
