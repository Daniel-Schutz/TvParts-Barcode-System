from ._anvil_designer import QRPrintTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class QRPrintTemplate(QRPrintTemplateTemplate):
  def __init__(self, source, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    #self.img_source = source
    self.image_1.source = source

    # Any code you write here will run before the form opens.
