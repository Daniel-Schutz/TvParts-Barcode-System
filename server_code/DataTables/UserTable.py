import anvil.secrets
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

#Check User First Name
@anvil.server.callable
def get_user_first_name():
  user = anvil.users.get_user()
  return user['first_name']

#Check User Last Name
@anvil.server.callable
def get_user_last_name():
  user = anvil.users.get_user()
  return user['last_name']

#Set User Role from Role Page
@anvil.server.callable
def set_user_role(role):
  user = anvil.users.get_user()
  if user is not None:
    user['role'] = role
    user.update()

@anvil.server.callable
def set_user_first_name(first_name):
  user = anvil.users.get_user()
  if user is not None:
    user['first_name'] = first_name
    user.update()

@anvil.server.callable
def set_user_last_name(last_name):
  user = anvil.users.get_user()
  if user is not None:
    user['last_name'] = last_name
    user.update()