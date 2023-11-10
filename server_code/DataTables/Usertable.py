import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:


#Check User Role
@anvil.server.callable
def get_user_role():
  user = anvil.users.get_user()
  return user['role']

#Set User Role from Role Page
@anvil.server.callable
def set_user_role(role):
  user = anvil.users.get_user()
  if user is not None:
    user['role'] = role
    user.update()