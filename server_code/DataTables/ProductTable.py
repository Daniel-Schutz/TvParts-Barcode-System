import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import re

@anvil.server.callable
def get_product_by_sku(input_sku):
  print("input sku", input_sku)
  result_row = app_tables.products.search(sku=input_sku)
  return result_row[0]

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
                               product_description_t,
                               desc_search_type,
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

                                 
  if product_description_t:
    if desc_search_type == 'Contains':
      product_description_query = f"%{product_description_t}%"
    else:
       product_description_query = product_description_t
  else:
    product_description_query = "%"
    
  
  if product_type_t == 'All Types':
    type_query = "%"
  else:
    type_query = product_type_t
  
  # Execute the search with the combined query
  results = app_tables.products.search(product_name = q.ilike(product_name_query), 
                                       sku = q.ilike(sku_query),
                                       description= q.ilike(product_description_query),
                                       type = q.ilike(type_query)
                                      )
  for result in results:
    anvil.server.call('add_product_qr_url',result['s3_object_key'])

  results = app_tables.products.search(product_name = q.ilike(product_name_query), 
                                       sku = q.ilike(sku_query),
                                       description= q.ilike(product_description_query),
                                       type = q.ilike(type_query)
                                      )                          
  # Return the matching results
  return results


@anvil.server.callable
def update_description():
  anvil.server.launch_background_task('update_description_bk')

@anvil.server.background_task
def update_description_bk():
  products = app_tables.products.search()
  for row in products:
    if row['product_id'] is not None and row['description'] == '':
      part_info = anvil.server.call('get_part_info_from_shopify',row['product_id'])
      if part_info is not None:
        raw_description = part_info['body_html']
        if raw_description is not None:
          description = re.sub(r'<.*?>|\n', '', raw_description)
          row.update(description=description)  
    


