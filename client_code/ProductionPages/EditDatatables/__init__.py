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
    self.col_tups = None
    self.col_type_map = None
    self.string_dropdown_options = anvil.server.call('get_string_compare_dd')
    self.num_dropdown_options = anvil.server.call('get_num_compare_dd')
    self.init_visibility()

    # Any code you write here will run before the form opens.

    
##################################################
###### Visibility Settings #######################
  def init_visibility(self):
    #self.select_table_dd.selected_value = '(Select Table)'
    self.select_table_dd.enabled = True
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
    #Reset object vars
    self.col_tups = None
    self.col_type_map = None

  def table_selected_visibility(self):
    table = self.select_table_dd.selected_value
    self.select_table_dd.enabled = False
    self.no_results_output.content = anvil.server.call('get_table_len', table)
    self.num_results_panel.visible = True
    self._get_column_dd_for_table()
    self.col_to_modify_panel.visible = True

  def modify_col_selected_visibility(self):
    if self.select_col_dd.selected_value == '(Select Column)':
      self.column_datatype_out.content = '(Select Column)'
      self.filter_conditions_card.visible = False
    else:
      self.column_datatype_out.content = self.col_type_map[self.select_col_dd.selected_value]
      self.filter_conditions_card.visible = True
      self.init_filter_box_visibility()

  def init_filter_box_visibility(self):
    self.filt_condition_1_panel.visible = False
    self.filt_condition_2_panel.visible = False
    self.filt_condition_3_panel.visible = False

  def add_filter_box_visibility(self):
    if self.filt_condition_3_panel.visible:
      anvil.alert("You can only have up to 3 filters. If you need more, contact Autonomi.")
    elif self.filt_condition_2_panel.visible:
      self.filt_condition_3_panel.visible = True
      self.filter_box_3_init_visibility()
    elif self.filt_condition_1_panel.visible:
      self.filt_condition_2_panel.visible = True
      self.filter_box_2_init_visibility()
    else:
      self.filt_condition_1_panel.visible = True   
      self.filter_box_1_init_visibility()

  def filter_box_1_init_visibility(self):
    self.filt_col_dd_1.selected_value = '(Select Column)'
    self.filt_1_dtype_out.content = '(Select Column)'
    self.query_dd.visible = False
    self.query_1_text_input.visible = False
    self.query_1_date_input.visible = False
  
  def filter_box_2_init_visibility(self):
    self.filt_col_dd_2.selected_value = '(Select Column)'
    self.filt_2_dtype_out.content = '(Select Column)'
    self.query2_dd.visible = False
    self.query_2_text_input.visible = False
    self.query_2_date_input.visible = False    

  def filter_box_3_init_visibility(self):
    self.filt_col_dd_3.selected_value = '(Select Column)'
    self.filt_3_dtype_out.content = '(Select Column)'
    self.query3_dd.visible = False
    self.query_3_text_input.visible = False
    self.query_3_date_input.visible = False   

  def filter_box_1_column_select_vis(self):
    if self.filt_col_dd_1.selected_value == '(Select Column)':
      self.filt_1_dtype_out.content = '(Select Column)'
      self.query_dd.visible = False
      self.query_1_text_input.visible = False
      self.query_1_date_input.visible = False
    else:
      self.filt_1_dtype_out.content = self.col_type_map[self.filt_col_dd_1.selected_value]
      if self.filt_1_dtype_out.content == 'string':
        self.query_dd.items = self.string_dropdown_options
        self.query_dd.selected_value = "(Select Condition)"
        self.query_dd.visible = True
        self.query_1_text_input.visible = True
        self.query_1_date_input.visible = False
      else:
        self.query_dd.items = self.num_dropdown_options
        self.query_dd.selected_value = "(Select Condition)"
        self.query_dd.visible = True
        if self.filt_1_dtype_out.content == 'number':
          self.query_1_text_input.visible = True
          self.query_1_date_input.visible = False        
        elif self.filt_1_dtype_out.content == 'datetime':
          self.query_1_text_input.visible = False
          self.query_1_date_input.visible = True

  def filter_box_2_column_select_vis(self):
    if self.filt_col_dd_2.selected_value == '(Select Column)':
      self.filt_2_dtype_out.content = '(Select Column)'
      self.query2_dd.visible = False
      self.query_2_text_input.visible = False
      self.query_2_date_input.visible = False
    else:
      self.filt_2_dtype_out.content = self.col_type_map[self.filt_col_dd_2.selected_value]
      if self.filt_2_dtype_out.content == 'string':
        self.query2_dd.items = self.string_dropdown_options
        self.query2_dd.selected_value = "(Select Condition)"
        self.query2_dd.visible = True
        self.query_2_text_input.visible = True
        self.query_2_date_input.visible = False
      else:
        self.query2_dd.items = self.num_dropdown_options
        self.query2_dd.selected_value = "(Select Condition)"
        self.query2_dd.visible = True
        if self.filt_2_dtype_out.content == 'number':
          self.query_2_text_input.visible = True
          self.query_2_date_input.visible = False        
        elif self.filt_2_dtype_out.content == 'datetime':
          self.query_2_text_input.visible = False
          self.query_2_date_input.visible = True

  def filter_box_3_column_select_vis(self):
    if self.filt_col_dd_3.selected_value == '(Select Column)':
      self.filt_3_dtype_out.content = '(Select Column)'
      self.query3_dd.visible = False
      self.query_3_text_input.visible = False
      self.query_3_date_input.visible = False
    else:
      self.filt_3_dtype_out.content = self.col_type_map[self.filt_col_dd_3.selected_value]
      if self.filt_3_dtype_out.content == 'string':
        self.query3_dd.items = self.string_dropdown_options
        self.query3_dd.selected_value = "(Select Condition)"
        self.query3_dd.visible = True
        self.query_3_text_input.visible = True
        self.query_3_date_input.visible = False
      else:
        self.query3_dd.items = self.num_dropdown_options
        self.query3_dd.selected_value = "(Select Condition)"
        self.query3_dd.visible = True
        if self.filt_3_dtype_out.content == 'number':
          self.query_3_text_input.visible = True
          self.query_3_date_input.visible = False        
        elif self.filt_3_dtype_out.content == 'datetime':
          self.query_3_text_input.visible = False
          self.query_3_date_input.visible = True

###################################################
###### Data Type/Data Validation & Dropdowns ######
  def _get_column_dd_for_table(self):
    table = self.select_table_dd.selected_value
    self.col_tups = anvil.server.call('get_col_names_for_dd', table)
    self.col_type_map= anvil.server.call('get_col_type_dict_for_mapping', table)
    self.select_col_dd.items = self.col_tups
    self.select_col_dd.selected_value = '(Select Column)'
    
    #Inititalize filter columns as well
    self.filt_col_dd_1.items = self.col_tups
    self.filt_col_dd_1.selected_value = '(Select Column)'
    self.filt_col_dd_2.items = self.col_tups
    self.filt_col_dd_2.selected_value = '(Select Column)'
    self.filt_col_dd_3.items = self.col_tups
    self.filt_col_dd_3.selected_value = '(Select Column)'
    pass


####################################################
########## On Change/On Click Events ###############
  def reset_search_click(self, **event_args):
    self.init_visibility()

  def select_table_change(self, **event_args):
    if self.select_table_dd.selected_value == '(Select Table)':
      self.init_visibility()
    else:
      self.table_selected_visibility()

  def select_col_dd_change(self, **event_args):
    self.modify_col_selected_visibility()

  def add_condition_btn_click(self, **event_args):
    self.add_filter_box_visibility()

  def filt_col_dd_1_change(self, **event_args):
    self.filter_box_1_column_select_vis()

  def filt_col_dd_2_change(self, **event_args):
    self.filter_box_2_column_select_vis()    

  def filt_col_dd_3_change(self, **event_args):
    self.filter_box_3_column_select_vis()    

###################################################
###### Database Interaction #######################