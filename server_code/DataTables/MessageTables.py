import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import uuid

@anvil.server.callable
def get_quick_msg_dropdown():
  results = app_tables.quickmessages.search()
  return [row['quick_msg_text'] for row in results]

@anvil.server.callable
def get_roles_dropdown():
  results = app_tables.roles.search()
  return [row['role'] for row in results]


########### Send Side Functions ##########################
@anvil.server.callable
def create_message(user_from, role_from, role_to, message_body, associated_part):
  app_tables.messages.add_row(
    user_from=user_from,
    role_from=role_from,
    message_id=str(uuid.uuid4()),
    role_to=role_to,
    message_body=message_body,
    associated_part=associated_part,
    complete=False
  )
##########################################################


########### Recieve Side Functions #######################
@anvil.server.callable
def get_role_recieved_msgs(role_to):
  return app_tables.messages.search(
    complete=False,
    role_to=role_to
  )
##########################################################
