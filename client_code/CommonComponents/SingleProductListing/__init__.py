from ._anvil_designer import SingleProductListingTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class SingleProductListing(SingleProductListingTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

######## Select Event #############################
  def select_product_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    print("read the button click")
    print(self.item['sku'])
    n = Notification(f"The selected product is: {self.item['sku']}", style='info')
    n.show()
    self.parent.raise_event('x-product-selected', product=self.item)
