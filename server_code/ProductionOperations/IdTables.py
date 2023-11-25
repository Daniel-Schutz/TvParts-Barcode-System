import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

import json
# from ..LowLevelInterfaces import AWSInterface




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



def add_item_row(item_json):
  app_tables.items.add_row(**item_json)


@anvil.server.callable
def process_new_item(item_json, raw_qr_source):
  add_item_row(item_json)
  anvil.server.launch_background_task('add_s3_key_to_item', 
                                      item_json['item_id'], 
                                      raw_qr_source)
  

######## Background task - Add image to S3 ###############
  

@anvil.server.background_task
def add_s3_key_to_item(item_id, raw_qr_source):
  obj_key = anvil.server.call('get_s3_obj_key', raw_qr_source)
  item_row = app_tables.items.get(item_id=item_id)
  item_row['s3_object_key'] = obj_key


# @anvil.server.background_task
# def process_new_item_bk(item, raw_qr_source):
#     aws = AWSInterface(aws_access, aws_secret)
#     dyn_item_dict = aws.date_processor(item_dict)
#     obj_key_id = uuid.uuid4()
#     aws.create_item('unique_item', dyn_item_dict)
#     obj_key = aws.upload_image_from_url_to_s3(raw_qr_source, 
#                                               'barcode-system-storage-tvparts', 
#                                               'qr_images', 
#                                               obj_key_id)
#     print(obj_key)
#     key = {'item_id': item['item_id']}
#     update_expression = 'SET s3_object_key = :val'
#     expression_attribute_values = {':val': obj_key}
#     response = aws.update_item('unique_item', key, update_expression, expression_attribute_values)
#     print(response)
