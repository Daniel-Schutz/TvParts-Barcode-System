from ._anvil_designer import NeedsAttentionResolveModalTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

import json
from ..NeedsAttentionReplaceModal import NeedsAttentionReplaceModal
from ..MovetoTray import MovetoTray

class NeedsAttentionResolveModal(NeedsAttentionResolveModalTemplate):
  def __init__(self, order_no, repeater_items, user, role, dept, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.fulfillments_repeater.items = repeater_items
    self.current_order = order_no
    self.headline.text = f"Resolve Order {order_no}"
    self.current_user = user
    self.user_role = role
    self.dept = dept

    #handle item logic within the modal
    self.fulfillments_repeater.set_event_handler('x-remove-item-btn', self.remove_fulfillment)
    self.fulfillments_repeater.set_event_handler('x-replace-item-btn', self.replace_item)

    # Any code you write here will run before the form opens.



######## Event helper functions #########################
  def restock_linked_items(self):
    skus_list = [f['sku'] for f in self.fulfillments_repeater.items]
    bins_str = ''
    # counter=0
    for fulfillment in self.fulfillments_repeater.items:
      f_id = fulfillment['fulfillment_id']
      bin = anvil.server.call('restock_linked_item', 
                        f_id, 
                        self.current_user, 
                        self.user_role)
      print(f'in the bin area of restocking. bin={bin}')
      if bin:
        bins_str += f"{counter}: sku:{[skus_list[counter]]} | bin: {bin}\n"
      # counter += 1
    if bins_str == '':
      return None
      
    n = Notification(f"Items have been restocked in the system. \
    Please return all items to their original bins.\n {bins_str}", 
                     title="Restock Parts", 
                     style='warning', 
                     timeout=240)
    n.show()
  

######## Event Logic for remediation of the order###########
# Probably makes more sense to take care of all removal logic etc here
# And just have the system fetch a new item after this one has been moved
  
  #reverts the order to an open status and restocks linked items
  def clear_items_btn_click(self, **event_args):
    n_1 = Notification(f"Resetting Order {self.current_order}. Please wait.", style='info')
    n_1.show()
    self.restock_linked_items()
    anvil.server.call('reset_order', self.current_order)
    self.raise_event("x-close-alert", value=42) #close modal

  #removes the order and its fulfillments from the system and restocks linked items
  def cancel_order_btn_click(self, **event_args):
    n_1 = Notification(f"Deleting Order {self.current_order}. Please wait.", style='info')
    n_1.show()
    self.restock_linked_items()
    anvil.server.call('delete_order', self.current_order)
    self.raise_event("x-close-alert", value=42) #close modal


######### Inner Buttons handled using event handlers (to centralize logic) ####
  def remove_fulfillment(self, fulfillment_id, **event_args):
    if len(self.fulfillments_repeater.items) == 1:
      kill_order = anvil.alert("NOTICE: Since there is only product in this order, removing the product will cancel the fulfillment of this order. Ok to proceed?",
                 title="Cancel Order?", buttons=['DELETE ORDER', 'CANCEL'], large=True)
      if kill_order == 'DELETE ORDER':
        self.cancel_order_btn_click()
        return None
    sku = anvil.server.call('get_sku_from_f_id', fulfillment_id=fulfillment_id)
    remove_modal = anvil.alert(f"Confirm removal of {sku} from order {self.current_order}",
                              title='Remove Product?', 
                               buttons=['YES', 'CANCEL'], 
                               large=True)
    if remove_modal == 'YES':
      n = Notification("Removing Product from Order. Just a moment.", 
                       title='Partial No-Stock: Removing Product from Order', style='warning',
                      timeout=5)
      n.show()
      anvil.server.call('remove_fulfillment_by_item_id', 
                        item_id,
                        self.current_user, 
                        self.user_role)
      self.fulfillments_repeater.items = anvil.server.call('load_current_fulfillments', 
                                                           self.current_order)
      

  def replace_item(self, item_id, fulfillment_id, **event_args):
    #the actual action in this one happens in the modal
    replace_modal = anvil.alert(NeedsAttentionReplaceModal(item_id=item_id),
                               large=True, dismissible=False)
    if replace_modal == 'CANCELLED':
      pass
    else:
      self.fulfillments_repeater.items = anvil.server.call('load_current_fulfillments', 
                                                           self.current_order)
      
      
    
########## Move to Tray Logic #####################
  def move_to_tray(self):
    tray_modal = anvil.alert(MovetoTray(user=self.current_user, role=self.user_role, order_no=self.current_order), 
                             large=True, buttons=['CANCEL'])
    if tray_modal == 'CANCEL':
      return None
    n = Notification('Order restored. Will return to flow after the next table completion.',
                    title='Order Restored!', style='success', timeout=3)
    n.show()
    self.raise_event('x-close-alert')