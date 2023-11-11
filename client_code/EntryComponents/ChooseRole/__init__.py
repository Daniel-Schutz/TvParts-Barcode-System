from ._anvil_designer import ChooseRoleTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ChooseRole(ChooseRoleTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.selected_role = None

  def teardown_button_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.selected_role = "Teardown"

  def id_button_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.selected_role = "Id"

  def warehouse_button_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.selected_role = "Warehouse"

  def testing_button_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.selected_role = 'Testing'

  def shipping_button_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.selected_role = 'Shipping'

  def cs_button_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.selected_role = 'Customer Service'

  def submit_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    force_retry = False
    if self.selected_role:
      if self.first_name_entry.text:
        if self.last_name_entry.text:
          anvil.server.call('set_user_role', self.selected_role)
          anvil.server.call('set_user_first_name', self.first_name_entry.text)
          anvil.server.call('set_user_last_name', self.last_name_entry.text)
          self.remove_from_parent()
        else:
          force_retry = True
      else:
        force_retry = True 
    else:
      force_retry = True
    if force_retry:
      anvil.alert("All values required.")
    







