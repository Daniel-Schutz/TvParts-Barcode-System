from ._anvil_designer import ActionPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ActionPanel(ActionPanelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  #Init Orders
  self.orders_na_all()
  self.get_needs_fixed_panel()
  #Init Purgatory

    # Any code you write here will run before the form opens.

####### Get id holding read count

####### Orders NA Displays & Navigation ################
  def orders_na_all(self, **event_args):
    self.all_na_btn.background = "#236F65"
    self.warehouse_holding_btn.background = "#3FA498"
    self.testing_holding_btn.background = "#3FA498"
    self.shipping_holding_btn.background = "#3FA498"
    all_na_orders = anvil.server.call('get_all_needs_attention_orders')
    
    if len(all_na_orders) == 0:
      self.no_pending_items_panel.visible = True
      self.na_orders_repeater.visible = False
    else:
      self.no_pending_items_panel.visible = False
      self.na_orders_repeater.items = all_na_orders
      self.na_orders_repeater.visible = True
      
  def orders_na_warehouse(self, **event_args):
    self.all_na_btn.background = "#3FA498"
    self.warehouse_holding_btn.background = "#236F65"
    self.testing_holding_btn.background = "#3FA498"
    self.shipping_holding_btn.background = "#3FA498"
    all_na_orders = anvil.server.call('get_needs_attention_orders', 
                                      "Warehouse Hold", 
                                      "Warehouse")
    
    if len(all_na_orders) == 0:
      self.no_pending_items_panel.visible = True
      self.na_orders_repeater.visible = False
    else:
      self.no_pending_items_panel.visible = False
      self.na_orders_repeater.items = all_na_orders
      self.na_orders_repeater.visible = True

  
  def orders_na_testing(self, **event_args):
    self.all_na_btn.background = "#3FA498"
    self.warehouse_holding_btn.background = "#3FA498"
    self.testing_holding_btn.background = "#236F65"
    self.shipping_holding_btn.background = "#3FA498"
    all_na_orders = anvil.server.call('get_needs_attention_orders', 
                                      "Testing Hold", 
                                      "Testing")
    
    if len(all_na_orders) == 0:
      self.no_pending_items_panel.visible = True
      self.na_orders_repeater.visible = False
    else:
      self.no_pending_items_panel.visible = False
      self.na_orders_repeater.items = all_na_orders
      self.na_orders_repeater.visible = True

  
  def orders_na_shipping(self, **event_args):
    self.all_na_btn.background = "#3FA498"
    self.warehouse_holding_btn.background = "#3FA498"
    self.testing_holding_btn.background = "#3FA498"
    self.shipping_holding_btn.background = "#236F65"
    all_na_orders = anvil.server.call('get_needs_attention_orders', 
                                      "Shipping Hold", 
                                      "Shipping")
    
    if len(all_na_orders) == 0:
      self.no_pending_items_panel.visible = True
      self.na_orders_repeater.visible = False
    else:
      self.no_pending_items_panel.visible = False
      self.na_orders_repeater.items = all_na_orders
      self.na_orders_repeater.visible = True


####### Needs Fixed Display ################
  def get_needs_fixed_panel(self):
    needs_fixed_items = anvil.server.call('get_needs_fixed_items')
    if not needs_fixed_items:
      self.na_items_repeater.visible = False
      self.no_pending_items_panel.visible = True
    else:
      self.na_items_repeater.visible = True
      self.no_pending_items_panel.visible = False