from ._anvil_designer import CreateSupplierModalTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class CreateSupplierModal(CreateSupplierModalTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def clear_btn_click(self, **event_args):
    self.supplier_name_input.text = None
    self.supplier_name_input.focus()

  def cancel_btn_click(self, **event_args):
    self.raise_event('x-close-alert', value=None)

  def create_supplier_click(self, **event_args):
    if not self.supplier_name_input.text:
      n = Notification("You must enter a value to create a supplier!", 
                       title="Error: No Input", style='danger')
      n.show()
      self.supplier_name_input.focus()
      return None
    else:
      self.raise_event('x-close-alert', value=self.supplier_name_input.text)
