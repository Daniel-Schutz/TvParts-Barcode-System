from ._anvil_designer import SingleProductEditTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import js
import anvil.media

class SingleProductEdit(SingleProductEditTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)


    # Any code you write here will run before the form opens.

######## Select Event #############################
  def update_product_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    print("read the button click")
    print()
    anvil.server.call('update_product',self.item['product_id'],
                      self.name_input.text,self.sku_input.text,self.bin_input.text,
                     self.text_box_1.text,self.text_box_2.text,self.vendor_input.text,
                     self.os_bin_input.text,self.cross_refs.text)
    n = Notification("Product updated!", 
                       style='success', timeout=2)
    n.show()

