import boto3
import os
import json
import subprocess
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName = 'haoze_job_results')
while True:
    messages = queue.receive_messages(WaitTimeSeconds=20)
    if len(messages) > 0:
        for message in messages:
            mess = json.loads(message.body)['Message']
            data = json.loads(mess)
            job_id = data["job_id"]
            email = data["email"]
            client = boto3.client('ses')
            url = 'https://haoze.ucmpcs.org:4433/annotations/'+job_id
            infor = 'Your job '+ job_id+'  is finished. Yo can click this link to diaplay job details.\n' + url
            response = client.send_email(
                Source = 'haoze@ucmpcs.org',
                Destination={
                    'ToAddresses': [
                        email,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': 'UTF-8',
                            'Data':"Your job " + job_id+ " is finished. Click this link to view"+"<a href= "+url+">Link</a>",
                        },
                        'Text': {
                            'Charset': 'UTF-8',
                            'Data': 'Your job '+ job_id+' is finished. Yo can click this link to diaplay job details.\n' + url
                        },
                    },
                    'Subject': {
                        'Charset': 'UTF-8',
                        'Data':  'Job request finished'
                    },
                },
            )
            message.delete()
    else:
        continue



