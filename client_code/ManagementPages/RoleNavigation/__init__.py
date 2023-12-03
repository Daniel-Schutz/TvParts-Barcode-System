from ._anvil_designer import RoleNavigationTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...ProductionPages.TeardownModule import TeardownModule

class RoleNavigation(RoleNavigationTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.selected_color = '#236F65'
    self.open_color = '#3FA498'

    # Any code you write here will run before the form opens.

#### Change views (evets and logic) ########################
  def teardown_view(self):
    self.role_page_view_panel.add_component(TeardownModule())
    self.teardown_role_btn.background = self.selected_color
    self.id_role_btn.background = self.open_color
    self.warehouse_pick_role_btn.background = self.open_color
    self.warehouse_stock_role_btn.background = self.open_color
    self.testing_role_btn.background = self.open_color
    self.shipping_role_btn.background = self.open_color
    self.all_inboxes_btn.background = self.open_color


####### Messages (events and logic) ########################