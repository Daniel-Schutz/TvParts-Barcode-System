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
    self.replace_item_id_output.content = self.prev_item_id
    #remember that dropdown items are tuples
    self.replacement_reason_dropdown.items = [('(Select Reason)', '(Select Reason)'),
                                              ("Needs Fixed", "Needs Fixed"), 
                                              ('Restocked', 'Restocked'), 
                                              ('Tossed', 'Tossed')]
    self.new_item_scan_input.focus()

    # Any code you write here will run before the form opens.

######### Validate before replacing ############################
  def validate_item_scan_input(self):
    try:
      scan_dict = json.loads(self.new_item_scan_input.content)
      new_item_id = scan_dict['item_id']
      self.

######### Handle Button Click Logic on Done ####################
  def cancel_btn_click(self, **event_args):
    self.raise_event('x-close-alert', value='CANCELLED')

