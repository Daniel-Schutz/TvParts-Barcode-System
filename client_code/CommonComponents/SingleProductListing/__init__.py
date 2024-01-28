from ._anvil_designer import SingleProductListingTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import js
import anvil.media

class SingleProductListing(SingleProductListingTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.print_product_btn.visible = False
    self.image_1.visible = False
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

  def print_product_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    print("Image URL:", self.item['qr_code_url'])
    js.call('printPage', self.item['qr_code_url'])

  def generate_label_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    print( self.sku_content)
    row = anvil.server.call('get_product_row_by_sku',self.sku_content)
    img_url = anvil.server.call('get_s3_image_url',s3_obj_key)
    self.image_1.source = img_url
    self.print_product_btn.visible = True
    self.image_1.visible = True
    pass

