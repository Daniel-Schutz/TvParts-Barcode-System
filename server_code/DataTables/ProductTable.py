import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_product_by_sku(input_sku):
  result_row = app_tables.products.get(sku=input_sku)
  return result_row

@anvil.server.callable
def get_type_dropdown():
  results = app_tables.product_type.search()
  types = [(row['type'], row['type']) for row in results]
  types.append(('All Types', 'All Types'))
  types.sort()
  return types

@anvil.server.callable
def run_product_explorer_query(product_name_t, 
                               product_name_search_type, 
                               sku_t, sku_search_type, 
                               product_type_t):
  query_conditions = []
    
    # Add conditions based on input fields and search type
  if product_name_t:
    if product_name_search_type == 'Contains':
      product_name_query = f"%{product_name_t}%"
    else:
      product_name_query = product_name_t
  else:
    product_name_query = '%'

  if sku_t:
    if sku_search_type == 'Contains':
      sku_query = f"%{sku_t}%"
    else:
      sku_query = sku_t
  else:
    sku_query = "%"
  
  if product_type_t == 'All Types':
    type_query = "%"
  else:
    type_query = product_type_t
  
  
  # Execute the search with the combined query
  results = app_tables.products.search(product_name = q.ilike(product_name_query), 
                                       sku = q.ilike(sku_query),
                                       type = q.ilike(type_query)
                                      )
  
  # Return the matching results
  return results