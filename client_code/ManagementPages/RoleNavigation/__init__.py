from ._anvil_designer import RoleNavigationTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...ProductionPages.TeardownModule import TeardownModule
from ...ProductionPages.IdModule import IdModule
from ...ProductionPages.WarehousePickModule import WarehousePickModule
from ...ProductionPages.WarehouseStockModule import WarehouseStockModule
from ...ProductionPages.TestingModule import TestingModule
from ...ProductionPages.ShippingModule import ShippingModule

class RoleNavigation(RoleNavigationTemplate):
  def __init__(self, current_user, current_role, **properties):
    # Set Form properties and Data Bindings.
    self.current_user = current_user
    self.current_role = current_role
    self.init_components(**properties)
    self.init_messages()
    self.selected_color = '#236F65'
    self.open_color = '#3FA498'
    self.msg_inbox_repeater.set_event_handler('x-refresh-messages', self.refresh_messages)

    # Any code you write here will run before the form opens.

#### Change views (evets and logic) ########################
  def teardown_view(self):
    self.role_page_view_panel.clear()
    self.role_page_view_panel.add_component(TeardownModule(current_user=self.current_user, 
                                                           current_role=self.current_role), 
                                            full_width_row=True)
    self.teardown_role_btn.background = self.selected_color
    self.id_role_btn.background = self.open_color
    self.warehouse_pick_role_btn.background = self.open_color
    self.warehouse_stock_role_btn.background = self.open_color
    self.testing_role_btn.background = self.open_color
    self.shipping_role_btn.background = self.open_color
    self.all_inboxes_btn.background = self.open_color
    self.role_page_view_panel.visible = True
    self.messages_card.visible = False

  def id_view(self):
    self.role_page_view_panel.clear()
    self.role_page_view_panel.add_component(IdModule(current_user=self.current_user, 
                                                           current_role=self.current_role), 
                                            full_width_row=True)
    self.teardown_role_btn.background = self.open_color
    self.id_role_btn.background = self.selected_color
    self.warehouse_pick_role_btn.background = self.open_color
    self.warehouse_stock_role_btn.background = self.open_color
    self.testing_role_btn.background = self.open_color
    self.shipping_role_btn.background = self.open_color
    self.all_inboxes_btn.background = self.open_color
    self.role_page_view_panel.visible = True
    self.messages_card.visible = False

  def wh_pick_view(self):
    self.role_page_view_panel.clear()
    self.role_page_view_panel.add_component(WarehousePickModule(current_user=self.current_user, 
                                                           current_role=self.current_role), 
                                            full_width_row=True)
    self.teardown_role_btn.background = self.open_color
    self.id_role_btn.background = self.open_color
    self.warehouse_pick_role_btn.background = self.selected_color
    self.warehouse_stock_role_btn.background = self.open_color
    self.testing_role_btn.background = self.open_color
    self.shipping_role_btn.background = self.open_color
    self.all_inboxes_btn.background = self.open_color
    self.role_page_view_panel.visible = True
    self.messages_card.visible = False

  def wh_stock_view(self):
    self.role_page_view_panel.clear()
    self.role_page_view_panel.add_component(WarehouseStockModule(current_user=self.current_user, 
                                                           current_role=self.current_role), 
                                            full_width_row=True)
    self.teardown_role_btn.background = self.open_color
    self.id_role_btn.background = self.open_color
    self.warehouse_pick_role_btn.background = self.open_color
    self.warehouse_stock_role_btn.background = self.selected_color
    self.testing_role_btn.background = self.open_color
    self.shipping_role_btn.background = self.open_color
    self.all_inboxes_btn.background = self.open_color
    self.role_page_view_panel.visible = True
    self.messages_card.visible = False

  def testing_view(self):
    self.role_page_view_panel.clear()
    self.role_page_view_panel.add_component(TestingModule(current_user=self.current_user, 
                                                           current_role=self.current_role), 
                                            full_width_row=True)
    self.teardown_role_btn.background = self.open_color
    self.id_role_btn.background = self.open_color
    self.warehouse_pick_role_btn.background = self.open_color
    self.warehouse_stock_role_btn.background = self.open_color
    self.testing_role_btn.background = self.selected_color
    self.shipping_role_btn.background = self.open_color
    self.all_inboxes_btn.background = self.open_color
    self.role_page_view_panel.visible = True
    self.messages_card.visible = False   

  def shipping_view(self):
    self.role_page_view_panel.clear()
    self.role_page_view_panel.add_component(ShippingModule(current_user=self.current_user, 
                                                           current_role=self.current_role), 
                                            full_width_row=True)
    self.teardown_role_btn.background = self.open_color
    self.id_role_btn.background = self.open_color
    self.warehouse_pick_role_btn.background = self.open_color
    self.warehouse_stock_role_btn.background = self.open_color
    self.testing_role_btn.background = self.open_color
    self.shipping_role_btn.background = self.selected_color
    self.all_inboxes_btn.background = self.open_color
    self.role_page_view_panel.visible = True
    self.messages_card.visible = False 

  def all_inboxes_view(self):
    self.role_page_view_panel.clear()
    self.teardown_role_btn.background = self.open_color
    self.id_role_btn.background = self.open_color
    self.warehouse_pick_role_btn.background = self.open_color
    self.warehouse_stock_role_btn.background = self.open_color
    self.testing_role_btn.background = self.open_color
    self.shipping_role_btn.background = self.selected_color
    self.all_inboxes_btn.background = self.open_color
    self.role_page_view_panel.visible = False
    self.messages_card.visible = True

  def teardown_btn_click(self, **event_args):
    self.teardown_view()

  def id_btn_click(self, **event_args):
    self.id_view()

  def wh_pick_btn_click(self, **event_args):
    self.wh_pick_view()

  def wh_stock_btn_click(self, **event_args):
    self.wh_stock_view()

  def testing_btn_click(self, **event_args):
    self.testing_view()

  def shipping_btn_click(self, **event_args):
    self.shipping_view()

  def all_inboxes_btn_click(self, **event_args):
    self.reset_messages()
    self.all_inboxes_view()
    
####### Messages (events and logic) ########################
  def init_messages(self):
    self.load_msgs_btn.enabled = False
    self.select_role_dropdown.items = anvil.server.call('get_full_roles_dropdown')
    self.select_role_dropdown.selected_value = '(Select Role)'
    self.inbox_clear_card.visible = False
    self.msg_inbox_repeater.visible = False

  def reset_messages(self):
    self.load_msgs_btn.enabled = False
    self.select_role_dropdown.selected_value = '(Select Role)'
    self.inbox_clear_card.visible = False
    self.msg_inbox_repeater.visible = False
  
  def select_role_dropdown_changed(self, **event_args):
    if self.select_role_dropdown.selected_value == '(Select Role)':
      self.load_msgs_btn.enabled = False
      self.reset_messages()
    else:
      self.load_msgs_btn.enabled = True

  def load_messages_btn_click(self, **event_args):
    self.load_msgs_btn.enabled = False #this will revert to true when the dropdown changes
    role = self.select_role_dropdown.selected_value
    messages = anvil.server.call('get_role_recieved_msgs', role)
    if not messages:
      self.no_messages_msg.text = f"{role} inbox is clear!"
      self.inbox_clear_card.visible = True
    else:
      self.msg_inbox_repeater.items = messages
      self.msg_inbox_repeater.visible = True
      self.inbox_clear_card.visible = False

  def refresh_messages(self, **event_args):
    self.load_messages_btn_click()
    