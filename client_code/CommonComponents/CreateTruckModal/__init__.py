from ._anvil_designer import CreateTruckModalTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class CreateTruckModal(CreateTruckModalTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def clear_btn_click(self, **event_args):
    self.truck_name_input.text = None
    self.truck_name_input.focus()

  def cancel_btn_click(self, **event_args):
    self.raise_event('x-close-alert', value=None)

  def create_truck_click(self, **event_args):
    if not self.truck_name_input.text:
      n = Notification("You must enter a value to create a truck!",
                       title="Error: No Input", style='danger')
      n.show()
      self.truck_name_input.focus()
      return None
    else:
      self.raise_event('x-close-alert', value=self.truck_name_input.text)
