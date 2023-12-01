from ._anvil_designer import NeedsAttentionReplaceModalTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

import json

class NeedsAttentionReplaceModal(NeedsAttentionReplaceModalTemplate):
  def __init__(self, item_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.prev_item_id = item_id
    self.current_user = anvil.server.call('get_user_full_name')
    self.user_role = anvil.server.call('get_user_role')
    self.replace_item_id_output.content = self.prev_item_id
    self.f_id = anvil.server.call('get_f_id_from_item_id', item_id)
    self.scan_item_input_panel.visible = False
    self.new_item_id_panel.visible = False
    self.done_btn.enabled = False
    #remember that dropdown items are tuples
    self.replacement_reason_dropdown.items = [('(Select Reason)', '(Select Reason)'),
                                              ("Fixed", "Fixed"), 
                                              ('Restocked', 'Restocked'), 
                                              ('Tossed', 'Tossed')]
    self.replacement_reason_dropdown.selected_value = '(Select Reason)'
    self.new_item_scan_input.focus()

    # Any code you write here will run before the form opens.

######### Visibility Logic ##########################
  def replacement_dropdown_changed(self, **event_args):
    if self.replacement_reason_dropdown.selected_value == '(Select Reason)':
      self.scan_item_input_panel.visible = False
    else:
      self.scan_item_input_panel.visible = True
  

######### Validate before replacing ############################
  def validate_item_scan_input(self):
    try:
      scan_dict = json.loads(self.new_item_scan_input.content)
      new_item_id = scan_dict['item_id']
      self.new_item_id_output.content = new_item_id
      self.new_item_scan_input.enabled = False
      self.new_item_id_panel.visible = True
      self.done_btn.enabled = True
      return 'Valid'
    except:
      n = Notification("Scan is not a valid item!", style='danger')
      n.show()
      self.new_item_scan_input.enabled = True
      self.new_item_scan_input.focus()
      return "Invalid"

######### Handle Button Click Logic ####################
  def cancel_btn_click(self, **event_args):
    self.raise_event('x-close-alert', value='CANCELLED')

  def clear_scan_btn_click(self, **event_args):
    self.new_item_id_output.content = None
    self.new_item_id_panel.visible = False
    self.done_btn.enabled = False
    self.new_item_scan_input.enabled = True
    self.new_item_scan_input.focus()

### Here is the one that actually does something
  def done_btn_click(self, **event_args):
    destiny = self.replacement_reason_dropdown.selected_value
    new_item_id = self.new_item_id_output.content
    anvil.server.call('replace_item_on_fulfillment', 
                      self.prev_item_id, 
                      new_item_id, 
                      destiny, 
                      self.current_user, 
                      self.user_role, 
                      'Picked')
    self.raise_event('x-close-alert', value=new_item_id)
    


