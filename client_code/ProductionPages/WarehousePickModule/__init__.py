from ._anvil_designer import WarehousePickModuleTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...CommonComponents import CommonFunctions as cf
from datetime import datetime

class WarehousePickModule(WarehousePickModuleTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.set_event_handler('x-order-picked', finish_order)
    self.current_user = anvil.server.call('get_user_full_name')
    self.current_table = anvil.server.call('get_current_table')
    self.current_order = None
    self.current_fulfillments = None
    self.current_section = None
    if not self.current_table:
      self.initial_visibility()
      self.get_table_dropdown()
    else:
      self.get_current_state() #sets order and fulfillments
      self.set_order_card_content()
      self.active_visibility()


########### Visibility Helper Functions ####################
  def initial_visibility(self):
    self.select_table_card.visible = True
    self.active_order_card.visible = False
    self.finish_table_card.visible = False
    self.na_spacer.visible = False
    self.na_card.visible = False

  def active_visibility(self):
    self.select_table_card.visible = False
    self.active_order_card.visible = True
    self.finish_table_card.visible = True
    self.na_spacer.visible = True
    self.na_card.visible = True

  def forced_finish_visibility(self):
    self.select_table_card.visible = False
    self.active_order_card.visible = False
    self.finish_table_card.visible = True
    self.na_spacer.visible = False
    self.na_card.visible = False
    
########## Select Table Card Logic & Events ############
  def get_table_dropdown(self):
    open_tables_list = anvil.server.call('get_open_tables')
    self.table_dropdown.items = open_tables_list
    self.table_dropdown.selected_value = '(Select Table)'
    self.begin_table_btn.visible = False

  def select_table_dropdown_change(self, **event_args):
    if self.table_dropdown.selected_value == '(Select Table)':
      self.begin_table_btn.visible = False
    else:
      self.begin_table_btn.visible = True

  def begin_table_btn_click(self, **event_args):
    self.get_new_table()


########## Order Card Logic & Events #############################
  #populates UI display from object attributes
  def set_order_card_content(self):
    self.order_no_output.content = self.current_order['order_no']
    self.table_output.content = self.current_table
    self.section_output.content = self.current_section
    self.customer_name_output.content = self.current_order['customer_name']
    self.price_output.content = self.current_order['total_price']
    self.no_items_output.content = self.current_order['total_items']
    self.fulfillment_repeating_panel.items = self.current_fulfillments


########## Lifecycle DB Functions ###############################
# Initializing a new table
  def get_new_table(self):
    self.current_table = anvil.server.call('claim_table', 
                                           self.current_user)
    self.fetch_new_order()
    self.set_order_card_content()
    self.active_visibility()

#Fetching a New Order
  def fetch_new_order(self):
    self.current_order, self.current_fulfillments = anvil.server.call('fetch_new_order')
    self.current_section = anvil.server.call('link_order_to_table_section', 
                                             self.current_user, 
                                             self.current_order['order_no'], 
                                             self.current_table)
    if not self.current_section:
      n = Notification("Table complete! please take table to testing and press continue.", style='success')
      n.show()
      self.forced_finish_visibility()
    anvil.server.call('set_order_status', self.current_order['order_no'], 'Picking')

#Fetching Current Order (gracefully handle refresh)
  def get_current_state(self):
    self.current_order, self.current_fulfillments = \
    anvil.server.call('load_current_order')

#Getting a new order once this order is done (responds to event from fulfillments)
  def finish_order(self):
    anvil.server.call('finish_order_in_db', self.current_order['order_no'])
    self.fetch_new_order()
    self.set_order_card_content()

#Closing out a table and effectively reverting to a non-active session
  def finish_table(self):
    #close out any open orders in the DB
    #if there are orders that are half picked, raise an alert to move current order to
    #  needs attention
    #close out the table itself too
    #refresh page to reset to empty state
    pass
    
    
