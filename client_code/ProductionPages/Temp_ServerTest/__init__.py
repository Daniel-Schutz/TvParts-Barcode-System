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

import uuid
import datetime
import time
import json

class Temp_ServerTest(Temp_ServerTestTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)






######### COMPONENT EVENTS ############################

  def modal_send_msg_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    send_msg_modal = SendMessages()
    anvil.alert(
      send_msg_modal, 
      title="Send New Message",
      buttons=[],
      large=True
    )

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

  # def group_radio_changed(self, **event_args):
  #   """This method is called when this radio button is selected"""
  #   if self.exact_radio.selected:
  #     selected_value = self.exact_radio.value
  #   elif self.contains_radio.selected:
  #     selected_value = self.contains_radio.value

  def to_wh_stock_screen_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.parent.add_component(WarehouseStockModule(), full_width_row=True)
    self.remove_from_parent()

  def test_notification_click(self, **event_args):
    """This method is called when the button is clicked"""
    n = Notification("Item has been denoted as misidentified. Please set item aside for management.", 
                     style='danger', title='Part Misidentified', timeout=2)    
    n.show()
