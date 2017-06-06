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

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName = 'haoze_save_to_glacier')
while True:
    messages = queue.receive_messages(WaitTimeSeconds=20)
    if len(messages) > 0:
      for message in messages:
        mess = json.loads(message.body)['Message']
        item = json.loads(mess)
        tiCom = datetime.fromtimestamp(float(item['complete_time']))
        tiNow = datetime.now()
        if(int(round((tiNow-tiCom).total_seconds() / 60)) > 30):
          client = boto3.client('glacier',region_name='us-east-1')
          s3 = boto3.resource('s3',region_name='us-east-1')
          object = s3.Object("gas-results",item["s3_key_result_file"])
          content = object.get()["Body"].read()  
          response = client.upload_archive(
            accountId='-',
            archiveDescription='string',
            body=content,
            vaultName="ucmpcs",
          )
          dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
          ann_table = dynamodb.Table('haoze_annotations')
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
	  client = boto3.client('s3')
	  client.delete_object(
              Bucket='gas-results',
              Key=item["s3_key_result_file"],
            )
          message.delete()
