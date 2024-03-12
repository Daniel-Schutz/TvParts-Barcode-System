from ._anvil_designer import PlacePartModalTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
import random
import string
import uuid
from ...CommonComponents import CommonFunctions as cf
from ...CommonComponents.SelectBinModal import SelectBinModal
from datetime import datetime
import time

class PlacePartModal(PlacePartModalTemplate):
  def __init__(self, current_user, current_role, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.current_user = current_user
    self.current_role = current_role
    self.purgatory_bins = anvil.server.call_s('get_bins_in_purgatory')
    #If disabled, assumes that items are placed in their primary bin location upon placement scan
    self.require_bin_to_place = False #come back and edit this when looking at full functionality
    self.place_item_id = None

  
    # Any code you write here will run before the form opens.
# ######### Place Part Visibility Settings ###########
  def reset_place_part_visibility(self):
    self.other_bins_dd.items = [('(No Other Bins)', '(No Other Bins)')]
    self.other_bins_dd.selected_value = '(No Other Bins)'
    self.place_item_id = None
    self.item_code_place_input.text = None
    self.item_code_place_input.enabled = True
    self.primary_bin_output.content = None
    self.scan_item_panel.visible = True
    self.primary_bin_panel.visible = False
    self.other_bins_panel.visible = False 
    
  def primary_bin_visibility(self):
    self.scan_item_panel.visible = True
    self.primary_bin_panel.visible = True
    self.other_bins_panel.visible = False

  def other_bin_visibility(self):
    self.scan_item_panel.visible = True
    self.primary_bin_panel.visible = False
    self.other_bins_panel.visible = True
    if self.other_bins_dd.selected_value == '(Select Bin)':
      self.place_other_bin_btn.enabled = False
    else:
      self.place_other_bin_btn.enabled = True

  
# ######### Place Part Events ########################
# Helper for major update events
  def _place_item_updates(self, bin):
    print('HERE is the BIN: ', bin)
    anvil.server.call('update_item_on_binned', 
                      user=self.current_user, 
                      role=self.current_role,
                      item_id=self.place_item_id, 
                      bin=bin)
    n = Notification(f"{item_id} added to stock in bin {bin}. Inventory Updated!", style='success')
    n.show()
    #Update inventory (additive)
    #anvil.server.call('update_inv_qty_by_item', self.place_item_id)
  
  def item_code_place_input_pressed_enter(self, **event_args):
    time.sleep(1)
    self.item_code_place_input.enabled = False
    
    #get the primary bin location  & purgatory rows
    purgatory_bins = self.purgatory_bins
    item_scan = json.loads(self.item_code_place_input.text)
    self.place_item_id = item_scan.get('item_id')
    
    #maybe add validation at this row for item scans later on
    primary_bin = anvil.server.call('get_primary_bin_from_item_scan', 
                                    self.place_item_id)

    #Purgatory Handling
    if primary_bin in purgatory_bins:
      n = Notification(f"Bin {primary_bin} is in purgatory. Please place item in purgatory area.", 
                       title="Place Item In Purgatory", style='warning', timeout=10)
      n.show()
      anvil.server.call('add_item_to_purgatory', 
                        user=self.current_user, 
                        role=self.current_role,
                        bin=primary_bin,
                        item_id=self.place_item_id)
      self.reset_place_part_visibility()
      
    else:
      self.primary_bin_output.content = primary_bin
      self.primary_bin_visibility()
      self.other_bins_dd.items = anvil.server.call('get_other_bins_dd', primary_bin)
      self.other_bins_dd.selected_value = '(Select Bin)'
    
    
  def clear_place_input_btn_click(self, **event_args):  
    #get the primary bin location
    self.reset_place_part_visibility()

  def add_to_stock_primary_btn_click(self, **event_args):
    bin = self.primary_bin_output.content
    self._place_item_updates(bin)
    self.reset_place_part_visibility()

  def place_other_bin_btn_click(self, **event_args):
    bin = self.other_bins_dd.selected_value
    self._place_item_updates(bin)
    self.reset_place_part_visibility()

  def on_other_bin_dd_change(self, **event_args):
    if self.other_bins_dd.selected_value == '(Select Bin)':
      self.place_other_bin_btn.enabled = False
    else:
      self.place_other_bin_btn.enabled = True

  def other_bins_btn_click(self, **event_args):
    self.other_bin_visibility()
      
  def back_to_primary_btn_click(self, **event_args):
    self.primary_bin_visibility()

  def new_bin_btn_click(self, **event_args):
    #Can put an admin code here too if needed
    primary_bin = self.primary_bin_output.content
    selected_bin = anvil.alert(SelectBinModal(primary_bin=primary_bin, mode='open_bins'), 
                               large=True, 
                               buttons=[])
    if selected_bin:
      part_number = self.place_item_id.split('__')[0]
      anvil.server.call('add_new_bin_for_item', 
                        self.place_item_id, 
                        selected_bin)
      n = Notification(f"New OS Bin for part number: {part_number}!",
                       style='Success', timeout=4, title='New OS Bin Activated')
      n.show()
      self.reset_place_part_visibility()


  def purg_primary_bin_btn_click(self, **event_args):
    primary_bin = self.primary_bin_output.content
    confirm = anvil.alert(f"Confirm add bin {primary_bin} to Purgatory?", 
                          title=f"Add {primary_bin} to Purgatory?", 
                          large=True, buttons=['SEND TO PURGATORY', 'CANCEL'])
    if confirm == 'SEND TO PURGATORY':
      n = Notification('Sending Bin and Item to Purgatory, just a moment...', 
                       title=f'Sending {primary_bin} to Purgatory', 
                       style='warning',
                       timeout=4)
      n.show()
      anvil.server.call('add_bin_to_purgatory', 
                        user=self.current_user, 
                        role=self.current_role, 
                        bin=primary_bin, 
                        item_id=self.place_item_id)
      self.purgatory_bins = anvil.server.call('get_bins_in_purgatory')
      n_2 = Notification('Bin added to purgatory!', style='success')
      n_2.show()
      self.reset_place_part_visibility()