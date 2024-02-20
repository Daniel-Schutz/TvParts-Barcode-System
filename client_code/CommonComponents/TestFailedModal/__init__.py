from ._anvil_designer import TestFailedModalTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class TestFailedModal(TestFailedModalTemplate):
  def __init__(self, item_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.test_note_header = f"Failed QA Notes: Item {item_id}"

  def mark_failed_btn_click(self, **event_args):
    if not self.note_input.text:
      n = Notification("You must enter a failure note!", style='danger')
      n.show()
      return None
    else:
      n = Notification(f"Failure Note Recorded for item {item_id}", style='success')
      n.show()
      self.raise_event('x-close-alert', value=self.note_input.text)

  def cancel_btn_click(self, **event_args):
      self.raise_event('x-close-alert', value="Cancelled")   
      
