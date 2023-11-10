from ._anvil_designer import ChooseRoleTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime
import anvil.tz


class ChooseRole(ChooseRoleTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def teardown_button_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    pass

