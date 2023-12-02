from ._anvil_designer import Temp_ServerTestTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import js
import anvil.media

from ...CommonComponents.SendMessages import SendMessages
from ...CommonComponents.RecieveMessages import RecieveMessages
from ..IdModule import IdModule
from ..WarehouseStockModule import WarehouseStockModule
from ..WarehousePickModule import WarehousePickModule
from ...CommonComponents.ItemLookup import ItemLookup
from ..ManagementMasterModule import ManagementMasterModule
from ..TestingModule import TestingModule
from ..ShippingModule import ShippingModule

import uuid
import datetime
import time
import json

class Temp_ServerTest(Temp_ServerTestTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

######### COMPONENT EVENTS ############################

  def management_area_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.parent.add_component(ManagementMasterModule(), full_width_row=True)
    self.remove_from_parent()

  def modal_recieve_msg_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    recieve_msg_modal = RecieveMessages()
    anvil.alert(
      recieve_msg_modal, 
      title="All Messages",
      buttons=["CLOSE"],
      large=True
    )


  def db_test_click(self, **event_args):
    start_time = time.time()
    count = anvil.server.call('test_db_search')
    self.result_count.text = count
    end_time = time.time()
    print(f"Took {end_time-start_time} seconds")

  def radio_submit_click(self, **event_args):
    if self.exact_radio.selected:
      print(f"radio button changed, selected value: {self.exact_radio.value}")
    elif self.contains_radio.selected:
      print(f"radio button changed, selected value: {self.contains_radio.value}")
    # sku = 'EAT65193302'
    # row = anvil.server.call('get_product_row_by_sku',sku)
    # [print(entry) for entry in row]

  # def group_radio_changed(self, **event_args):
  #   """This method is called when this radio button is selected"""
  #   if self.exact_radio.selected:
  #     selected_value = self.exact_radio.value
  #   elif self.contains_radio.selected:
  #     selected_value = self.contains_radio.value

  def to_wh_stock_screen_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    # self.parent.add_component(WarehouseStockModule(), full_width_row=True)
    # self.remove_from_parent()
    self.parent.add_component(WarehousePickModule(), full_width_row=True)
    self.remove_from_parent()  

  def to_id_screen_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.parent.add_component(IdModule(), full_width_row=True)
    self.remove_from_parent()  

  def test_notification_click(self, **event_args):
    """This method is called when the button is clicked"""
    n = Notification("Item has been denoted as misidentified. Please set item aside for management.", 
                     style='danger', title='Part Misidentified', timeout=2)    
    n.show()

  def test_screen_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.parent.add_component(TestingModule(), full_width_row=True)
    self.remove_from_parent() 

  def reset_orders_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('reset_open_tables')

  def item_lookup_btn_click(self, **event_args):
    print("clicked item lookup")
    anvil.alert(ItemLookup())
  
  def warehouse_pick_btn_click(self, **event_args):
      self.parent.add_component(WarehousePickModule(), full_width_row=True)
      self.remove_from_parent() 

  def shipping_area_btn_click(self, **event_args):
      self.parent.add_component(ShippingModule(), full_width_row=True)
      self.remove_from_parent() 