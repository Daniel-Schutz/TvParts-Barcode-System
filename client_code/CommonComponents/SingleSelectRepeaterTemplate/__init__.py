from ._anvil_designer import SingleSelectRepeaterTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class SingleSelectRepeaterTemplate(SingleSelectRepeaterTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def form_show(self, **event_args):
    self.label_1.text = self.item['truck_id']

  def select_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.parent.raise_event('x-truck-selected', truck_id=self.item['truck_id'])
