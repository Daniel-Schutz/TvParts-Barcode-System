import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

#Upload data to table from Jupyter via Uplink
@anvil.server.callable
def import_data_to_anvil(records):
    for record in records:
        app_tables.products.add_row(**record)