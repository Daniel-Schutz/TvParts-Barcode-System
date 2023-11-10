from ._anvil_designer import HomePageTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..EntryComponents.ChooseRole import ChooseRole
from ..AdminSettings import AdminSettings


class HomePage(HomePageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    #self.content_panel.add_component(ChooseRole(), full_width_row=True)
    self.show_links()
  
  def show_links(self):
    if anvil.users.get_user():
      self.sign_out_link.visible = True
      self.bookings_link.visible = True
      self.sign_in_link.visible = False
      self.make_booking_link.visible = True
      if anvil.server.call('check_admin'):
        self.settings_link.visible = True


  def sign_out_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    anvil.users.logout()
    open_form('HomePage')

  def sign_in_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    anvil.users.login_with_form()
    self.role_navigation()
    #open_form('HomePage')

  def role_navigation(self):
    if anvil.users.get_user():
      user_role = anvil.server.call('get_user_role')
      if user_role is None:
        self.content_panel.add_component(ChooseRole(), full_width_row=True)
        self.show_links()
      else:
        print("The Logged in user has the role:", user_role)
        self.show_links()
      

  def settings_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    if anvil.server.call('check_admin'):
      get_open_form().content_panel.clear()
      get_open_form().content_panel.add_component(AdminSettings())





  # def link_2_click(self, **event_args):
  #   """This method is called when the link is clicked"""
  #   self.content_panel.clear()
  #   self.content_panel.add_component(BookATime(), full_width_row=True)

  # def bookings_link_click(self, **event_args):
  #   """This method is called when the link is clicked"""
  #   get_open_form().content_panel.clear()
  #   if anvil.server.call('check_admin'):
  #     get_open_form().content_panel.add_component(AllBookings())
  #   else:
  #     get_open_form().content_panel.add_component(MyBookings())

  # def make_booking_link_click(self, **event_args):
  #   """This method is called when the link is clicked"""
  #   self.link_2_click()
