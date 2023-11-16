from ._anvil_designer import IdModuleTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import js
import anvil.media
import time

from ...CommonComponents.ProductExplorer import ProductExplorer

import uuid
import datetime
import time
import json

class IdModule(IdModuleTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.make_dropdown.items = anvil.server.call('get_make_dropdown')
    self.year_dropdown.items = anvil.server.call('get_year_dropdown')
    self.size_dropdown.items = anvil.server.call('get_size_dropdown')






######### COMPONENT EVENTS ############################
  def on_truck_code_enter(self, **event_args):
    truck_code = self.truck_code_input.text
    supplier, truck = anvil.server.call('get_supplier_truck_from_code', truck_code)
    self.supplier_scan_output.content = supplier
    self.truck_scan_output.content = truck
    self.truck_code_input.enabled = False

  def lock_box_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.make_dropdown.enabled = False
    self.model_input_bx.enabled = False
    self.year_dropdown.enabled = False
    self.size_dropdown.enabled = False

  def reset_bx_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.truck_code_input.text = None
    self.truck_code_input.enabled = True
    self.supplier_scan_output.content = None
    self.truck_scan_output.content = None
    self.make_dropdown.enabled = True
    self.make_dropdown.selected_value = None
    self.model_input_bx.text = None
    self.model_input_bx.enabled = True
    self.year_dropdown.enabled = True
    self.year_dropdown.selected_value = None
    self.size_dropdown.enabled = True
    self.size_dropdown.selected_value = None

  def launch_pdt_explr_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    product_explorer = ProductExplorer()
    selected_product = alert(product_explorer, 
                            title="Select Product", 
                            large=True)
    self.selected_product_display.text = selected_product

