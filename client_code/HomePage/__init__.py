from ._anvil_designer import HomePageTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..EntryComponents.ChooseRole import ChooseRole
from ..AdminSettings import AdminSettings
from ..ProductionPages import TeardownModule


class HomePage(HomePageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.show_links()
    if anvil.users.get_user():
      self.route_to_role()
      


########## MAIN #############################
  def show_links(self):
    if anvil.users.get_user():
      self.sign_out_link.visible = True
      self.sign_in_link.visible = False
      if anvil.server.call('check_admin'):
        self.settings_link.visible = True

  def role_navigation(self):
    user = anvil.users.get_user()
    if user is not None:
      self.route_to_role()
    else:
      self.content_panel.add_component(ChooseRole(), full_width_row=True)
    
  def role_router(self, user_role):
    if user_role == "Teardown":
      self.content_panel.add_component(TeardownModule(), full_width_row=True)


  def route_to_role(self):
    user_role = anvil.server.call('get_user_role')
    self.role_router(user_role)
######## HOME PAGE EVENTS ############################  

  def settings_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    if anvil.server.call('check_admin'):
      get_open_form().content_panel.clear()
      get_open_form().content_panel.add_component(AdminSettings())

  def sign_out_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    anvil.users.logout()
    open_form('HomePage')

  def sign_in_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    anvil.users.login_with_form()
    self.role_navigation()
    #open_form('HomePage')
