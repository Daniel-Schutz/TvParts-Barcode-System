import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import calendar
import datetime
import anvil.tz
import pytz


@anvil.server.callable
def send_email(email, body, subject):
  if not subject:
    subject = "A Message about your Booking"
  anvil.email.send(from_name="Booking App Team", 
                   to=email, 
                   subject=subject,
                   text=body)

@anvil.server.callable
def check_admin():
  return anvil.users.get_user()['admin']
  
@anvil.server.callable
def update_settings_table(key, value):
  app_tables.settings.get(key=key)['value'] = value
  
@anvil.server.callable
def check_user_exists(email):
  return bool(app_tables.users.get(email=email))