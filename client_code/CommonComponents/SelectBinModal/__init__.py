from ._anvil_designer import SelectBinModalTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class SelectBinModal(SelectBinModalTemplate):
  def __init__(self, primary_bin, mode='os_bins', **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.set_bin_btn.visible = False
    self.primary_bin = primary_bin
    if mode == 'os_bins':
      self.get_os_bin_dropdown()
    elif mode == 'open_bins':
      self.get_open_bin_dropdown()
    elif mode == 'registered':
      self.get_any_bin_dropdown()
    else:
      raise ValueError("Bin Modal operating mode must be in ['os_bins', 'open_bins', 'registered']")
    self.bin_drop_down.selected_value = '(Select Bin)'

    # Any code you write here will run before the form opens.

# Get bin dropdown based on existing os_bins
  def get_os_bin_dropdown(self):
    bin_list = anvil.server.call('get_all_bins_from_primary', 
                              self.primary_bin)
    self.bin_drop_down.items = anvil.server.call('create_select_bin_dropdown', 
                                                 bin_list)

# Get bin dropdown based on open bins available
  def get_open_bin_dropdown(self):
    self.bin_drop_down.items = anvil.server.call('get_open_bins_dropdown')

# Get bin dropdown for any bins registered in the system
  def get_any_bin_dropdown(self):
    bin_list = anvil.server.call('get_all_registered_bins', self.primary_bin)
    self.bin_drop_down.items = anvil.server.call('create_select_bin_dropdown', 
                                              bin_list)

# Only show submit when a valid value is chosen
  def bin_drop_down_changed(self, **event_args):
    if self.bin_drop_down.selected_value == '(Select Bin)':
      self.set_bin_btn.visible = False
    else:
      self.set_bin_btn.visible = True

# Return selected bin upon submit
  def set_bin_btn_click(self, **event_args):
    self.raise_event('x-close-alert', value=self.bin_drop_down.selected_value)