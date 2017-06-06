import boto3
import os
import json
import subprocess
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName = 'haoze_job_requests')
while True:
    messages = queue.receive_messages(WaitTimeSeconds=20)
    if len(messages) > 0:
        for message in messages:
		message.delete()
