from ._anvil_designer import BookAlertTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class BookAlert(BookAlertTemplate):
  def __init__(self, time, require_email, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.datetime_label.text = time.strftime("%A %d %b %Y at %I:%M %p")
    #only show email box if admin
    self.email_box.visible = require_email
    self.email_label.visible = require_email

    




