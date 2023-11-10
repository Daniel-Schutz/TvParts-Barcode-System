from ._anvil_designer import ItemTemplate2Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import MyBookings

class ItemTemplate2(ItemTemplate2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)


  def delete_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    confirmed = alert("Are you sure you want to delete this booking?",
                      buttons=[("Yes", True), ("No", False)])
    if confirmed:
      anvil.server.call('delete_booking', self.item)
      get_open_form().content_panel.clear()
      get_open_form().content_panel.add_component(MyBookings())


