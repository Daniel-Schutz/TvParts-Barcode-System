from ._anvil_designer import TestingModuleTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class TestingModule(TestingModuleTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.fulfillment_repeating_panel.set_event_handler('x-change-focus-to-next', self.change_focus)
    self.fulfillment_repeating_panel.set_event_handler('x-ts-needs-attention', self.move_to_holding)
    self.current_user = anvil.server.call('get_user_full_name')
    self.current_role = anvil.server.call('get_user_role')
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

########## Select Table Card Logic & Events ############
  def get_table_dropdown(self):
    picking_trays = anvil.server.call('get_pending_test_trays')
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


########## Lifecycle DB Functions ###############################
# Initializing a new table
  def get_new_table(self):
    n = Notification("Claiming new table...",style='success')
    self.current_table = anvil.server.call_s('claim_table', 
                                           self.current_user, 
                                             "Testing")
    self.fetch_new_order()

#Fetching Current Order (gracefully handle refresh)
  def get_current_state(self):
    n = Notification("Getting current session state, Just a moment please.", style='info', title="Preparing Session...", timeout=5)
    n.show()
    self.current_order = anvil.server.call_s('load_current_order', self.current_user, status='Testing')
    if not self.current_order:
      self.fetch_new_order()
    self.current_section = self.current_order['section']
    self.current_fulfillments = anvil.server.call_s('load_current_fulfillments', 
                                                  self.current_order['order_no'])
