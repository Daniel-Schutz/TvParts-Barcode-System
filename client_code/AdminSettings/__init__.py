from ._anvil_designer import AdminSettingsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime
#set dropdown from settings table in init

class AdminSettings(AdminSettingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.convert_interval(app_tables.settings.get(key="interval")['value'])
    
    self.max_date_row = app_tables.settings.get(key="max_date") 
    self.num_row = app_tables.settings.get(key="num_bookings")
    
    self.init_components(**properties)
    self.repeating_panel_1.items = app_tables.open_hours.search()
    self.timezone_drop.items = anvil.server.call("get_timezones")
    self.timezone_drop.selected_value = app_tables.settings.get(key="tz")['value']

  def convert_interval(self, value):
    if value % 60 == 0:
      self.interval_drop.selected_value = "hours"
      self.interval_box.text = int(value / 60)
    else:
      self.interval_drop.selected_value = "minutes"
      self.interval_box.text = value
      
## events for interval
  def interval_box_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.save_link.visible = True
    self.cancel_link.visible = True
    
  def interval_drop_change(self, **event_args):
    """This method is called when an item is selected"""
    self.save_link.visible = True
    self.cancel_link.visible = True
    
  def save_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    if self.interval_box.text:
      interval = self.interval_box.text*60 if self.interval_drop.selected_value == "hours" else self.interval_box.text
      anvil.server.call('update_settings_table', 'interval', interval)
      self.save_link.visible = False
      self.cancel_link.visible = False
    else:
      Notification("Please enter a number").show()

  def cancel_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.convert_interval(app_tables.settings.get(key="interval")['value'])
    self.save_link.visible = False
    self.cancel_link.visible = False
    
## click events for max date
  def max_date_box_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.save_max_link.visible = True
    self.cancel_max_link.visible = True

  def save_max_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    if self.max_date_box.text:
      anvil.server.call('update_settings_table', "max_date", self.max_date_box.text)
      self.save_max_link.visible = False
      self.cancel_max_link.visible = False
    else:
      Notification("Please enter a number").show()
      
  def cancel_max_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.refresh_data_bindings()
    self.save_max_link.visible = False
    self.cancel_max_link.visible = False

## click events for number of bookings per slot
  def booking_num_box_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.save_num_link.visible = True
    self.cancel_num_link.visible = True

  def save_num_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    if self.booking_num_box.text:
      anvil.server.call('update_settings_table', 'num_bookings', self.booking_num_box.text)
      self.save_num_link.visible = False
      self.cancel_num_link.visible = False
    else:
      Notification("Please enter a number").show()

  def cancel_num_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.refresh_data_bindings()
    self.save_num_link.visible = False
    self.cancel_num_link.visible = False

  def location_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('reset_timezone',self.timezone_drop.selected_value)
    
  






