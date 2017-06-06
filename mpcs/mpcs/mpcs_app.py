# mpcs_app.py
#
# Copyright (C) 2011-2017 Vas Vasiliadis
# University of Chicago
#
# Application logic for the GAS
#
##
__author__ = 'Vas Vasiliadis <vas@uchicago.edu>'

import base64
import datetime
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

from mpcs_utils import log, auth
from bottle import route, request, redirect, template, static_file

'''
*******************************************************************************
Set up static resource handler - DO NOT CHANGE THIS METHOD IN ANY WAY
*******************************************************************************
'''
@route('/static/<filename:path>', method='GET', name="static")
def serve_static(filename):
  # Tell Bottle where static files should be served from
  return static_file(filename, root=request.app.config['mpcs.env.static_root'])

'''
*******************************************************************************
Home page
*******************************************************************************
'''
@route('/', method='GET', name="home")
def home_page():
  return template(request.app.config['mpcs.env.templates'] + 'home', auth=auth)

'''
*******************************************************************************
Registration form
*******************************************************************************
'''
@route('/register', method='GET', name="register")
def register():
  log.info(request.url)
  return template(request.app.config['mpcs.env.templates'] + 'register',
    auth=auth, name="", email="", username="", 
    alert=False, success=True, error_message=None)

@route('/register', method='POST', name="register_submit")
def register_submit():
  try:
    auth.register(description=request.POST.get('name').strip(),
                  username=request.POST.get('username').strip(),
                  password=request.POST.get('password').strip(),
                  email_addr=request.POST.get('email_address').strip(),
                  role="free_user")
  except Exception, error:
    return template(request.app.config['mpcs.env.templates'] + 'register', 
      auth=auth, alert=True, success=False, error_message=error)  

  return template(request.app.config['mpcs.env.templates'] + 'register', 
    auth=auth, alert=True, success=True, error_message=None)

@route('/register/<reg_code>', method='GET', name="register_confirm")
def register_confirm(reg_code):
  log.info(request.url)
  try:
    auth.validate_registration(reg_code)
  except Exception, error:
    return template(request.app.config['mpcs.env.templates'] + 'register_confirm',
      auth=auth, success=False, error_message=error)

  return template(request.app.config['mpcs.env.templates'] + 'register_confirm',
    auth=auth, success=True, error_message=None)

'''
*******************************************************************************
Login, logout, and password reset forms
*******************************************************************************
'''
@route('/login', method='GET', name="login")
def login():
  log.info(request.url)
  redirect_url = "/annotations"
  # If the user is trying to access a protected URL, go there after auhtenticating
  if request.query.redirect_url.strip() != "":
    redirect_url = request.query.redirect_url

  return template(request.app.config['mpcs.env.templates'] + 'login', 
    auth=auth, redirect_url=redirect_url, alert=False)

@route('/login', method='POST', name="login_submit")
def login_submit():
  auth.login(request.POST.get('username'),
             request.POST.get('password'),
             success_redirect=request.POST.get('redirect_url'),
             fail_redirect='/login')

@route('/logout', method='GET', name="logout")
def logout():
  log.info(request.url)
  auth.logout(success_redirect='/login')
   

'''
*******************************************************************************
*
CORE APPLICATION CODE IS BELOW...
*
*******************************************************************************
'''

'''
*******************************************************************************
Subscription management handlers
*******************************************************************************
'''
import stripe

# Display form to get subscriber credit card info
@route('/subscribe', method='GET', name="subscribe")
def subscribe():
  return template(request.app.config['mpcs.env.templates'] + 'subscribe', auth = auth)

# Process the subscription request
@route('/subscribe', method='POST', name="subscribe_submit")
def subscribe_submit():
  log.info(request.url)
  items = request.forms.get('stripe_token')
  stripe.api_key = request.app.config['mpcs.stripe.secret_key']

  customer_response = stripe.Customer.create(
    source= items,
  )
  stripe.Subscription.create(
  customer=customer_response["id"],
  plan="premium_plan"
  )
  auth.current_user.update(role="premium_user")
  dynamodb = boto3.resource('dynamodb',region_name=request.app.config['mpcs.aws.app_region'])
  ann_table = dynamodb.Table('haoze_annotations')
  response = ann_table.scan(FilterExpression=Attr('username').eq(auth.current_user.username))
  items = response['Items']
  amount = response["Count"]
  client = boto3.client('glacier',region_name="us-east-1")
  for i in range(0,amount):
    if 'results_file_archive_id' in items[i]: 
      response = client.initiate_job(
                           vaultName='ucmpcs',
                           jobParameters={'Type': "archive-retrieval",'ArchiveId': items[i]["results_file_archive_id"],'Description': items[i]["s3_key_result_file"],'SNSTopic': "arn:aws:sns:us-east-1:127134666975:haoze_result_glacier",'Tier':"Expedited"}
                          )
      










'''
*******************************************************************************
Display the user's profile with subscription link for Free users
*******************************************************************************
'''
@route('/profile', method='GET', name="profile")
def user_profile():
  log.info(request.url)
  return template(request.app.config['mpcs.env.templates'] + 'profile', auth = auth, username = auth.current_user.username, fullname = auth.current_user.description, subscription= auth.current_user.role)



'''
*******************************************************************************
Creates the necessary AWS S3 policy document and renders a form for
uploading an input file using the policy document
*******************************************************************************
'''
@route('/annotate', method='GET', name="annotate")
def upload_input_file():
  log.info(request.url)

  # Check that user is authenticated
  auth.require(fail_redirect='/login?redirect_url=' + request.url)
   
  # Use the boto session object only to get AWS credentials
  session = botocore.session.get_session()
  aws_access_key_id = str(session.get_credentials().access_key)
  aws_secret_access_key = str(session.get_credentials().secret_key)
  aws_session_token = str(session.get_credentials().token)

  # Define policy conditions
  bucket_name = request.app.config['mpcs.aws.s3.inputs_bucket']
  encryption = request.app.config['mpcs.aws.s3.encryption']
  acl = request.app.config['mpcs.aws.s3.acl']

  # Generate unique ID to be used as S3 key (name)
  key_name = request.app.config['mpcs.aws.s3.key_prefix'] + str(uuid.uuid4())

  # Redirect to a route that will call the annotator
  redirect_url = str(request.url) + "/job"

  # Define the S3 policy doc to allow upload via form POST
  # The only required elements are "expiration", and "conditions"
  # must include "bucket", "key" and "acl"; other elements optional
  # NOTE: We also must inlcude "x-amz-security-token" since we're
  # using temporary credentials via instance roles
  policy_document = str({
    "expiration": (datetime.datetime.utcnow() + 
      datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "conditions": [
      {"bucket": bucket_name},
      ["starts-with","$key", key_name],
      ["starts-with", "$success_action_redirect", redirect_url],
      {"x-amz-server-side-encryption": encryption},
      {"x-amz-security-token": aws_session_token},
      {"acl": acl}]})

  # Encode the policy document - ensure no whitespace before encoding
  policy = base64.b64encode(policy_document.translate(None, string.whitespace))

  # Sign the policy document using the AWS secret key
  signature = base64.b64encode(hmac.new(aws_secret_access_key, policy, hashlib.sha1).digest())

  # Render the upload form
  # Must pass template variables for _all_ the policy elements
  # (in addition to the AWS access key and signed policy from above)
  return template(request.app.config['mpcs.env.templates'] + 'upload',
    auth=auth, bucket_name=bucket_name, s3_key_name=key_name,
    aws_access_key_id=aws_access_key_id,     
    aws_session_token=aws_session_token, redirect_url=redirect_url,
    encryption=encryption, acl=acl, policy=policy, signature=signature)


'''
*******************************************************************************
Accepts the S3 redirect GET request, parses it to extract 
required info, saves a job item to the database, and then
publishes a notification for the annotator service.
*******************************************************************************
'''
@route('/annotate/job', method='GET')
def create_annotation_job_request():
  bucket = str(request.query.get('bucket'))
  key = str(request.query.get('key'))
  key_dic = key.split("/")
  id = key_dic[1].split("~")
  file_name = str(id[1]).split(".")
  time_now = str(time.time()).split(".")[0]
  data = {}
  data["job_id"] = id[0]
  data["username"] = auth.current_user.username
  data["input_file_name"] = id[1]
  data["s3_inputs_bucket"] = bucket
  data["s3_key_input_file"] = key
  data["submit_time"] = time_now
  data["job_status"] = "PENDING"
  dynamodb = boto3.resource('dynamodb',region_name=request.app.config['mpcs.aws.app_region'])
  ann_table = dynamodb.Table('haoze_annotations')
  ann_table.put_item(Item=data)
  client = boto3.client('sns',region_name=request.app.config['mpcs.aws.app_region'])
  data["user_role"] = auth.current_user.role
  data["email"] = auth.current_user.email_addr
  client.publish(
    TopicArn='arn:aws:sns:us-east-1:127134666975:haoze_job_request_notify',
    Message =json.dumps({'default': json.dumps(data)}),
    MessageStructure = 'json'
  )
  return template(request.app.config['mpcs.env.templates']+'upload_confirm',auth = auth, job_id = id[0])


'''
*******************************************************************************
List all annotations for the user
*******************************************************************************
'''
@route('/annotations', method='GET', name="annotations_list")
def get_annotations_list():
  log.info(request.url)
  auth.require(fail_redirect='/login?redirect_url=' + request.url)
  dynamodb = boto3.resource('dynamodb',region_name=request.app.config['mpcs.aws.app_region'])
  ann_table = dynamodb.Table('haoze_annotations')
  response = ann_table.query(IndexName='username_index', KeyConditionExpression=Key('username').eq(auth.current_user.username))
  items = response['Items']
  for i in items:
    i["submit_time"] = datetime.datetime.fromtimestamp(int(i["submit_time"])).strftime('%Y-%m-%d %H:%M')
  return template(request.app.config['mpcs.env.templates'] + 'annotations_list',auth = auth,items = json.dumps(items), num = len(items))
  
'''
*******************************************************************************
Display details of a specific annotation job
*******************************************************************************
'''
@route('/annotations/<job_id>', method='GET', name="annotation_details")
def get_annotation_details(job_id):
  log.info(request.url)
  auth.require(fail_redirect='/login?redirect_url=' + request.url)
  dynamodb = boto3.resource('dynamodb',region_name=request.app.config['mpcs.aws.app_region'])
  ann_table = dynamodb.Table('haoze_annotations')
  response = ann_table.query(KeyConditionExpression=Key('job_id').eq(job_id))
  item = json.loads(json.dumps(response['Items']))
  if(item[0]["username"] != auth.current_user.username): 
    return template(request.app.config['mpcs.env.templates'] + 'no_authorized', auth = auth)
  elif 'complete_time' not in item[0]:
    return template(request.app.config['mpcs.env.templates'] + 'annotations_detail',auth = auth, request_id = job_id,
      request_time = datetime.datetime.fromtimestamp(int(item[0]["submit_time"])).strftime('%Y-%m-%d %H:%M') , input_file = item[0]["input_file_name"], status = item[0]["job_status"], compelte_time = "0",url ="",job_id = 0,file_local = '')
  else: 
    s3 = boto3.client('s3',region_name=request.app.config['mpcs.aws.app_region'])
    path = s3.generate_presigned_url(
       ClientMethod='get_object',
        Params={
        'Bucket': request.app.config['mpcs.aws.s3.results_bucket'],
        'Key': item[0]["s3_key_result_file"]
        }
    )
    if auth.current_user.role != "premium_user":
      if 'results_file_archive_id' in item[0]:
        return template(request.app.config['mpcs.env.templates'] + 'annotations_detail',auth = auth, request_id = job_id,
      request_time = datetime.datetime.fromtimestamp(int(item[0]["submit_time"])).strftime('%Y-%m-%d %H:%M'), input_file = item[0]["input_file_name"], status = item[0]["job_status"], compelte_time = datetime.datetime.fromtimestamp(int(item[0]["complete_time"])).strftime('%Y-%m-%d %H:%M'),url =path,job_id = job_id,file_local= 'glacier')
      else:
         return template(request.app.config['mpcs.env.templates'] + 'annotations_detail',auth = auth, request_id = job_id,
      request_time = datetime.datetime.fromtimestamp(int(item[0]["submit_time"])).strftime('%Y-%m-%d %H:%M'), input_file = item[0]["input_file_name"], status = item[0]["job_status"], compelte_time = datetime.datetime.fromtimestamp(int(item[0]["complete_time"])).strftime('%Y-%m-%d %H:%M'),url =path,job_id = job_id,file_local = 's3')
    else:
      return template(request.app.config['mpcs.env.templates'] + 'annotations_detail',auth = auth, request_id = job_id,
      request_time = datetime.datetime.fromtimestamp(int(item[0]["submit_time"])).strftime('%Y-%m-%d %H:%M'), input_file = item[0]["input_file_name"], status = item[0]["job_status"], compelte_time = datetime.datetime.fromtimestamp(int(item[0]["complete_time"])).strftime('%Y-%m-%d %H:%M'),url =path,job_id = job_id,file_local = 's3')


  

'''
*******************************************************************************
Display the log file for an annotation job
*******************************************************************************
'''
@route('/annotations/<job_id>/log', method='GET', name="annotation_log")
def view_annotation_log(job_id):
    log.info(request.url)
    auth.require(fail_redirect='/login?redirect_url=' + request.url)
    dynamodb = boto3.resource('dynamodb',region_name=request.app.config['mpcs.aws.app_region'])
    ann_table = dynamodb.Table('haoze_annotations')
    response = ann_table.query(KeyConditionExpression=Key('job_id').eq(job_id))
    item = json.loads(json.dumps(response['Items']))
    s3 = boto3.resource('s3',region_name=request.app.config['mpcs.aws.app_region'])
    object = s3.Object(request.app.config['mpcs.aws.s3.results_bucket'],item[0]["s3_key_log_file"])
    content = object.get()["Body"].read()  
    return template(request.app.config['mpcs.env.templates'] + 'annotations_log_detail', auth = auth, content = content)



### EOF

