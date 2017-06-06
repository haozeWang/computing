import base64
from datetime import datetime
import hashlib
import hmac
import json
import sha
import string
import time
import urllib
import urlparse
import uuid
import boto3
import botocore.session
from boto3.dynamodb.conditions import Key


from bottle import route, request, redirect, template, static_file

while(True) :
	dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
  	ann_table = dynamodb.Table('haoze_annotations')
  	response = ann_table.scan()
  	items = response['Items']
  	for item in items:
  		if 'complete_time' not in item:
  			continue
  		if 'results_file_archive_id' in item:
  			continue
  		if 'subscribe_level' in item:
  			continue
  		tiCom = datetime.fromtimestamp(float(item['complete_time']))
  		tiNow = datetime.now()
  		if(int(round((tiNow-tiCom).total_seconds() / 60)) > 30):
  			client = boto3.client('glacier',region_name='us-east-1')
  			s3 = boto3.resource('s3',region_name='us-east-1')
    			object = s3.Object(gas-results,item["s3_key_result_file"])
    			content = object.get()["Body"].read()  
    			response = client.upload_archive(
    				accountId='-',
    				archiveDescription='string',
    				body=content,
    				vaultName=item["s3_key_result_file"],
			)
			print(response["archiveId"])
			ann_table.update_item(
            			Key={
                		'job_id': item["job_id"]
            			},
            			UpdateExpression="set results_file_archive_id = :r",
            			ExpressionAttributeValues={
                		":r": response["archiveId"]
            		},
            		ReturnValues="UPDATED_NEW"
        		)











