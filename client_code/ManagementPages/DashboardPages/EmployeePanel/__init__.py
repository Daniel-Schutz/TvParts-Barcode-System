from ._anvil_designer import EmployeePanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import plotly.graph_objects as go

class EmployeePanel(EmployeePanelTemplate):
  def __init__(self, current_user, current_role, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.current_user = current_user
    self.current_role = current_role

    misidentified_items = anvil.server.call('misidentified_rate_per_employee')
    needs_attention_per_employee = anvil.server.call('needs_attention_rate_per_employee')
   
    employees = []
    counts = []
    percentages = []

    for employee, data in misidentified_items.items():
        employees.append(employee)
        counts.append(data['count'])
        percentages.append(data['percentage'])


    bar_chart_plot_2_copy = go.Bar(
        x=employees,
        y=counts
    )
    self.plot_2_copy.data =  [bar_chart_plot_2_copy]

    bar_chart_plot_2_copy_copy_3 = go.Bar(
        x=employees,
        y=percentages
    )
    self.plot_2_copy_copy_3.data =  [bar_chart_plot_2_copy_copy_3]

    bar_chart_plot_2 = go.Bar(
        x=list(needs_attention_per_employee.keys()),
        y=list(needs_attention_per_employee.values())
    )
    self.plot_2.data =  [bar_chart_plot_2]

