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

  def generate_analysis_btn_click(self, **event_args):
    years = anvil.server.call('needs_attention_rate_per_employee')
    print(years)
    """This method is called when the button is clicked"""
    pass

  def control_panel_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
self.main_content_panel.clear()
    self.main_content_panel.add_component(ControlPanel(current_user=self.current_user, 
                                                      current_role=self.current_role), 
                                          full_width_row=True)
    self.control_panel_btn.role = 'raised'
    self.action_panel_btn.role = 'primary-color'
    self.dashboard_btn.role = 'primary-color'
    self.role_nav_btn.role = 'primary-color'