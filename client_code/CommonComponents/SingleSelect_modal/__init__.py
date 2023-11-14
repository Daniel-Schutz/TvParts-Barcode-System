from ._anvil_designer import SingleSelect_modalTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class SingleSelect_modal(SingleSelect_modalTemplate):
  def __init__(self, trucks, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.repeating_panel_1.items = trucks
    self.repeating_panel_1.set_event_handler('x-truck-selected', self.truck_selected)

    # Any code you write here will run before the form opens.

  def truck_selected(self, truck_id, **event_args):
    self.raise_event('x-close-alert', value=truck_id)