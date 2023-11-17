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

from ...CommonComponents.single_input_modal import single_input_modal
from ...CommonComponents.SingleSelect_modal import SingleSelect_modal

import uuid
import datetime
import time
import json

class TeardownModule(TeardownModuleTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    suppliers = self.mock_get_suppliers()
    self.supplier_dropdown.items = suppliers
    self.supplier_dropdown.selected_value = "Unknown Supplier"

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
    #print(self.qr_image.source)
    #js.window.printImage(self.qr_image.source)
    anvil.media.print_media(self.qr_image.source)

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
    self.truck_id.text = truck_id

    
    img_source = anvil.server.call('search_rows', 
                      'trucks', 
                      column_name='truck_id', 
                      value=truck_id)[0]['qr_img_source']
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
    modal_form = single_input_modal(label_text="Enter new supplier name:")
    new_supplier_name = anvil.alert(modal_form, title="New Supplier", buttons=[], 
                                    large=True, dismissible=False)
    if new_supplier_name:
      self.create_new_supplier(new_supplier_name)
      self.mock_get_suppliers()
      self.supplier_dropdown.selected_value = new_supplier_name
    
    
    


