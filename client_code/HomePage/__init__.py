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
from ..CommonComponents.SendMessages import SendMessages
from ..CommonComponents.RecieveMessages import RecieveMessages
from ..ProductionPages.Temp_ServerTest import Temp_ServerTest


class HomePage(HomePageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.show_links()
    if anvil.users.get_user():
      self.role_navigation()
      


########## MAIN #############################
  def show_links(self):
    print("show_links called")
    user = anvil.users.get_user()
    print(f"User logged in: {user is not None}")
    if user:
      self.sign_out_link.visible = True
      self.sign_in_link.visible = False
      self.test_area.visible = True
      self.send_message_btn.visible = True
      self.role_home_btn.visible = True
      print(f"test_area visibility set to: {self.test_area.visible}")
      if anvil.server.call('check_admin'):
        self.settings_link.visible = True
        
        
      # #This is for me (Issac) to get to my testing page
      # user = anvil.users.get_user()
      # user_email = user['email']
      # if user_email == 'issac@getautonomi.com':
        

  def role_navigation(self):
    user = anvil.users.get_user()
    user_role = anvil.server.call('get_user_role')
    if user_role is not None:
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
    self.content_panel.clear()
    open_form('HomePage')

  def sign_in_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    anvil.users.login_with_form()
    self.role_navigation()
    self.show_links()
    #open_form('HomePage')

  def role_home_btn_click(self, **event_args):
    self.content_panel.clear()
    self.role_navigation()

  def send_message_click(self, **event_args):
    """This method is called when the link is clicked"""
    send_msg_modal = SendMessages()
    anvil.alert(
      send_msg_modal, 
      title="Send New Message",
      buttons=[],
      large=True
    )
  def test_area_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.content_panel.clear()
    self.content_panel.add_component(Temp_ServerTest(), full_width_row=True)

  def mail_click(self, **event_args):
    recieve_msg_modal = RecieveMessages()
    anvil.alert(
      recieve_msg_modal, 
      title="All Messages",
      buttons=["CLOSE"],
      large=True
    )
