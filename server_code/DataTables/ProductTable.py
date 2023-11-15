import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def run_product_explorer_query(product_name_t, 
                               product_name_search_type, 
                               sku_t, sku_search_type, 
                               vendor, product_type):
  query_conditions = []
    
    # Add conditions based on input fields and search type
  if product_name_t:
    if product_name_search_type == 'Contains':
      query_conditions.append(product_name = q.ilike(f"%{product_name_t}%"))
    else:
      query_conditions.append(q.ilike(f"{product_name}"))

  if sku_t:
    if sku_search_type == 'Contains':
      query_conditions.append(sku=q.ilike(f"%{sku_t}%))
    else:
      query_conditions.append(q.sku == sku)
  
  # Vendor and Type are dropdowns, so they will be exact matches
  if vendor:
      query_conditions.append(q.vendor == vendor)
  
  if product_type:
      query_conditions.append(q.type == product_type)
  
  # Combine all the conditions with an 'AND' operator
  combined_query = q.AND(*query_conditions)
  
  # Execute the search with the combined query
  results = app_tables.products.search(combined_query)
  
  # Return the matching results
  return results