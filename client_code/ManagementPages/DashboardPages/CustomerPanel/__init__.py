from ._anvil_designer import CustomerPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import plotly.graph_objects as go

class CustomerPanel(CustomerPanelTemplate):
  def __init__(self, current_user, current_role, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.current_user = current_user
    self.current_role = current_role
    repeat_rate = anvil.server.call('repeat_purchase_rate')
    customer_data = anvil.server.call('total_order_volume_per_customer')
    # Create data for bar chart
    bar_chart = go.Bar(
        x=list(customer_data.keys()),
        y=list(customer_data.values())
    )
    
    # Update plot with bar chart
    self.plot_customer.data = [bar_chart]

    self.repeat_rate_output.content = f"{repeat_rate:.2f}%"
