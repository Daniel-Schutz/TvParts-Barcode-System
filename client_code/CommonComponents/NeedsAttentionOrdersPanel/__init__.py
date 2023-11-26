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

    # Any code you write here will run before the form opens.


##### Open the Resolve Items Modal to allow for order remediation
  def resolve_items_btn_click(self, **event_args):
    order_no = self.order_no_output.content
    fulfillments = anvil.server.call('load_current_fulfillments', 
                                     order_no=order_no)
    modal_return = anvil.alert(NeedsAttentionResolveModal(order_no=order_no,
                                                          repeater_items=fulfillments))
    #some conditional logic about what events to pass up based on what happens in the modal