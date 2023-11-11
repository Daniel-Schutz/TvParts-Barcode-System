from ._anvil_designer import Temp_ServerTestTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import js
import anvil.media

import uuid
import datetime
import time
import json

class Temp_ServerTest(Temp_ServerTestTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def mock_get_suppliers(self):
    supplier_tuples = anvil.server.call('get_supplier_dropdown')
    return supplier_tuples

  def mock_get_trucks(self):
    return anvil.server.call('get_unique_trucks')

  def get_suppliers(self):
    pass

  def print_barcode(self):
    #print(self.qr_image.source)
    #js.window.printImage(self.qr_image.source)
    anvil.media.print_media(self.qr_image.source)


######### COMPONENT EVENTS ############################

  def create_new_truck_click(self, **event_args):
    """This method is called when the button is clicked"""
    if anvil.confirm("Generate New Truck?"):
      new_truck_id = str(uuid.uuid4()) #set new truck IDs here
      self.truck_id.text = new_truck_id
      created_date = datetime.date.today()
      anvil.server.call('create_truck', new_truck_id, created_date)
      #anvil.confirm("New Truck has been generated.")
      self.create_qr()


  #This is manually invoked, as it depends on UUID Generation
  def create_qr(self, **event_args):
    supplier = self.supplier_dropdown.selected_value
    truck = self.truck_id.text
    self.qr_image.source = anvil.server.call('generate_qr_code',
                                              supplier=supplier, truck=truck)

  def create_barcode_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.print_barcode()
