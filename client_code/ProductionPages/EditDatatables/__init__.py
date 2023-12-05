from ._anvil_designer import EditDatatablesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class EditDatatables(EditDatatablesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.select_table_dd.items = anvil.server.call('get_table_name_dropdown')
    self.select_table_dd.selected_value = '(Select Table)'

    # Any code you write here will run before the form opens.

    
##################################################
###### Visibility Settings #######################
  def init_visibility(self):
    self.select_table_dd.selected_value = '(Select Table)'
    self.num_results_panel.visible = False
    self.no_results_output.content = None
    self.col_to_modify_panel.visible = False
    self.filter_conditions_card.visible = False
    self.column_datatype_out.content = None
    self.filt_1_dtype_out.content = None
    self.query_1_text_input.text = None
    self.query_1_date_input.date = None
    self.filt_2_dtype_out.content = None
    self.query_2_text_input.text = None
    self.query_2_date_input.date = None    
    self.filt_3_dtype_out.content = None
    self.query_3_text_input.text = None
    self.query_3_date_input.date = None
    self.set_value_panel.visible = False
    self.new_value_text_input.text = None
    self.new_value_date_input.date = None
    
    

###################################################
###### Data Type/Data Validation & Dropdowns ######


###################################################
###### Database Interaction #######################