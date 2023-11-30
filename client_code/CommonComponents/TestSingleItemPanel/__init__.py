from ._anvil_designer import TestSingleItemPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class TestSingleItemPanel(TestSingleItemPanelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.item_id_label.text = self.item['item_id']
    self.set_event_handler('x-mark-passed-item', self.mark_passed)
    self.set_event_handler('x-mark-failed-item', self.mark_failed)
    self.set_event_handler('x-test-needs-attention', self.mark_needs_attention)
    

    # Any code you write here will run before the form opens.

# Handle pass/fail updates on the repeater
  def mark_passed(self, item_id, **event_args):
    if item_id == self.item['item_id']:
      self.waiting_label.visible = False
      self.passed_label.visible = True
      self.failed_label.visible = False
    print('hit mark passed in repeater')

  def mark_failed(self, item_id, **event_args):
    if item_id == self.item['item_id']:
      self.waiting_label.visible = False
      self.passed_label.visible = False
      self.failed_label.visible = True
    print('hit mark failed in repeater')

  def mark_needs_attention(self, item_id, **event_args):
    if item_id == self.item['item_id']:
      self.waiting_label.visible = False
      self.passed_label.visible = False
      self.failed_label.visible = True
    print('hit mark needs attention in repeater')