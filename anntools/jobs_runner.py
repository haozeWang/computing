import boto3
import os
import json
import subprocess
sqs = boto3.resource('sqs')
subprocess.Popen('python /home/ubuntu/anntools/result_notify.py', shell = True)
subprocess.Popen('python /home/ubuntu/anntools/monitor.py', shell = True)
subprocess.Popen('python /home/ubuntu/anntools/download.py', shell = True)
queue = sqs.get_queue_by_name(QueueName = 'haoze_job_requests')
while True:
    messages = queue.receive_messages(WaitTimeSeconds=20)
    if len(messages) > 0:
        for message in messages:
            mess = json.loads(message.body)['Message']
            data = json.loads(mess)
            user = data["username"]
            job_id = data["job_id"]
            input_file = data["input_file_name"]
            path = data["s3_key_input_file"]
            file_name = path.split("/")[1]
            if (os.path.exists("/home/ubuntu/" + user) == False):
                os.mkdir("/home/ubuntu/" + user)
            os.mkdir("/home/ubuntu/" + user + "/" + job_id)
            resource = boto3.resource('s3')
            my_bucket = resource.Bucket('gas-inputs')
            my_bucket.download_file(path, "/home/ubuntu/" + user + "/" + job_id + "/" + file_name)
            temp = "/home/ubuntu/" + user + "/" + job_id + "/" + job_id + "~" + input_file
            user_role = data["user_role"]
            p = subprocess.Popen('python /home/ubuntu/anntools/run.py ' + temp + " " + job_id+ " " + user_role + " " + data["email"], shell=True)

            dynamodb = boto3.resource('dynamodb')
            ann_table = dynamodb.Table('haoze_annotations')
            ann_table.update_item(
                Key={
                    'job_id': job_id
                },
                UpdateExpression="set job_status = :r",
                ExpressionAttributeValues={
                    ":r": "RUNNING"
                }

            )
            message.delete()
    else:
        continue

