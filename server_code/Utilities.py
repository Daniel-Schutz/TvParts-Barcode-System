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
def check_admin():
  return anvil.users.get_user()['admin']
  
@anvil.server.callable
def check_user_exists(email):
  return bool(app_tables.users.get(email=email))

@anvil.server.callable
def create_dataframe_from_table(table_name):
    table = getattr(app_tables, table_name)
    rows_list = [{column: getattr(row, column) for column in row} for row in table.search()]
    df = pd.DataFrame(rows_list)
    return df