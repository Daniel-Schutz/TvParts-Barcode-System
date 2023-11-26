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
  def __init__(self, order_no, repeater_items, user, role, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.fulfillments_repeater.items = repeater_items
    self.current_order = order_no
    self.headline.text = f"Resolve Order {order_no}"
    self.current_user = user
    self.user_role = role
    self.fulfillments_repeater.set_event_handler('x-remove-item-btn', self.remove_item)
    self.fulfillments_repeater.set_event_handler('x-replace-item-btn', self.replace_item)

    # Any code you write here will run before the form opens.


######## Event helper functions #########################
  def restock_linked_items(self):
    skus_list = [f['sku'] for f in self.fulfillments_repeater.items]
    bins_str = ''
    counter=0
    for fulfillment in self.fulfillments_repeater.items:
      f_id = fulfillment['fulfillment_id']
      bin = anvil.server.call('restock_linked_item', 
                        f_id, 
                        self.current_user, 
                        self.user_role)
      if bin:
        bins_str += f"{counter}: sku:{[skus_list[counter]]} | bin: {bin}\n"
      counter += 1
    bins_dict_str = json.dumps()
    n = Notification(f"Items have been restocked in the system. \
    Please return all items to their original bins.\n {bins_str}", 
                     title="Restock Parts", 
                     style='warning', 
                     timeout=120)
    n.show()
  

######## Event Logic for remediation of the order###########
# Probably makes more sense to take care of all removal logic etc here
# And just have the system fetch a new item after this one has been moved
  
  #reverts the order to an open status and restocks linked items
  def clear_items_btn_click(self, **event_args):
    n_1 = Notification(f"Resetting Order {self.current_order}. Please wait.", style='info')
    n_1.show()
    anvil.server.call('reset_order', self.current_order)
    self.restock_linked_items()
    self.raise_event("x-close-alert", value=42) #close modal
    pass

  #removes the order and its fulfillments from the system and restocks linked items
  def cancel_order_btn_click(self, **event_args):
    n_1 = Notification(f"Deleting Order {self.current_order}. Please wait.", style='info')
    n_1.show()
    anvil.server.call('delete_order', self.current_order)
    self.restock_linked_items()
    self.raise_event("x-close-alert", value=42) #close modal
    pass


######### Inner Buttons handled using event handlers (to centralize logic) ####
  def remove_item(self, item_id, fulfillment_id, **event_args):
    remove_modal = anvil.alert(f"Confirm removal of item {item_id} from order {self.current_order}",
                              title='Remove Item?', 
                               buttons=['YES', 'CANCEL'], 
                               large=True)
    if remove_modal == 'YES':
      n = Notification("Removing Fulfillment from Order. Just a moment.", 
                       title='Partial No-Stock: Removing Item', style='warning',
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