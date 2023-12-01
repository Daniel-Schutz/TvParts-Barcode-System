from ._anvil_designer import NeedsAttentionOrdersPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..NeedsAttentionResolveModal import NeedsAttentionResolveModal

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
    
    #Get the department down to the innermost nest so it can be used to define visibility based on dept
    # fs_with_dept = []
    # for record in fulfillments:
    #   f_dict = dict(record)
    #   f_dict['dept'] = self.dept
    #   f_dict['num_fulfillments'] = len(fulfillments)
    #   fs_with_dept.append(f_dict)
    modal_return = anvil.alert(NeedsAttentionResolveModal(order_no=order_no,
                                                          repeater_items=fulfillments, 
                                                          user=self.current_user, 
                                                          role=self.current_role, 
                                                          dept=self.dept), 
                               large=True, 
                               title="Resolve Order Menu")
    #some conditional logic about what events to pass up based on what happens in the modal