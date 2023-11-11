from ._anvil_designer import TeardownModuleTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import uuid
import datetime


class TeardownModule(TeardownModuleTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    suppliers = self.mock_get_suppliers()
    self.supplier_dropdown.items = suppliers

  def mock_get_suppliers(self):
    supplier_tuples = anvil.server.call('get_supplier_dropdown')

  def mock_get_trucks(self):
    return anvil.server.call('get_unique_trucks')
    
  def get_suppliers(self):
    pass

######### COMPONENT EVENTS ############################

  def create_new_truck_click(self, **event_args):
    """This method is called when the button is clicked"""
    if anvil.confirm("Generate New Truck?"):
      new_truck_id = str(uuid.uuid4())
      self.truck_id = new_truck_id
      created_date = datetime.date.today()
      anvil.server.call('create_truck', truck_id, created_date)
      anvil.confirm("New Truck has been generated.")
