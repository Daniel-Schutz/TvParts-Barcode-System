from ._anvil_designer import SendMessagesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


#TODO: Make it so that the item_scan fetches the original QR code,
#      so that it can be scanned directly from the screen

class SendMessages(SendMessagesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.from_name_textbox.text = f"{anvil.server.call('get_user_first_name')} {anvil.server.call('get_user_last_name')}"
    self.from_role_textbox.text = anvil.server.call('get_user_role')
    self.role_dropdown.items = anvil.server.call('get_roles_dropdown')
    self.quick_msg_dropdown.items = anvil.server.call('get_quick_msg_dropdown')
    # Any code you write here will run before the form opens.

  def validate_quick_send(self):
    if self.role_dropdown.selected_value and self.quick_msg_dropdown.selected_value:
      return True
    else:
      anvil.alert("Message requires both Role and Message before send.")

  def validate_long_send(self):
    if self.role_dropdown.selected_value and self.long_msg_box.text:
      return True    
    else:
      anvil.alert("Message requires both Role and Message before send.")

######### EVENTS ###################################  
  def quick_msg_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.validate_quick_send():
      anvil.server.call('create_message', 
                        self.from_name_textbox.text,
                       self.from_role_textbox.text,
                       self.role_dropdown.selected_value,
                       self.quick_msg_dropdown.selected_value,
                       self.item_qr_scan.text)
      result = anvil.alert(title="Message Sent", buttons=["OK"])
      if result == "OK":
        self.raise_event("x-close-alert", value=42)

  def long_msg_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.validate_long_send():
      anvil.server.call('create_message', 
                        self.from_name_textbox.text,
                       self.from_role_textbox.text,
                       self.role_dropdown.selected_value,
                       self.long_msg_box.text,
                       self.item_qr_scan.text)
      result = anvil.alert(title="Message Sent", buttons=["OK"])
      if result == "OK":
        self.raise_event("x-close-alert", value=42)


      


