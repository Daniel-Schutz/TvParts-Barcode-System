from ._anvil_designer import ActionPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...CommonComponents.SelectBinModal import SelectBinModal

class ActionPanel(ActionPanelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.current_user = anvil.server.call('get_user_full_name')
    self.current_role = anvil.server.call('get_user_role')
    self.purgatory_bins = ''
    self.purgatory_items = ''

    #set event listeners for NF repeater logic
    self.nf_items_repeater.set_event_handler('x-nf-move-to-bin', 
                                             self.nf_move_item_to_bin)
    self.nf_items_repeater.set_event_handler('x-nf-toss-item', self.nf_toss_item)

    #Init all repeaters
    n_1 = Notification("Action Panel Loading. This requires a large amount of data, so please wait a moment...", 
                       title="Getting Action Panel", style='info', timeout=10)
    n_1.show()
    self.get_id_holding_count()
    self.orders_na_all()
    self.get_needs_fixed_panel()
    #Init Purgatory
    #Provide loaded success screen
    n_2 = Notification('Loading Complete! You may close this window', 
                       title='Action Panel Loaded', style='success', timeout=5)
    n_2.show()
  
      # Any code you write here will run before the form opens.

####### Get id holding read count ############
  def get_id_holding_count(self):
    self.holding_table_count_output.text = anvil.server.call_s('get_id_holding_count')
    pass

  # set hold count logic
  def set_hold_count_btn_click(self, **event_args):
    self.set_id_hold_count_btn.enabled = False
    set_text = self.id_hold_count_input.text
    try:
      set_num = int(set_text)
      anvil.server.call('set_id_holding_count', 
                        count=set_num)
      n = Notification(f'Id holding count has been set to {set_num}', 
                  title='Holding Count Updated!', 
                  style='success', timeout=2)
      n.show()
      self.id_hold_count_input.text = None
      self.get_id_holding_count(self)
      self.set_id_hold_count_btn.enabled = True
      
    except:
      n = Notification('New Id Holding Count must be a whole number.', 
                       title='Invalid Entry', 
                       style='danger', timeout=2)
      n.show()
      self.id_hold_count_input.text = None
      self.id_hold_count_input.focus()
      self.set_id_hold_count_btn.enabled = True
      return None #Stop execution
  

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
      self.nf_items_repeater.visible = False
      self.no_pending_items_panel.visible = True
    else:
      self.nf_items_repeater.visible = True
      self.no_pending_items_panel.visible = False

  # move to bin logic
  def nf_move_item_to_bin(self, primary_bin, item_id, **event_args):
    print('caught the NF move item event')
    new_bin = anvil.alert(SelectBinModal(primary_bin=primary_bin), 
                          large=True)
    if not new_bin:
      pass #take no action if the modal is closed without seletion
    else:
      n = Notification(f'Please restock item to bin {new_bin}.', 
                       title="Item Binned", 
                       style = 'info', 
                       timeout=60)
      anvil.server.call('bin_and_update_item', 
                        self.current_user, 
                        self.current_role, item_id, new_bin)
      #Reset Panel
      self.get_needs_fixed_panel()

  #toss logic
  def nf_toss_item(self, item_id, **event_args):
    confirm = anvil.alert("Are you sure you want to toss this item?", 
                          title='Confirm Toss', large=True, 
                          buttons=['TOSS ITEM', 'CANCEL'])
    if confirm == 'TOSS ITEM':
      n = Notification(f'Item {item_id} has been tossed.', 
                       title='Item Tossed', 
                       style='danger')
      n.show()
      anvil.server.call_s('toss_item', 
                          self.current_user, 
                          self.current_role, 
                          item_id)

########### Purgatory Logic ###################
# Initialize/Update purgatory
  def update_purgatory(self):
    purgatory_bins_exist = True
    purgatory_items_exist = True
    self.purgatory_bins = anvil.server.call('get_purgatory_bins')
    if not self.purgatory_bins:
      purgatory_bins_exist = False
    self.purgatory_items = anvil.server.call('get_purgatory_items')
    if not self.purgatory_items:
      purgatory_items_exist = False

    #sets view default to bins, falls back to items
    if not purgatory_bins_exist:
      if not purgatory_items_exist:
        self.no_purgatory_view()
      else:
        self.purgatory_items_view()
    else:
      self.purgatory_bins_view()

# Visibility and master buttons
  def purgatory_bins_view(self):
    self.purgatory_bins_btn.background = "#236F65"
    self.purgatory_items_btn.background = "#3FA498"
    self.bins_purgatory_repeater.visible = True
    self.bins_purgatory_spacer.visible = True
    self.items_purgatory_repeater.visible = False
    self.items_purgatory_spacer.visible = False
    self.no_purgatory_panel.visible = False
    
  def purgatory_items_view(self):
    self.purgatory_bins_btn.background = "#3FA498"
    self.purgatory_items_btn.background = "#236F65"
    self.bins_purgatory_repeater.visible = False
    self.bins_purgatory_spacer.visible = False
    self.items_purgatory_repeater.visible = True
    self.items_purgatory_spacer.visible = True
    self.no_purgatory_panel.visible = False  

  def no_purgatory_view(self):
    self.purgatory_bins_btn.background = "#236F65"
    self.purgatory_items_btn.background = "#3FA498"
    self.bins_purgatory_repeater.visible = False
    self.bins_purgatory_spacer.visible = False
    self.items_purgatory_repeater.visible = False
    self.items_purgatory_spacer.visible = False
    self.no_purgatory_panel.visible = True