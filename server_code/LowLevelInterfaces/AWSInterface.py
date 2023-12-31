import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

import os
import json
import pandas as pd
import boto3
import requests
import time
import uuid
import datetime
from decimal import Decimal
from botocore.exceptions import ClientError
from io import BytesIO
import logging

@anvil.server.callable
def get_s3_obj_key(raw_qr_source):
  aws_access = anvil.secrets.get_secret('aws_access')
  aws_secret = anvil.secrets.get_secret('aws_secret')
  aws = AWSInterface(aws_access, aws_secret)
  obj_key_id = uuid.uuid4()
  obj_key = aws.upload_image_from_url_to_s3(raw_qr_source, 
                                            'barcode-system-storage-tvparts', 
                                            'qr_images', 
                                            obj_key_id)
  return obj_key
  

@anvil.server.callable
#key = item_id for item sets
def set_value_in_dynamo(table_name, key, col_name, value):
  aws_access = anvil.secrets.get_secret('aws_access')
  aws_secret = anvil.secrets.get_secret('aws_secret')
  aws = AWSInterface(aws_access, aws_secret)
  return aws.simple_set_value(table_name, key, col_name, value)

@anvil.server.callable
def get_row_from_dynamo(table_name, key):
  aws_access = anvil.secrets.get_secret('aws_access')
  aws_secret = anvil.secrets.get_secret('aws_secret')
  aws = AWSInterface(aws_access, aws_secret)
  return_dict = aws.get_item(table_name, {'item_id': key})
  return return_dict

@anvil.server.callable
def store_qr_code(qr_source_url):
  aws_access = anvil.secrets.get_secret('aws_access')
  aws_secret = anvil.secrets.get_secret('aws_secret')
  aws = AWSInterface(aws_access, aws_secret)
  bucket_name = 'barcode-system-storage-tvparts'
  qr_code_id = str(uuid.uuid4())
  object_key = aws.upload_image_from_url_to_s3(qr_source_url, 
                                               bucket_name, 
                                               'qr_images', 
                                               qr_code_id)
  return object_key

@anvil.server.callable
def get_s3_image_url(object_key):
  aws_access = anvil.secrets.get_secret('aws_access')
  aws_secret = anvil.secrets.get_secret('aws_secret')
  aws = AWSInterface(aws_access, aws_secret)
  bucket_name = 'barcode-system-storage-tvparts'
  s3_source_url = aws.generate_presigned_url(bucket_name, str(object_key))
  return s3_source_url
  

class AWSInterface:
    
    def __init__(self, aws_access, aws_secret):
        self.resource = boto3.resource(
            'dynamodb',
            aws_access_key_id = aws_access,
            aws_secret_access_key = aws_secret,
            region_name = 'us-east-1'
        )
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access,
            aws_secret_access_key=aws_secret,
            region_name='us-east-1'
        )
        
        #Schema
        self.schemas = {
                'unique_item': {
                    'item_id': 'S',
                    'supplier_id': 'S',
                    'truck_id': 'S',
                    'box_id': 'S',
                    'item_serial': 'S',
                    'product_name': 'S',
                    'product_price': 'N',
                    'identified_by': 'S',
                    'created_date': 'N',
                    'verified_by': 'S',
                    'verified_time': 'N',
                    'lifecycle_status': 'S',
                    'order_id': 'S',
                    'testing_status': 'S',
                    'qr_object_key': 'S',
                }
            }

############ Higher Level Interface ###################
    def simple_set_value(self, table_name, item_id, col_name, value):
        key = {'item_id': item_id}
        update_expression = f'SET {col_name} = :val'
        value = self.value_processor(value)
        expression_attribute_values = {':val': value}
        response = self.update_item(table_name, key, 
                                    update_expression, expression_attribute_values)

    def process_new_item(self, item_dict, raw_qr_source, 
                         bucket='barcode-system-storage-tvparts', 
                         folder='qr_images'):
        dyn_item_dict = self.date_processor(item_dict)
        obj_key_id = uuid.uuid4()
        self.create_item('unique_item', dyn_item_dict)
        obj_key = self.upload_image_from_url_to_s3(raw_qr_source, 
                                                  bucket, 
                                                  folder, 
                                                  obj_key_id)
        print(obj_key)
        key = {'item_id': item['item_id']}
        update_expression = 'SET s3_object_key = :val'
        expression_attribute_values = {':val': obj_key}
        response = aws.update_item('unique_item', key, update_expression, expression_attribute_values)
        print(response)        
        
############ Helpers ##################################
    def date_processor(self, item_dict):
        new_dict = {}
        for k,v in item_dict.items():
            if type(v) == datetime.datetime:
                new_v = v.isoformat()
                new_dict[k] = new_v
            else:
                new_dict[k] = v
        return new_dict

    #Converts unsupported types for Dynamo
    def value_processor(self, v):
        if type(v) == datetime.datetime:
          new_v = v.isoformat()
          return new_v
        elif type(v) == float:
          new_v = Decimal(v)
          return new_v
        else:
          return v
        
############ BASIC CRUD ###############################
    
    def create_item(self, table_name, item):
        dynamodb = self.resource
        table = dynamodb.Table(table_name)
        response = table.put_item(Item=item)
        return response
        
    
    def get_item(self, table_name, key):
        dynamodb = self.resource
        table = dynamodb.Table(table_name)
        response = table.get_item(Key=key)
        return response.get('Item')
    
    def update_item(self, table_name, key, update_expression, expression_attribute_values):
        dynamodb = self.resource
        table = dynamodb.Table(table_name)
        response = table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )
        return response
    
    def delete_item(self, table_name, key):
        dynamodb = self.resource
        table = dynamodb.Table(table_name)
        response = table.delete_item(Key=key)
        return response
    
    def query_items(self, table_name, key_condition_expression, expression_attribute_values):
        dynamodb = self.resource
        table = dynamodb.Table(table_name)
        response = table.query(
            KeyConditionExpression=key_condition_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return response['Items']
    
##################################################################

######### Additional DB Operations ##################################
    def return_full_table(self, table_name):
        dynamodb = self.resource
        table = dynamodb.Table(table_name)
        response = table.scan()

        items = response['Items']

        # Continue scanning until all the data is retrieved
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])

        return items

    
    def list_tables(self):
        try:
            tables = []
            for table in self.resource.tables.all():
                print(table.name)
                tables.append(table)
        except ClientError as err:
            logger.error(
                "Couldn't list tables. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return tables
        
    def reset_table(self, table_name, partition_key):
        dynamodb = self.resource
        table = dynamodb.Table(table_name)
        table.delete()
        table.wait_until_not_exists()
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': partition_key,
                    'KeyType': 'HASH'  # 'HASH' type is for a partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': partition_key,
                    'AttributeType': 'S'  # 'S' stands for string
                }
            ],
            BillingMode='PAY_PER_REQUEST'  # Set the table to use on-demand billing
        )
        table.wait_until_exists()
        print(f"Table {table_name} was recreated as on-demand.")
        return None
##############################################################
            
############ Image Migration from qr maker to S3/Dynamo ######
    def upload_image_from_url_to_s3(self, image_url, bucket_name, folder_path, item_id):
        """
        Uploads an image from a URL directly to an S3 bucket without downloading it locally first,
        then updates the corresponding DynamoDB item with the S3 object key.
        """
        try:
            # Get the image from the URL
            response = requests.get(image_url, stream=True)
            response.raise_for_status()  # Ensure we notice bad responses
            
            # Upload the image directly from the stream
            object_name = f"{folder_path}/{item_id}.jpg"  # The S3 object key
            self.s3_client.upload_fileobj(response.raw, bucket_name, object_name)
            
            # No need to close the response if you use 'with', Python will handle it.
            
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return False
        except ClientError as e:
            logging.error(e)
            return False
        except Exception as err:
            print(f"Other error occurred: {err}")
            return False

        # If success, return the S3 object key
        return object_name
    
    #Run this everytime we need to get a source url 
    def generate_presigned_url(self, bucket_name, object_key, expiration=3600):
        """Generate a presigned URL for an S3 object."""
        try:
            response = self.s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': bucket_name,
                                                                'Key': object_key},
                                                        ExpiresIn=expiration)
        except ClientError as e:
            logging.error(e)
            return None

        # The response contains the presigned URL
        return response
