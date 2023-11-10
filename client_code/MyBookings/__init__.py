from ._anvil_designer import MyBookingsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class MyBookings(MyBookingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    current_bookings, past_bookings = anvil.server.call('get_bookings')
    self.repeating_panel_1.items = current_bookings
    self.repeating_panel_2.items = past_bookings

    