from ._anvil_designer import Form1Template
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..BookATime import BookATime
from ..AdminSettings import AdminSettings
from ..MyBookings import MyBookings
from ..AllBookings import AllBookings
from ..BookATime import BookATime


class Form1(Form1Template):

  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.content_panel.add_component(BookATime(), full_width_row=True)
    self.show_links()
  
  def show_links(self):
    if anvil.users.get_user():
      self.sign_out_link.visible = True
      self.bookings_link.visible = True
      self.sign_in_link.visible = False
      self.make_booking_link.visible = True
      if anvil.server.call('check_admin'):
        self.settings_link.visible = True


  def link_2_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.content_panel.clear()
    self.content_panel.add_component(BookATime(), full_width_row=True)

  def sign_out_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    anvil.users.logout()
    open_form('Form1')

  def sign_in_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    anvil.users.login_with_form()
    open_form('Form1')

  def bookings_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    get_open_form().content_panel.clear()
    if anvil.server.call('check_admin'):
      get_open_form().content_panel.add_component(AllBookings())
    else:
      get_open_form().content_panel.add_component(MyBookings())

  def settings_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    if anvil.server.call('check_admin'):
      get_open_form().content_panel.clear()
      get_open_form().content_panel.add_component(AdminSettings())

  def make_booking_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.link_2_click()







