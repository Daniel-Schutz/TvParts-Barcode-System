from ._anvil_designer import SupplierPanelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import plotly.graph_objects as go
from datetime import datetime

class SupplierPanel(SupplierPanelTemplate):
  def __init__(self, current_user, current_role, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.current_user = current_user
    self.current_role = current_role
    
    end_date = datetime.now().strftime("%m/%d/%Y")
    start_date = '01/01/1900'
    '''revenue_by_supplier = anvil.server.call('revenue_by_supplier_and_date',start_date,end_date)
    bar_chart_plot_2_copy_copy = go.Bar(
        x=list(parts_by_year.keys()),
        y=list(parts_by_year.values())
    )
    self.plot_2_copy_copy.data =  [bar_chart_plot_2_copy_copy]'''
    
    '''revenue_by_truck = anvil.server.call('revenue_by_truck_and_date',start_date,end_date)
    bar_chart_plot_2_copy_copy_2 = go.Bar(
        x=list(parts_by_year.keys()),
        y=list(parts_by_year.values())
    )
    self.plot_2_copy_copy_2.data =  [bar_chartplot_2_copy_copy_2]'''
    
    parts_by_year = anvil.server.call('count_items_per_year')
    bar_chart_plot_2_copy = go.Bar(
        x=list(parts_by_year.keys()),
        y=list(parts_by_year.values())
    )
    self.plot_2_copy.data =  [bar_chart_plot_2_copy]
    
    parts_by_brand = anvil.server.call('count_items_per_brand')
    bar_chart_plot_2_copy_copy_3 = go.Bar(
        x=list(parts_by_brand.keys()),
        y=list(parts_by_brand.values())
    )
    self.plot_2_copy_copy_3.data =  [bar_chart_plot_2_copy_copy_3]

    
    parts_by_model = anvil.server.call('count_items_per_model')
    bar_chart_plot_2 = go.Bar(
        x=list(parts_by_model.keys()),
        y=list(parts_by_model.values())
    )
    self.plot_2.data =  [bar_chart_plot_2]

    
    tossed_rate_per_truck = anvil.server.call('tossed_rate_per_truck')
    bar_chart_plot_2_copy_copy_4 = go.Bar(
        x=list(tossed_rate_per_truck.keys()),
        y=list(tossed_rate_per_truck.values())
    )
    self.plot_2_copy_copy_4.data =  [bar_chart_plot_2_copy_copy_4]

  def query_1_date_input_copy_change(self, **event_args):
    """This method is called when the selected date changes"""
    end_date = self.query_1_date_input.date
    start_date = self.query_1_date_input_copy.date
    '''revenue_by_supplier = anvil.server.call('revenue_by_supplier_and_date',start_date,end_date)
    bar_chart_plot_2_copy_copy = go.Bar(
        x=list(parts_by_year.keys()),
        y=list(parts_by_year.values())
    )
    self.plot_2_copy_copy.data =  [bar_chart_plot_2_copy_copy]'''
    
    '''revenue_by_truck = anvil.server.call('revenue_by_truck_and_date',start_date,end_date)
    bar_chart_plot_2_copy_copy_2 = go.Bar(
        x=list(parts_by_year.keys()),
        y=list(parts_by_year.values())
    )
    self.plot_2_copy_copy_2.data =  [bar_chartplot_2_copy_copy_2]'''
    pass

  def query_1_date_input_change(self, **event_args):
    """This method is called when the selected date changes"""
    end_date = datetime.now().strftime("%m/%d/%Y")
    start_date = '01/01/1900'
    '''revenue_by_supplier = anvil.server.call('revenue_by_supplier_and_date',start_date,end_date)
    bar_chart_plot_2_copy_copy = go.Bar(
        x=list(parts_by_year.keys()),
        y=list(parts_by_year.values())
    )
    self.plot_2_copy_copy.data =  [bar_chart_plot_2_copy_copy]'''
    
    '''revenue_by_truck = anvil.server.call('revenue_by_truck_and_date',start_date,end_date)
    bar_chart_plot_2_copy_copy_2 = go.Bar(
        x=list(parts_by_year.keys()),
        y=list(parts_by_year.values())
    )
    self.plot_2_copy_copy_2.data =  [bar_chartplot_2_copy_copy_2]'''
    pass
