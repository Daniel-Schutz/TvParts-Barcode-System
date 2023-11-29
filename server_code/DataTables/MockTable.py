import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def test_product_call():
  results = app_tables.products.search(sku=q.ilike("81421233%"))
  return results

@anvil.server.callable
def get_supplier_dropdown():
  results = app_tables.suppliers.search()
  return [(row['supplier_name'], row['supplier_name']) for row in results]

@anvil.server.callable
def get_unique_trucks():
  results = results_tables.mocktrucks.search()
  return list(set([row['truck_ID'] for row in results]))

@anvil.server.callable
def create_truck(truck_id, truck_created):
  app_tables.mocktrucks.add_row(truck_id = truck_id, truck_created=truck_created)



@anvil.server.callable
def test_db_search():
  # Create individual query objects for each condition
  # condition1 = q.like("%18%")
  # condition2 = q.like('product_id', "%8%")

  # # Combine the conditions using logical 'AND'
  # combined_conditions = condition1 & condition2

  # Execute the search with the combined conditions
  num_results = len(app_tables.products.search(sku=q.like("%"),
                                              product_name=q.like("%")))

  return num_results
