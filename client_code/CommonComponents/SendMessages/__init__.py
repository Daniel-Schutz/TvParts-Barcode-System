from ._anvil_designer import SendMessagesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class SendMessages(SendMessagesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.from_name_textbox.text = anvil.server.call('get_user_first_name')
    self.from_role_textbox_name_textbox.text = anvil.server.call('get_user_role')
    

    # Any code you write here will run before the form opens.
