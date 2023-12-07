from ._anvil_designer import RecallItemModalTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

import json

class RecallItemModal(RecallItemModalTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.cancel_btn.visible = False
    self.get_box_btn.visible = False
    self.clear_btn.visible = False
    self.scan_input.focus()

    # Any code you write here will run before the form opens.

  def on_scan_pressed_enter(self, **event_args):
    self.cancel_btn.visible = True
    self.get_box_btn.visible = True
    self.clear_btn.visible = True
    self.scan_input.enabled = False

  def clear_btn_click(self, **event_args):
    self.cancel_btn.visible = False
    self.get_box_btn.visible = False
    self.clear_btn.visible = False
    self.scan_input.text = None
    self.scan_input.enabled
    self.scan_input.focus()

  def cancel_btn_click(self, **event_args):
    self.raise_event('x-close-alert', value=None)

  def recall_btn_click(self, **event_args):
    item_id = json.loads(self.scan_input.text)['item_id']
    self.raise_event('x-close-alert', value=item_id)
    