from ._anvil_designer import AllBookingsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

#todo: fix past bookings formatting

class AllBookings(AllBookingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.sort_drop.items = [("Sort by date", "datetime"), ("Sort by user", "user")]
    current_bookings, past_bookings = anvil.server.call('get_bookings')
    self.repeating_panel_1.items = current_bookings
    self.repeating_panel_2.items = past_bookings


  def sort_drop_change(self, **event_args):
    """This method is called when an item is selected"""
    current_bookings, past_bookings = anvil.server.call('get_bookings', self.sort_drop.selected_value)
    self.repeating_panel_1.items = current_bookings
    self.repeating_panel_2.items = past_bookings

