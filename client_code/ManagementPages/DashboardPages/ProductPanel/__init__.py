from ._anvil_designer import ProductPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import plotly.graph_objects as go

class ProductPanel(ProductPanelTemplate):
  def __init__(self, current_user, current_role, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.current_user = current_user
    self.current_role = current_role

    misidentified_rate = anvil.server.call('misidentified_rate_per_product')
    needs_attention_rate = anvil.server.call('needs_attention_rate')
    testing_failure_rate = anvil.server.call('testing_failure_rate')

    average_holding_time = anvil.server.call('average_holding_time')
    average_time_fulfill = anvil.server.call('average_time_to_fulfill')
    self.holding_time_output.content = average_holding_time
    self.time_fulfill_output.content = average_time_fulfill
        # Create data for bar chart
    bar_chart_plot_2_copy = go.Bar(
        x=list(misidentified_rate.keys()),
        y=list(misidentified_rate.values())
    )
    self.plot_2_copy.data =  [bar_chart_plot_2_copy]

    bar_chart_plot_2_copy_copy_3 = go.Bar(
        x=list(needs_attention_rate.keys()),
        y=list(needs_attention_rate.values())
    )
    self.plot_2_copy_copy_3.data =  [bar_chart_plot_2_copy_copy_3]


    bar_chart_plot_2 = go.Bar(
        x=list(testing_failure_rate.keys()),
        y=list(testing_failure_rate.values())
    )
    self.plot_2.data =  [bar_chart_plot_2]
