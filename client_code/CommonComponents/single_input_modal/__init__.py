from ._anvil_designer import single_input_modalTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class single_input_modal(single_input_modalTemplate):
  def __init__(self, label_text="Enter Value:", **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.label.text = label_text

    # Any code you write here will run before the form opens.
############# EVENTS ###########################
  def button_submit_click(self, **event_args):
    # This function is called when the button is clicked
    self.raise_event('x-close-alert', value=self.text_box.text)

