import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

import json
from ..LowLevelInterfaces import AWSInterface

@anvil.server.callable
def get_make_dropdown():
  results = app_tables.tv_makes.search()
  return [(row['make'], row['make']) for row in results]

@anvil.server.callable
def get_year_dropdown():
  results = app_tables.years.search()
  return [(str(row['year']), row['year']) for row in results]

@anvil.server.callable
def get_size_dropdown():
  results = app_tables.tv_sizes.search()
  return [(row['size'], row['size']) for row in results]

########## Data Retrievals from Page Interactions #############
@anvil.server.callable
def get_supplier_truck_from_code(truck_code):
  truck_code = json.loads(truck_code)
  truck_id = truck_code['truck']
  results = app_tables.trucks.search(truck_id=truck_id)
  row = [item for item in results][0]
  supplier = row['supplier_name']
  truck = row['truck_id']
  return supplier, truck

######## Background task - Add item to Dynamo/S3 ###############
@anvil.server.callable
def process_new_item(item, raw_qr_source):
  anvil.server.launch_background_task('process_new_item_bk', 
                                      item, 
                                      raw_qr_source)

@anvil.server.background_task
def process_new_item_bk(item, raw_qr_source):
    aws = AWSInterface(aws_access, aws_secret)
    dyn_item_dict = aws.date_processor(item_dict)
    obj_key_id = uuid.uuid4()
    aws.create_item('unique_item', dyn_item_dict)
    obj_key = aws.upload_image_from_url_to_s3(raw_qr_source, 
                                              'barcode-system-storage-tvparts', 
                                              'qr_images', 
                                              obj_key_id)
    print(obj_key)
    key = {'item_id': item['item_id']}
    update_expression = 'SET s3_object_key = :val'
    expression_attribute_values = {':val': obj_key}
    response = aws.update_item('unique_item', key, update_expression, expression_attribute_values)
    print(response)
