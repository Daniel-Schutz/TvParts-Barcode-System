from ._anvil_designer import NeedsAttentionOrdersPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..NeedsAttentionResolveModal import NeedsAttentionResolveModal
from ...ManagementPages.AdminPassModal import AdminPassModal

class NeedsAttentionOrdersPanel(NeedsAttentionOrdersPanelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.order_no_output.text = self.item['order_no']
    self.table_output.content = self.item['table_no']
    self.section_output.content = self.item['section']
    self.customer_name_output.content = self.item['customer_name']
    self.price_output.content = self.item['total_price']
    self.no_items_output.content = self.item['total_items']
    self.dept = self.item['dept']
    self.current_user = anvil.server.call('get_user_full_name')
    self.current_role = anvil.server.call('get_user_role')

    # Any code you write here will run before the form opens.


##### Open the Resolve Items Modal to allow for order remediation
  def resolve_items_btn_click(self, **event_args):
    order_no = self.item['order_no']
    fulfillments = anvil.server.call('load_current_fulfillments', 
                                     order_no=order_no)
    
    #Admin Passcode protection
    access = anvil.alert(AdminPassModal(), 
                         dismissible=False, 
                         large=True)
    if access == 'Granted':
      modal_return = anvil.alert(NeedsAttentionResolveModal(order_no=order_no,
                                                            repeater_items=fulfillments, 
                                                            user=self.current_user, 
                                                            role=self.current_role, 
                                                            dept=self.dept), 
                                large=True, 
                                title="Resolve Order Menu")
    elif access == 'Denied':
      n = Notification("Admin Passcode was incorrect!", 
                       style='danger', title='Wrong Password',
                      timeout=1)
    else:
      return None