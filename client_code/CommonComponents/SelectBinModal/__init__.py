from ._anvil_designer import SelectBinModalTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class SelectBinModal(SelectBinModalTemplate):
  def __init__(self, primary_bin, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.set_bin_btn.visible = False
    self.primary_bin = primary_bin
    self.get_bin_dropdown()
    self.bin_drop_down.selected_value = '(Select Bin)'

    # Any code you write here will run before the form opens.

# Create a bin dropdown from the list
  def get_bin_dropdown(self):
    bin_list = anvil.server.call('get_all_bins_from_primary', 
                              self.primary_bin)
    self.bin_drop_down.items = anvil.server.call('create_select_bin_dropdown', 
                                                 bin_list)

# Only show submit when a valid value is chosen
  def bin_drop_down_changed(self, **event_args):
    if bin_drop_down.selected_value == '(Select Bin)':
      self.set_bin_btn.visible = False
    else:
      self.set_bin_btn.visible = True

# Return selected bin upon submit
  def set_bin_btn_click(self, **event_args):
    self.raise_event('x-close-alert', value=self.bin_drop_down.selected_value)