from ._anvil_designer import ContactTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from time import sleep


class Contact(ContactTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.email = self.item['user']['email']
    self.rich_text_1.add_component(Label(text=self.item['name']), slot='name')
    self.rich_text_1.add_component(Label(text=self.email), slot='email')
    # Any code you write here will run when the form opens.

  def send_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.text_area_1.text:
      anvil.server.call('send_email', self.email, self.text_area_1.text, self.subject_textbox.text)
      self.text_area_1.text = ""
      self.subject_textbox.text = ""
      self.send_button.visible = False
      self.sent_label.visible = True
      sleep(2)
      self.send_button.visible = True
      self.sent_label.visible = False

