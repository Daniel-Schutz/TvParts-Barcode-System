from ._anvil_designer import DashboardingTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..DashboardPages.SupplierPanel import SupplierPanel
from ..DashboardPages.EmployeePanel import EmployeePanel
from ..DashboardPages.ProductPanel import ProductPanel
from ..DashboardPages.CustomerPanel import CustomerPanel

class Dashboarding(DashboardingTemplate):
  def __init__(self, current_user, current_role, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.current_user = current_user
    self.current_role = current_role

  def supplier_panel_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.main_content_panel.clear()
    self.main_content_panel.add_component(SupplierPanel(current_user=self.current_user, 
                                                      current_role=self.current_role), 
                                          full_width_row=True)
    self.supplier_panel_btn.role = 'raised'
    self.product_panel_btn.role = 'primary-color'
    self.employee_panel_btn.role = 'primary-color'
    self.customer_panel_btn.role = 'primary-color'
    pass

  def product_panel_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.main_content_panel.clear()
    self.main_content_panel.add_component(ProductPanel(current_user=self.current_user, 
                                                      current_role=self.current_role), 
                                          full_width_row=True)
    self.supplier_panel_btn.role = 'primary-color'
    self.product_panel_btn.role = 'raised'
    self.employee_panel_btn.role = 'primary-color'
    self.customer_panel_btn.role = 'primary-color'
    pass

  def employee_panel_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.main_content_panel.clear()
    self.main_content_panel.add_component(EmployeePanel(current_user=self.current_user, 
                                                      current_role=self.current_role), 
                                          full_width_row=True)
    self.supplier_panel_btn.role = 'primary-color'
    self.product_panel_btn.role = 'primary-color'
    self.employee_panel_btn.role = 'raised'
    self.customer_panel_btn.role = 'primary-color'
    pass

  def customer_panel_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.main_content_panel.clear()
    self.main_content_panel.add_component(CustomerPanel(current_user=self.current_user, 
                                                      current_role=self.current_role), 
                                          full_width_row=True)
    self.supplier_panel_btn.role = 'primary-color'
    self.product_panel_btn.role = 'primary-color'
    self.employee_panel_btn.role = 'primary-color'
    self.customer_panel_btn.role = 'raised'
    pass
    
