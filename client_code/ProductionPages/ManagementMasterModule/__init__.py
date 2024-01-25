from ._anvil_designer import ManagementMasterModuleTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...ManagementPages.ActionPanel import ActionPanel
from ...ManagementPages.ControlPanel import ControlPanel
from ...ManagementPages.Dashboarding import Dashboarding
from ...ManagementPages.RoleNavigation import RoleNavigation

class ManagementMasterModule(ManagementMasterModuleTemplate):
  def __init__(self, current_user, current_role, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.current_user = current_user
    self.current_role = current_role
    self.main_content_panel.add_component(ActionPanel(current_user=current_user, 
                                                      current_role=current_role), 
                                          full_width_row=True)
    self.action_panel_btn.role = 'raised'
    # Any code you write here will run before the form opens.

######### Button Navigation using SPA ###################
  def control_panel_btn_click(self, **event_args):
    anvil.server.call('add_qr_products_bk') 
    #anvil.server.call('update_description') just testing
    self.main_content_panel.clear()
    self.main_content_panel.add_component(ControlPanel(current_user=self.current_user, 
                                                      current_role=self.current_role), 
                                          full_width_row=True)
    self.control_panel_btn.role = 'raised'
    self.action_panel_btn.role = 'primary-color'
    self.dashboard_btn.role = 'primary-color'
    self.role_nav_btn.role = 'primary-color'

  def action_panel_btn_click(self, **event_args):
    self.main_content_panel.clear()
    self.main_content_panel.add_component(ActionPanel(current_user=self.current_user, 
                                                      current_role=self.current_role), 
                                          full_width_row=True)
    self.control_panel_btn.role = 'primary-color'
    self.action_panel_btn.role = 'raised'
    self.dashboard_btn.role = 'primary-color'
    self.role_nav_btn.role = 'primary-color'

  def dashboard_btn_click(self, **event_args):
    self.main_content_panel.clear()
    self.main_content_panel.add_component(Dashboarding(current_user=self.current_user, 
                                                      current_role=self.current_role), 
                                          full_width_row=True)
    self.control_panel_btn.role = 'primary-color'
    self.action_panel_btn.role = 'primary-color'
    self.dashboard_btn.role = 'raised'
    self.role_nav_btn.role = 'primary-color'

  def role_nav_btn_click(self, **event_args):
    self.main_content_panel.clear()
    self.main_content_panel.add_component(RoleNavigation(current_user=self.current_user, 
                                                      current_role=self.current_role), 
                                          full_width_row=True)
    self.control_panel_btn.role = 'primary-color'
    self.action_panel_btn.role = 'primary-color'
    self.dashboard_btn.role = 'primary-color'
    self.role_nav_btn.role = 'raised'