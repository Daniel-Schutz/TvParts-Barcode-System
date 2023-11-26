from ._anvil_designer import MovetoTrayTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class MovetoTray(MovetoTrayTemplate):
  def __init__(self, user, role, order_no, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.current_user = user
    self.current_role = role
    self.current_order = order_no
    self.tray_picker_dropdown.items = anvil.server.call('get_open_trays_for_dd')
    self.tray_picker_dropdown.selected_value = '(Select Tray)'

    # Any code you write here will run before the form opens.

#### Respond to button push ####
  def move_to_tray_btn_click(self, **event_args):
    tray = self.tray_picker_dropdown.selected_value()
    if tray == '(Select Tray)':
      n_1 = Notification("You must select a proper tray.", style='danger')
      n_1.show()
      return None
    anvil.server.call('move_order_to_tray', self.current_order, tray)
    # n = Notification("Order has been moved into fulfillment in the system. Place the order on the Tray to await processing.",
    #                 title='Order Moved!', style='success')
    # n.show()
    self.raise_event('x-close-alert', value=tray)