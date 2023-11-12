from ._anvil_designer import RecieveMessagesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RecieveMessages(RecieveMessagesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.received_msgs_panel.set_event_handler('x-refresh-messages', self.refresh_messages)
    self.refresh_messages()

    # Any code you write here will run before the form opens.
# In your main form where the RepeatingPanel is located
  def refresh_messages(self):
    role_to = anvil.users.get_user()['role']
    messages = anvil.server.call('get_role_recieved_msgs', role_to)
    self.received_msgs_panel.items = messages
