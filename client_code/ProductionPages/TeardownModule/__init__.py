from ._anvil_designer import TeardownModuleTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import js
import anvil.media
import time

from ...CommonComponents.SingleSelect_modal import SingleSelect_modal
from ...CommonComponents.CreateSupplierModal import CreateSupplierModal

import uuid
import datetime
import time
import json


class TeardownModule(TeardownModuleTemplate):
  def __init__(self, current_user, current_role, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    suppliers = self.mock_get_suppliers()
    self.current_user = current_user
    self.current_role = current_role
    self.supplier_dropdown.items = suppliers
    self.supplier_dropdown.selected_value = "Unknown Supplier"
    self.qr_img_url = None

  def mock_get_suppliers(self):
    supplier_tuples = anvil.server.call('get_supplier_dropdown')
    return supplier_tuples

  def create_new_supplier(self, supplier_name):
    def update_dropdown(supplier_name):
      suppliers = self.mock_get_suppliers()
      self.supplier_dropdown.items = suppliers
      self.supplier_dropdown.selected_value = (supplier_name, supplier_name)
    anvil.server.call('add_new_supplier',
                    supplier_id = str(uuid.uuid4()),
                    supplier_name = supplier_name,
                    truck_count = 0,
                    created_date = datetime.date.today())
    time.sleep(0.5)
    update_dropdown(supplier_name)
    
    

  def mock_get_trucks(self):
    return anvil.server.call('get_unique_trucks')
    
  def get_suppliers(self):
    pass

  def print_barcode(self):
    #pdf = anvil.server.call('fetch_and_return_image', self.qr_image.source)
    # test_source = "data:image/png;base64,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"
    # html="""
    # <img src={image_url}>
    # """.format(image_url=test_source)
    # print(html)
    # js.call('printPage', html)
    print("Image URL:", self.qr_img_url)
    js.call('printPage', self.qr_img_url)
    # data_url = anvil.server.call('get_image_as_data_url', self.qr_image.source)
    # js.call('printPage', data_url)

    # print("got thie pdf!")
    # print(pdf)

######## Create Truck Id helper functions ###############

  
  def create_truck_id(self):
      supplier = self.supplier_dropdown.selected_value
      current_truck_count = anvil.server.call('search_rows', 
                                              table_name='suppliers',
                                              column_name='supplier_name',
                                              value=supplier)[0]['truck_count']
      new_str = ''
      supplier_words = supplier.split()
      for word in supplier_words:
          # Remove parentheses and take the first 3 characters of each word
          pre_text = word.replace(")", "").replace("(", "")[:3]
          # Concatenate to new_str (no need to use join here)
          new_str += pre_text.upper()  # assuming you want uppercase letters
      new_count = current_truck_count + 1
      # Format the new truck ID with the incremented count
      truck_id = f"{new_str}_{new_count}"
      return new_count, truck_id
      
######### COMPONENT EVENTS ############################    
  def continue_truck_btn_click(self, **event_args):
    supplier = self.supplier_dropdown.selected_value
    trucks = anvil.server.call('search_rows', 
                               'trucks', 
                               column_name='supplier_name', 
                               value=supplier)
    prev_trucks = SingleSelect_modal(trucks=trucks)
    truck_id = anvil.alert(
      prev_trucks, 
      title=f"All Trucks from {supplier}",
      buttons=[], 
      large=True
    )
    if truck_id:
      self.truck_id.text = truck_id
      s3_source = anvil.server.call('search_rows', 
                        'trucks', 
                        column_name='truck_id', 
                        value=truck_id)[0]['s3_object_key']
      
      #Get presigned url
      img_source = anvil.server.call('get_s3_image_url', s3_source)
      self.qr_img_url = img_source
      self.qr_image.source = img_source
  


  def create_new_truck_click(self, **event_args):
    """This method is called when the button is clicked"""
    if anvil.confirm("Generate New Truck?"):
      new_truck_count, new_truck_id = self.create_truck_id()
      self.truck_id.text = new_truck_id
      created_date = datetime.date.today()
      
      #Add row to truck table
      anvil.server.call('add_row_to_table', 
                        'trucks',
                        truck_id=new_truck_id, 
                        truck_created=datetime.date.today(),
                        supplier_name=self.supplier_dropdown.selected_value, 
                        item_system_count=0, 
                        item_sold_count=0, 
                        item_return_count=0, 
                        item_defect_count=0, 
                        s3_object_key='')
      
      #Update supplier truck count
      anvil.server.call('update_rows', 
                        table_name='suppliers', 
                        search_column='supplier_name', 
                        search_value=self.supplier_dropdown.selected_value, 
                        target_column='truck_count', 
                        new_value=new_truck_count)
      #anvil.confirm("New Truck has been generated.")
      time.sleep(0.5)
      self.create_qr(new_truck_id)
      

  #This is manually invoked, as it depends on UUID Generation
  def create_qr(self, truck_id, **event_args):
    supplier = self.supplier_dropdown.selected_value
    truck = self.truck_id.text
    qr_img_url = anvil.server.call('generate_qr_code', 
                                              truck=truck)
    self.qr_img_url = qr_img_url
    self.qr_image.source = qr_img_url

    #TODO: Move all of this to a background function
    s3_obj_key = anvil.server.call('store_qr_code', qr_img_url)
    s3_img_url = anvil.server.call('get_s3_image_url', s3_obj_key)
    self.qr_image.source = s3_img_url
    #Update img source in table - TODO: Move to AWS image storage
    anvil.server.call('update_rows', 
                    table_name='trucks', 
                    search_column='truck_id', 
                    search_value=truck_id, 
                    target_column='s3_object_key', 
                    new_value=s3_obj_key)
    

  def create_barcode_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.print_barcode()

  def add_supplier_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    modal_form = CreateSupplierModal()
    new_supplier_name = anvil.alert(modal_form,
                                    large=True, dismissible=False, title='Create New Supplier')
    print(new_supplier_name)
    if new_supplier_name:
      if not type(new_supplier_name) == bool:
        self.create_new_supplier(new_supplier_name)
        self.mock_get_suppliers()
        self.supplier_dropdown.selected_value = new_supplier_name
    
    
    


