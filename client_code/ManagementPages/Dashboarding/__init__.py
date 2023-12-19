from ._anvil_designer import DashboardingTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Dashboarding(DashboardingTemplate):
  def __init__(self, current_user, current_role, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.current_user = current_user
    self.current_role = current_role

    # Any code you write here will run before the form opens.

  def select_role_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  def select_role_dropdown_copy_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  def comp_type_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  def categorize_by_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  def time_period_quick_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  def date_picker_1_change(self, **event_args):
    """This method is called when the selected date changes"""
    print("test")
    pass
