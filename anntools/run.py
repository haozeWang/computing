__author__ = 'Vas Vasiliadis <vas@uchicago.edu>'

import sys
import time
import driver
import boto3
import shutil
import json
# A rudimentary timer for coarse-grained profiling
class Timer(object):
        def __init__(self, verbose=False):
                self.verbose = verbose

        def __enter__(self):
                self.start = time.time()
                return self

        def __exit__(self, *args):
                self.end = time.time()
                self.secs = self.end - self.start
                self.msecs = self.secs * 1000  # millisecs
                if self.verbose:
                    print "Elapsed time: %f ms" % self.msecs

if __name__ == '__main__':
                    # Call the AnnTools pipeline
    if len(sys.argv) > 1:
        input_file_name = sys.argv[1]
        if len(sys.argv) > 2:
            job_id = sys.argv[2]
	    user_role = sys.argv[3]
	    email = sys.argv[4]
        with Timer() as t:
            driver.run(input_file_name, 'vcf')
        print "Total runtime: %s seconds" % t.secs
        s3 = boto3.resource('s3')
        path = str(input_file_name).split("/")
        path1 = str(input_file_name).split(".")[0].split("/")
        id = path[4].split("~")[0]
        s3.meta.client.upload_file(input_file_name+".count.log",'gas-results',"haoze/"+path[3]+"/"+id+"/"+path[5]+".count.log")
        s3.meta.client.upload_file(str(input_file_name).split(".")[0]+".annot.vcf",'gas-results',"haoze/"+path1[3]+"/"+id+"/"+path1[5]+".annot.vcf")
        shutil.rmtree(path[0]+"/"+path[1]+"/"+path[2]+"/"+path[3]+"/"+path[4])
        dynamodb = boto3.resource('dynamodb')
        ann_table = dynamodb.Table('haoze_annotations')
        time_now = str(time.time()).split(".")[0]
        ann_table.update_item(
            Key={
                'job_id': job_id
            },
            UpdateExpression="set job_status = :r, s3_results_bucket = :p, s3_key_result_file = :a, s3_key_log_file = :c, complete_time = :d",
            ExpressionAttributeValues={
                ":r": "COMPLETED",
                ":p": "gas-results",
                ":a": "haoze/"+path1[3]+"/"+id+"/"+path1[5]+".annot.vcf",
                ":c": "haoze/"+path[3]+"/"+id+"/"+path[5]+".count.log",
                ":d": time_now
            },
            ReturnValues="UPDATED_NEW"
        )
        data = {}
        data['complete_time'] = time_now
        data['job_id'] = job_id
        data['s3_key_result_file'] = "haoze/"+path1[3]+"/"+id+"/"+path1[5]+".annot.vcf"
        if user_role != "premium_user":
            client = boto3.client('sns', region_name='us-east-1')
            client.publish(
                TopicArn='arn:aws:sns:us-east-1:127134666975:haoze_save_glacier',
                Message=json.dumps({'default': json.dumps(data)}),
                MessageStructure='json'
            )
	data = {}
        data['job_id'] = job_id
        data["email"] = email
        client = boto3.client('sns', region_name='us-east-1')
        client.publish(
            TopicArn='arn:aws:sns:us-east-1:127134666975:haoze_job_results',
            Message=json.dumps({'default': json.dumps(data)}),
            MessageStructure='json'
        )
else:
    print 'A valid .vcf file must be provided as input to this program.'
