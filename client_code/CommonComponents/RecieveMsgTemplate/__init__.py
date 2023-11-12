from ._anvil_designer import RecieveMsgTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RecieveMsgTemplate(RecieveMsgTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # self.from_name_box.text = self.item['user_from']
    # self.from_role_box.text = self.item['role_from']
    # self.message_text.text = self.item['message_body']
    # self.item_detail_text = self.item['associated_part']
    # Any code you write here will run before the form opens.

  def button_mark_complete_click(self, **event_args):
    print("Inside mark Complete")
    print(self.item['message_id'])
    anvil.server.call('mark_message_complete', self.item['message_id'])
    self.parent.raise_event('x-refresh-messages')