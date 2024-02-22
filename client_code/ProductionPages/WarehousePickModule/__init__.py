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
  def __init__(self, current_user, current_role, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # for component in self.fulfillment_repeating_panel.get_components():
    #   component.set_event_handler('x-change-focus-to-next', self.change_focus)
    # self.set_event_handler('x-order-picked', self.finish_order)
    self.fulfillment_repeating_panel.set_event_handler('x-change-focus-to-next', self.change_focus)
    self.fulfillment_repeating_panel.set_event_handler('x-wh-no-stock', self.move_to_holding_no_stock)
    self.fulfillment_repeating_panel.set_event_handler('x-wh-needs-attention', self.move_to_holding_needs_attention)
    self.current_user = current_user
    self.current_role = current_role
    self.current_table = anvil.server.call('get_current_table', self.current_user)
    self.current_order = None
    self.current_fulfillments = None
    self.current_section = None
    self.begin_tray_btn.visible = False
    self.tray_mode = False #processing orders that were resolved
    
    if not self.current_table:
      self.initial_visibility()
      self.get_table_dropdown()
    else:
      self.get_current_state() #sets order and fulfillments
      self.set_order_card_content()
      self.active_visibility()
      if self.fulfillment_repeating_panel.get_components():
        self.fulfillment_repeating_panel.get_components()[0].item_scan_input.focus()

  # #### Needs Attention Inits ######
    self.dept_output.content = 'Warehouse'
    self.refresh_needs_attention_area()


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
    n = Notification('Your Table is full. Please close this table and grab a new one.', 
                     title="Table Full Notice", 
                     style='warning', 
                     timeout=3)
    self.select_table_card.visible = False
    self.active_order_card.visible = False
    self.finish_table_card.visible = True
    self.na_spacer.visible = False
    self.na_card.visible = False
    
########## Select Table Card Logic & Events ############
  def get_table_dropdown(self):
    picking_trays = anvil.server.call('get_pending_trays', "Picking")
    if not picking_trays:
      open_tables_list = anvil.server.call('get_open_tables', status='Open')
      self.table_dropdown.items = open_tables_list
      self.table_dropdown.selected_value = '(Select Table)'
      self.begin_table_btn.visible = False
    else:
      n = Notification("Previous Orders have been resolved. Please select a tray to continue.", 
                       style='warning', timeout=5, title='Tray Processing')
      n.show()
      self.table_dropdown.items = picking_trays
      self.table_dropdown.selected_value = '(Select Table)'
      self.begin_table_btn.visible = False
      self.tray_mode = True

  def select_table_dropdown_change(self, **event_args):
    if self.table_dropdown.selected_value == '(Select Table)':
      self.begin_table_btn.visible = False
    else:
      if self.tray_mode:
        self.begin_tray_btn.visible = True
      else:
        self.begin_table_btn.visible = True

  def begin_table_btn_click(self, **event_args):
    self.get_new_table()

  def finish_table_click(self, **event_args):
    self.finish_table()
    self.get_table_dropdown()
    self.initial_visibility()
    


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
    self.num_fulfillments = len(self.current_fulfillments)
    components = self.fulfillment_repeating_panel.get_components()
    components[self.component_idx].item_scan_input.focus()

   

  # changes focus to next card upon scan
  def change_focus(self, **event_args):
    #print('GOT THE EVENT HANDLER. In change focus. Event args are:', event_args)
    self.component_idx += 1
    print(self.component_idx)
    all_picked = self.all_picked_check()
    if not all_picked:
      components = self.fulfillment_repeating_panel.get_components()
      components[self.component_idx].item_scan_input.focus()
    else:
      print('The system recognized all orders have been picked')
      self.finish_order()
    


########## Lifecycle DB Functions ###############################
# Initializing a new table
  def get_new_table(self):
    n = Notification("Claiming new table...",style='success')
    self.current_table = anvil.server.call_s('claim_table', 
                                           self.current_user, 
                                             "Open", 
                                             "Picking")
    self.fetch_new_order()
    # self.set_order_card_content()
    # self.active_visibility()

#Fetching a New Order, also called for no-stocks
  def fetch_new_order(self, **event_args):
    n_1 = Notification('Finding next section...', timeout=1)
    self.current_section = anvil.server.call('get_next_open_section', self.current_table)
    if not self.current_section:
      n = Notification("Table complete! please take table to testing and press continue.", style='success')
      n.show()
      self.forced_finish_visibility()
      return None
    else:
      n = Notification("Grabbing next order, just a moment.", style='info', timeout=2, title="New Order Loading")
      n.show()
      self.current_order = anvil.server.call_s('fetch_new_order', self.current_user)
      self.current_fulfillments = anvil.server.call_s('load_current_fulfillments', self.current_order['order_no'])
      self.current_section = anvil.server.call_s('link_order_to_table_section', 
                                              self.current_user, 
                                              str(self.current_order['order_no']), 
                                              self.current_table)
  
      anvil.server.call_s('set_order_status', self.current_order['order_no'], 'Picking')
      self.set_order_card_content()
      self.active_visibility()

#Fetching Current Order (gracefully handle refresh)
  def get_current_state(self):
    n = Notification("Getting current session state, Just a moment please.", style='info', title="Preparing Session...", timeout=2)
    n.show()
    self.current_order = anvil.server.call_s('load_current_order', self.current_user, status='Picking')
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
    anvil.server.call_s('close_order_in_db_sync', 
                        self.current_user, 
                        self.current_role, 
                        self.current_order['order_no'], 
                        'Picked')
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

      # return the currently displayed order to new status, if it exists
      anvil.server.call('force_close_pick_table', self.current_user)
      
    #close out the table itself too
    n = Notification("Table complete! please take table to testing and press continue.", style='success', title='Move Table to Testing', timeout=5)
    n.show()
    anvil.server.call_s('close_table', self.current_table, status='Testing')
    #TODO: refresh page to reset to empty state
    pass

##### Needs Attention Panel ############
  #responds to fulfillment repeater buttons
  def move_to_holding_no_stock(self, sku, fulfillment_id, **event_args):
    print("Made it to the move_to_holding event.")
    confirm = anvil.alert(f"Confirm: {sku} is not in stock?", 
                          buttons=['YES', 'CANCEL'], 
                          large=True, Title = "Out of Stock?")
    if confirm == "YES":
      n = Notification("updating...", style='info')
      n.show()
      anvil.server.call('set_fulfillment_status', fulfillment_id, 'No Stock')
      open_section = anvil.server.call('get_next_open_section', 'WHH1') #hardcoded table name here
      move_item = anvil.alert(f"Please move Order to Holding Table {open_section['table']}, \
      Section: {open_section['section']}", buttons=['OK'], large=True,
                title="Move Item to Holding.")
      #Message for Management
      # print("user", self.current_user)
      # print("role", self.current_role)
      # print("sku", sku)
      # print("order", self.current_order)
      anvil.server.call('create_message', 
                        self.current_user,
                        self.current_role, 
                        'Management',
                        #'Test Message for holding',
                       f'NEEDS ATTENTION: {sku} marked as out of stock in warehouse. Blocking order {self.current_order["order_no"]}.',
                       sku)
      #Order to Holding Area
      anvil.server.call('move_order_to_holding_area', self.current_order['order_no'],
                       open_section['table'], open_section['section'])
      #Start fresh
      self.fetch_new_order()      
      self.refresh_needs_attention_area()

  def move_to_holding_needs_attention(self, sku, fulfillment_id, **event_args):
    print("Made it to the move_to_holding event - Needs Attention.")
    confirm = anvil.alert(f"Confirm: {sku} needs management attention?", 
                          buttons=['YES', 'CANCEL'], 
                          large=True, Title = "Needs attention?")
    if confirm == "YES":
      n = Notification("updating...", style='info')
      n.show()
      anvil.server.call('set_fulfillment_status', fulfillment_id, 'Needs Attention')
      open_section = anvil.server.call('get_next_open_section', 'WHH1') #hardcoded table name here
      move_item = anvil.alert(f"Please move Order to Holding Table {open_section['table']}, \
      Section: {open_section['section']}", buttons=['OK'], large=True,
                title="Move Item to Holding.")
      #Message for Management
      # print("user", self.current_user)
      # print("role", self.current_role)
      # print("sku", sku)
      # print("order", self.current_order)
      anvil.server.call('create_message', 
                        self.current_user,
                        self.current_role, 
                        'Management',
                        #'Test Message for holding',
                       f'NEEDS ATTENTION: {sku} marked as needs attention - other in the Warehouse. Blocking order {self.current_order["order_no"]}.',
                       sku)
      #Order to Holding Area
      anvil.server.call('move_order_to_holding_area', self.current_order['order_no'],
                       open_section['table'], open_section['section'])
      #Start fresh
      self.fetch_new_order()      
      self.refresh_needs_attention_area()

  def refresh_needs_attention_area(self):
    self.needs_attention_orders = anvil.server.call('get_needs_attention_orders', 
                                                    holding_type='Warehouse Hold', 
                                                    dept='Warehouse')
    
    if not self.needs_attention_orders:
      self.num_na_orders.content = 0
      self.no_pending_panel.visible = True
      self.needs_attention_repeater.visible = False
    else:
      self.num_na_orders.content = len(self.needs_attention_orders)
      self.no_pending_panel.visible = False
      self.needs_attention_repeater.visible = True
      self.needs_attention_repeater.items = self.needs_attention_orders
  
######### Handling for Tray Mode ################
  def begin_tray_btn_click(self, **event_args):
    self.current_table = self.table_dropdown.selected_value
    anvil.server.call('reserve_tray', self.current_table)
    self.get_current_state() #should give me the order and fulfillments
    #check if it's already done
    tray_complete = anvil.server.call('tray_complete', self.current_order)
    if tray_complete:
      self.finish_table()
    else:
      self.fulfillment_repeating_panel.items = self.current_fulfillments

  def stock_mode_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    from ..WarehouseStockModule import WarehouseStockModule
        
    get_open_form().content_panel.clear()
    get_open_form().content_panel.add_component(WarehouseStockModule(current_user=self.current_user, current_role=self.current_role),
                                        full_width_row=True)
    pass


########## Additional Functionality - Already Packed ##############
  def mark_finished_btn_click(self, **event_args):
    confirm = anvil.alert(f"Ok to mark order {self.current_order['order_no']} as already complete? This is not reversible.", 
                large=True, buttons=['MARK PACKED', 'CANCEL'], dismissible=False)
    if confirm == 'MARK PACKED':
      order_no = self.current_order['order_no']
      anvil.server.call('close_order_in_db', 
                        self.current_user, 
                        self.current_role, 
                        self.current_order['order_no'], 
                        status='Sold')
      anvil.server.call('pack_order_and_fulfillments', #probably need to convert to bk
                        user=self.current_user, 
                        role=self.current_role, 
                        order_no=order_no)
      anvil.server.call('remove_order_from_table', 
                        order_no=order_no)
      n = Notification(f"Order {self.current_order} marked as complete!", style='success')
      n.show()
      self.fetch_new_order()