from ._anvil_designer import ControlPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ControlPanel(ControlPanelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.select_user_dropdown.items = anvil.server.call('get_users_dropdown')
    self.select_user_dropdown.selected_value = '(Select User)'
    self.select_role_dropdown.items = anvil.server.call('get_full_roles_dropdown')
    self.select_role_dropdown.selected_value = '(Select Role)'
    self.assign_new_role_btn.enabled = False
    self.admin_passcode_input.text = anvil.server.call('get_admin_passcode')

    # Any code you write here will run before the form opens.

########### Change User Role Logic (Including Events) #############
  def on_assigned_user_change(self, **event_args):
    if self.select_user_dropdown.selected_value == '(Select User)':
      return None
    else:
      if self.select_role_dropdown.selected_value == '(Select Role)':
        return None
      else:
        self.assign_new_role_btn.enabled = True

  def on_assigned_role_change(self, **event_args):
    if self.select_role_dropdown.selected_value == '(Select Role)':
      return None
    else:
      if self.select_user_dropdown.selected_value == '(Select User)':
        return None
      else:
        self.assign_new_role_btn.enabled = True

  def assign_role_btn_click(self, **event_args):
    role = self.select_role_dropdown.selected_value
    user = self.select_user_dropdown.selected_value
    anvil.server.call('set_user_to_role', 
                      user, 
                      role)
    n = Notification(f"New role {role} assigned to {user}!", 
                     style='success', 
                     title='New Role Assigned')
    #Reset menu
    self.select_role_dropdown.selected_value = '(Select Role)'
    self.select_user_dropdown.selected_value = '(Select User)'
    self.assign_new_role_btn.enabled = False

########### Manage Open Order Logic (Including Events) ###############
  def refresh_open_orders_btn_click(self, **event_args):
    confirm = anvil.alert("Refreshing all open orders will grab all open orders within the last 7 days. Ok to Proceed?",
                          title="Refresh Open Orders (Prepare Pick Batch)", 
                          buttons=['PULL NEW ORDERS', 'CANCEL'], large=True)
    if confirm == 'PULL NEW ORDERS':
      anvil.server.call('refresh_orders_and_fulfillment')
      n = Notification("""Order processing has started in the background. Please allow up to 5 minutes for the
      system to finish batch updating.""", 
                       title="Pulling New Orders", 
                       style='success', 
                       timeout=5)
      n.show()

  def clear_open_order_btn_click(self, **event_args):
    confirm = anvil.alert("""Clearing all Orders and Fulfillments will also reset all Tables, Trays, and Holding Areas.
    There MUST be no orders processing, and needs attention area MUST be empty to continue. 
    Orders remaining in these areas may leave the system in an unrecoverable state.\n\nPLEASE PROCEED WITH CAUTION!""",
                          title="Clear all orders?", 
                          buttons=['CLEAR SYSTEM ORDERS', 'CANCEL'], large=True)
    if confirm == 'CLEAR SYSTEM ORDERS':
      anvil.server.call('clear_all_orders_fulfillments')
      n = Notification("""Clearing all orders in the background. Please allow up to 30 seconds to complete.""", 
                       title="Clearing Orders", 
                       style='success', 
                       timeout=5)
      n.show()

######## Set Admin Passcode Logic (Including Events) #########
  def set_admin_pass_btn_click(self, **event_args):
    if not self.admin_passcode_input.text:
      n = Notification("You must type something in the passcode area first!", 
                       style='warning', timeout=1)
      n.show()
    else:
      anvil.server.call('set_admin_passcode', passcode)
      n = Notification("Passcode updated!", 
                       style='success', timeout=2)
      n.show()

########## set bin mode logic (including events) #########
  def setup_bin_mode_dropdown(self):
    dropdown_items = [('Select', 'Select'), ('Auto', 'Auto')]
    self.bin_mode_dropdown.items = dropdown_items
    self.bin_mode_dropdown.selected_value = anvil.server.call('get_bin_stock_mode')

  def bin_stock_submit_btn_click(self, **event_args):
    confirm = anvil.alert("Change Warehouse Stock Mode?",
                          title="Confirm - Set Warehouse Stock Mode", 
                          buttons=['SET MODE', 'CANCEL'], large=True)
    if confirm == 'SET MODE':
      mode = self.bin_mode_dropdown.selected_value
      anvil.server.call('set_bin_stock_mode', mode)
      n = Notification("Bin Stock Mode updated!", 
                       style='success', timeout=2)
      n.show()

