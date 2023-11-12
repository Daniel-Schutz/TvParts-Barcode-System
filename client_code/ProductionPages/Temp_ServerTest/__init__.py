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

