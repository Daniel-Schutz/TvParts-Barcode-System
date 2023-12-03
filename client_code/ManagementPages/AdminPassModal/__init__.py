from ._anvil_designer import AdminPassModalTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class AdminPassModal(AdminPassModalTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.admin_passcode = anvil.server.call('get_admin_passcode')
    # Any code you write here will run before the form opens.

  
  ############# EVENTS ###########################
  def button_submit_click(self, **event_args):
    if not self.admin_pass_code_input.text:
      n = Notification("You didn't enter a password", 
                       style='danger', timeout=1)
      n.show()
      return None
    elif self.admin_pass_code_input.text == self.admin_passcode:
      self.raise_event('x-close-alert', value='Granted')
    else:
      self.raise_event('x-close-alert', value='Denied')

  def close_btn_click(self, **event_args):
    self.raise_event('x-close-alert', value='Closed')
    

