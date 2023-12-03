from ._anvil_designer import TestingModuleTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

import json

class TestingModule(TestingModuleTemplate):
  def __init__(self, current_user, current_role, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    #self.fulfillments_repeater.set_event_handler('x-change-focus-to-next', self.change_focus)
    #self.fulfillments_repeater.set_event_handler('x-ts-needs-attention', self.move_to_holding)
    self.current_user = current_user
    self.current_role = current_role
    self.current_table = anvil.server.call('get_current_table', self.current_user)
    self.current_order = None
    self.current_fulfillments = None
    self.current_section = None
    self.begin_tray_btn.visible = False
    self.tray_mode = False #processing orders that were resolved
    self.this_item_id = None
    self.target_f = None
    
    if not self.current_table:
      self.initial_visibility()
      self.get_table_dropdown()
    else:
      self.get_current_state() #sets order and fulfillments
      self.init_order_card_content()
      self.active_visibility()
      if self.fulfillments_repeater.get_components():
        self.item_scan_input.focus()

  # #### Needs Attention Inits ######
    self.dept_output.content = 'Testing'
    self.refresh_needs_attention_area()

######## Visibility Helpers ###############
  def initial_visibility(self):
    self.select_table_card.visible = True
    self.active_order_card.visible = False
    self.finish_table_card.visible = False
    self.na_spacer.visible = False
    self.na_card.visible = False
    self.begin_table_btn.visible = False
    self.begin_tray_btn.visible = False

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

  def enable_buttons(self):
    self.failed_btn.enabled = True
    self.passed_btn.enabled = True
    self.needs_attention_btn.enable = True
    
########## Select Table Card Logic & Events ############
  def get_table_dropdown(self):
    #picking_trays = anvil.server.call('get_pending_test_trays')
    picking_trays = False
    if not picking_trays:
      testing_tables_list = anvil.server.call('get_open_tables', status='Testing')
      self.table_dropdown.items = testing_tables_list
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

# ######### Update the Order Card #######################
  def init_order_card_content(self):
    # This is a "blank card", before scans
    self.order_headline.text = f"Order: {self.current_order['order_no']}"
    self.table_output.content = self.current_table
    self.section_output.content = self.current_section
    self.product_img_output.source = None
    self.failed_btn.enabled = False
    self.passed_btn.enabled = False
    self.needs_attention_btn.enabled = False

    # set focus
    self.item_scan_input.focus()


# ######### Lifecycle DB Helper Functions ########################
  def update_fulfillments(self):
    self.current_fulfillments = anvil.server.call_s('load_current_fulfillments', 
                                                  self.current_order['order_no'])
    self.fulfillments_repeater.items = self.current_fulfillments

  def check_complete(self):
    complete = True
    for f in self.current_fulfillments:
      if f['status'] != 'Tested':
        complete = False
        break
    if complete:
      self.close_order()
      more_orders_this_table = self.fetch_new_order()
      self.clear_scan_btn_click()
      if not more_orders_this_table:
        return None #Stops the system from generating a new order card
      self.init_order_card_content()
      self.item_scan_input.focus()
    else:
      self.update_fulfillments()
      self.clear_scan_btn_click()
      

########## Lifecycle DB Functions ###############################
# Initializing a new table
  def claim_selected_table(self):
    selected_table = self.table_dropdown.selected_value
    n = Notification("Claiming table...", style='success')
    self.current_table = anvil.server.call('claim_selected_table', 
                                           user=self.current_user, 
                                           table_no=selected_table)
    #self.fetch_new_order()

  # def get_new_table(self):
  #   n = Notification("Claiming new table...", style='success')
  #   self.current_table = anvil.server.call_s('claim_table', 
  #                                           self.current_user, 
  #                                             "Testing")
  #   self.fetch_new_order()

#Fetching Current Order (gracefully handle refresh)
  def get_current_state(self):
    n = Notification("Getting current session state, Just a moment please.", style='info', title="Preparing Session...", timeout=5)
    n.show()
    self.current_order = anvil.server.call_s('load_current_order', self.current_user, status='Testing')
    if not self.current_order:
      self.fetch_new_order()
    self.current_section = self.current_order['section']
    self.update_fulfillments()

#Fetching a New Order after completion of testing, or problems
  def fetch_new_order(self, **event_args):
    n = Notification("Grabbing next order, just a moment.", style='info', timeout=5, title="New Order Loading")
    n.show()
    print(self.current_table)
    self.current_order = anvil.server.call_s('get_next_order', 
                                             self.current_user, 
                                             self.current_table, 
                                             "Picked", 
                                             "Testing")
    if not self.current_order:
      n = Notification("Table complete! please take table to Shipping and press continue.", style='success')
      n.show()
      self.forced_finish_visibility()
      print("no open sections in fetch new order")
      return None
    self.current_section = self.current_order['section']
    self.update_fulfillment_display()
    return "Continue"

# Update the fulfillments after a scan has been marked
  def update_fulfillment_display(self):
    self.current_fulfillments = anvil.server.call_s('load_current_fulfillments', self.current_order['order_no'])
    self.fulfillments_repeater.items = self.current_fulfillments

# This whole system is scan driven. self.target_f is the fulfillment linked to the scanned item
  def item_scan_input_pressed_enter(self, **event_args):
    scan_dict = json.loads(self.item_scan_input.text)
    self.this_item_id = scan_dict['item_id']
    for f in self.current_fulfillments:
      if f['item_id'] == self.this_item_id:
        self.target_f = f
        break
    if not self.target_f:
      n = Notification(f"Scanned item {self.this_item_id} is not a part of Order {self.current_order['order_no']}. Please try again.", 
                       title='Item not in Order',
                      style='warning')
      n.show()
      self.item_scan_input.text = None
    else:
      self.sku_output.content = self.target_f['sku']
      self.name_content.content = self.target_f['product_name']
      self.item_id_output.content = self.target_f['item_id']
      self.enable_buttons()
      self.product_img_output.source = anvil.server.call_s('get_img_source_from_sku', 
                                                           sku=self.target_f['sku'])
      

# Close Orders when they are complete
  def close_order(self):
    order_no = self.current_order['order_no']
    anvil.server.call('close_order_in_db', 
                      order_no=order_no, 
                      status='Tested')

# ##### Button Events - Initial Visibility #############
  def begin_table_btn_click(self, **event_args):
    self.claim_selected_table()
    self.get_current_state()
    self.init_order_card_content()
    self.active_visibility()
    pass

###### Button Events - Active Visibility #############
  def clear_scan_btn_click(self, **event_args):
    self.item_scan_input.text = None
    self.sku_output.content = None
    self.name_content.content = None
    self.item_id_output.content = None
    self.failed_btn.enabled = False
    self.needs_attention_btn.enabled = False
    self.passed_btn.enabled = False
    self.target_f = None
    self.item_scan_input.focus()

  def passed_btn_click(self, **event_args):
    self.fulfillments_repeater.raise_event_on_children('x-mark-passed-item', 
                                                       item_id=self.target_f['item_id'])

    anvil.server.call('set_f_status_by_item_id', 
                      item_id=self.target_f['item_id'], 
                      status='Tested')
    # self.update_fulfillments()
    self.check_complete()
    pass
    
  def needs_attention_btn_click(self, **event_args):
    self.fulfillments_repeater.raise_event_on_children('x-test-needs-attention', 
                                                    item_id=self.target_f['item_id'])

  def failed_btn_click(self, **event_args):
    self.fulfillments_repeater.raise_event_on_children('x-mark-failed-item', 
                                                       item_id=self.target_f['item_id'])
    self.move_to_holding_failed(item_id=self.target_f['item_id'], 
                                fulfillment_id=self.target_f['fulfillment_id'])
    
    pass #This kicks off the whole needs attention flow, so we'll come back to it

  def finish_table_btn_click(self, **event_args):
    n = Notification("Closing Table, please wait...")
    anvil.server.call('close_table', self.current_table, status='Shipping')
    self.initial_visibility()
    self.get_table_dropdown()


##### Needs Attention Panel ############
  #responds to fulfillment repeater buttons
  def move_to_holding_failed(self, item_id, fulfillment_id, **event_args):
    print("Made it to the move_to_holding event.")
    confirm = anvil.alert(f"Confirm item {item_id} does not pass testing", 
                          buttons=['YES', 'CANCEL'], 
                          large=True, Title = "Failed Testing?")
    if confirm == "YES":
      anvil.server.call('set_fulfillment_status', fulfillment_id, 'Needs Replaced')
      open_section = anvil.server.call('get_next_open_section', 'TH1') #hardcoded table name here
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
                       f'FAILED TEST: Item {item_id} marked as failed at testing. Notice has been sent to warehouse to replace. Blocking order {self.current_order["order_no"]}.',
                       item_id)
      #Order to Holding Area
      anvil.server.call('move_order_to_holding_area', self.current_order['order_no'],
                       open_section['table'], open_section['section'])
      #Start fresh
      self.fetch_new_order()
      self.init_order_card_content()
      self.needs_attention_orders = anvil.server.call('get_needs_attention_items', 
                                                      holding_type='Testing Hold', 
                                                      dept='Testing')
      self.num_na_orders.output = len(self.needs_attention_orders)
      self.refresh_needs_attention_area()

  def refresh_needs_attention_area(self):
    self.needs_attention_orders = anvil.server.call('get_needs_attention_orders', 
                                                    holding_type='Testing Hold', 
                                                    dept='Testing')
    if not self.needs_attention_orders:
      self.num_na_orders.content = 0
      self.no_pending_panel.visible = True
      self.needs_attention_repeater.visible = False
    else:
      self.num_na_orders.content = len(self.needs_attention_orders)
      self.no_pending_panel.visible = False
      self.needs_attention_repeater.visible = True
      self.needs_attention_repeater.items = self.needs_attention_orders
  