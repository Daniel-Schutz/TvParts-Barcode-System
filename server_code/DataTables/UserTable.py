import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


#Check User Role
@anvil.server.callable
def get_user_role():
  user = anvil.users.get_user()
  return user['role']

#Get user full name
@anvil.server.callable
def get_user_full_name():
  user = anvil.users.get_user()
  if user['first_name'] is not None and user['last_name'] is not None:
    return user['first_name'] + " " + user['last_name']
  else:
    return None

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