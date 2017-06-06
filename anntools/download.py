import boto3
import time 
from boto3.dynamodb.conditions import Key, Attr



client = boto3.client('sqs',region_name='us-east-1')

while(True) :
	response = client.receive_message(QueueUrl="https://sqs.us-east-1.amazonaws.com/127134666975/haoze_retrive",MaxNumberOfMessages=1,VisibilityTimeout=20,WaitTimeSeconds=20)
	if response.has_key("Messages"):
		data = response["Messages"][0]["Body"]
		recipe = response["Messages"][0]["ReceiptHandle"]
		items = data.split("\\\"")

		job_id = items[35]
		archive_id = items[7]

		# client.delete_message(QueueUrl="arn:aws:sqs:us-east-1:127134666975:haoze_glacier_retrive",ReceiptHandle=receipt)
		glacier = boto3.client('glacier',region_name="us-east-1")
		result = glacier.get_job_output(
    					vaultName='ucmpcs',
                        jobId = job_id
				)
		dynamodb = boto3.resource('dynamodb',region_name="us-east-1")
  		ann_table = dynamodb.Table('haoze_annotations')
  		response = ann_table.scan(FilterExpression=Attr('results_file_archive_id').eq(archive_id))
  		items = response['Items']
  		key = items[0]["s3_key_result_file"]
  		content = result["body"].read()
  		file = open("/home/ubuntu/test.annot.vcf","w+")
  		file.write(content)
  		s3 = boto3.resource('s3',region_name='us-east-1')
  		s3.meta.client.upload_file("/home/ubuntu/test.annot.vcf",'gas-results',key)
		client.delete_message(QueueUrl="https://sqs.us-east-1.amazonaws.com/127134666975/haoze_retrive",ReceiptHandle=recipe)
