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
    # for component in self.fulfillment_repeating_panel.get_components():
    #   component.set_event_handler('x-change-focus-to-next', self.change_focus)
    # self.set_event_handler('x-order-picked', self.finish_order)
    self.fulfillment_repeating_panel.set_event_handler('x-abandon-order', self.fetch_new_order)
    self.fulfillment_repeating_panel.set_event_handler('x-change-focus-to-next', self.change_focus)
    self.current_user = anvil.server.call('get_user_full_name')
    self.current_role = anvil.server.call('get_user_role')
    self.current_table = anvil.server.call('get_current_table', self.current_user)
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
      if self.fulfillment_repeating_panel.get_components():
        self.fulfillment_repeating_panel.get_components()[0].item_scan_input.focus()


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

  def finish_table_click(self, **event_args):
    self.finish_table()


########## Order Card Logic & Events #############################
  # populates UI display from object attributes
  def set_order_card_content(self):
    # print("in order card content!")
    # [print(entry) for entry in self.current_order]
    self.order_no_output.text = self.current_order['order_no']
    self.table_output.content = self.current_table
    self.section_output.content = self.current_section
    self.customer_name_output.content = self.current_order['customer_name']
    self.price_output.content = self.current_order['total_price']
    self.no_items_output.content = self.current_order['total_items']
    self.fulfillment_repeating_panel.items = self.current_fulfillments 
    
    #set focus stuff
    self.component_idx = 0
    self.num_fulfillments = len(self.current_fulfillments )
    components = self.fulfillment_repeating_panel.get_components()
    components[self.component_idx].item_scan_input.focus()

   

  # changes focus to next card upon scan
  def change_focus(self, **event_args):
    #print('GOT THE EVENT HANDLER. In change focus. Event args are:', event_args)
    self.component_idx += 1
    all_picked = self.all_picked_check()
    if not all_picked:
      components = self.fulfillment_repeating_panel.get_components()
      components[self.component_idx].item_scan_input.focus()
    else:
      #print('The system recognized all orders have been picked')
      self.finish_order()
    


########## Lifecycle DB Functions ###############################
# Initializing a new table
  def get_new_table(self):
    n = Notification("Assign New Table.", title='Reserve Table', style='success')
    n.show()
    self.current_table = anvil.server.call('claim_table', 
                                           self.current_user)
    self.fetch_new_order()
    self.set_order_card_content()
    self.active_visibility()

#Fetching a New Order, also called for no-stocks
  def fetch_new_order(self, **event_args):
    n = Notification("Grabbing next order, just a moment.", style='info', timeout=5, title="New Order Loading")
    n.show()
    self.current_order = anvil.server.call_s('fetch_new_order', self.current_user)
    self.current_fulfillments = anvil.server.call_s('load_current_fulfillments', self.current_order['order_no'])
    self.current_section = anvil.server.call_s('link_order_to_table_section', 
                                             self.current_user, 
                                             str(self.current_order['order_no']), 
                                             self.current_table)
    if not self.current_section:
      n = Notification("Table complete! please take table to testing and press continue.", style='success')
      n.show()
      self.forced_finish_visibility()
      return None
    anvil.server.call_s('set_order_status', self.current_order['order_no'], 'Picking')

#Fetching Current Order (gracefully handle refresh)
  def get_current_state(self):
    n = Notification("Getting current session state, Just a moment please.", style='info', title="Preparing Session...", timeout=5)
    n.show()
    self.current_order = anvil.server.call_s('load_current_order', self.current_user)
    # print('in current state - Here is the current order')
    # [print(entry) for entry in self.current_order]
    if not self.current_order:
      self.fetch_new_order()
    self.current_section = self.current_order['section']
    self.current_fulfillments = anvil.server.call_s('load_current_fulfillments', 
                                                  self.current_order['order_no'])

#Checking for pick completion
  def all_picked_check(self):
    return self.component_idx == self.num_fulfillments



#Getting a new order once this order is done (responds to event from fulfillments)
  def finish_order(self):
    n = Notification(f"Order {self.current_order['order_no']} complete! Loading Next Open Order.", style='success', title="Order Complete!", timeout=5)
    n.show()
    anvil.server.call_s('finish_order_in_db', self.current_order['order_no'])
    self.fetch_new_order()
    self.set_order_card_content()

#Closing out a table and effectively reverting to a non-active session
  def finish_table(self):
    #self.get_current_state()
    n = Notification("Please wait. Closing table...", style='info')
    order_no = self.current_order['order_no']
    
    #close out any orders in the DB currently being picked
    if self.current_order['status'] == 'Picking':
      mid_pick = False
      for fulfillment in self.current_fulfillments:
        if fulfillment['status'] == 'Picked':
          mid_pick = True
      if mid_pick:
        response = anvil.alert(f"You are currently picking order {order_no} \
        which must be closed before closing this table.", buttons=['MOVE TO HOLDING', 'FINISH PICK'],
                              title="Unprocessed Orders", large=True)
        if response == 'MOVE TO HOLDING':
          hold_table, hold_section = anvil.server.call('get_next_open_holding_area')
          confirm = anvil.alert(f'Ok to move order {order_no} to Holding Area? Table: {hold_table}, Section: {hold_section}', buttons=['YES', 'NO'], 
                                title= f'Move {order_no}to Holding Area')
          if confirm:
            anvil.server.call('move_order_to_holding_area', order_no, hold_table, hold_section)
    #close out the table itself too
    n = Notification("Table complete! please take table to testing and press continue.", style='success', title='Move Table to Testing', timeout=5)
    n.show()
    anvil.server.call_s('close_table')
    #TODO: refresh page to reset to empty state
    pass
    