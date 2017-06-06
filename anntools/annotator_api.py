
from bottle import get, post, request, error, run, response, template
import uuid
import cgi
import os
import json
import subprocess
import shutil
import base64
import boto3
import hmac
import hashlib
import datetime
@post('/annotations')
def run_file():
    FileName = request.forms.get('File')
    if (os.path.exists("/home/ubuntu/anntools/data/" + str(FileName))):
        id = str(uuid.uuid1())
        info = {}
        info["code"] = "200 OK"
        data = {}
        data["Job_id"] = str(id)
        data["input_file"] = str(FileName)
        info["data"] = data
        jsondata = json.dumps(info)
        os.makedirs(id)
        temp = "/home/ubuntu/anntools/data/" + str(FileName)
        shutil.copy(temp,"/home/ubuntu/anntools/"+id)
        temp = "/home/ubuntu/anntools/" + id +"/"+ str(FileName)
        if (os.path.exists("./record.txt")):
            file = open("record.txt", "a")
            file.write(str(id) + " " + str(FileName) + " \n")
            file.close()
        else:
            file = open("record.txt", "w+")
            file.write(str(id) + " " + str(FileName) + " \n")
            file.close()
        p = subprocess.Popen('python /home/ubuntu/anntools/run.py ' + temp, shell=True)
        response.status = 200
        return jsondata

    else:
        response.status = 200
        return 'Sorry, No such file'



@get('/annotations/<job_id>')
def job_result(job_id):
    id = job_id
    file = open("record.txt", "r")
    for line in file:
        content = line.split(" ")
        if (content[0] == id):
            if (os.path.exists("/home/ubuntu/anntools/"+ id +"/"+ content[1] + ".count.log")):
                info = {}
                info["code"] = "200 OK"
                data = {}
                data["Job_id"] = content[0]
                file = open("/home/ubuntu/anntools/" + id + "/"+ content[1] + ".count.log", "r")
                data["log"] = file.read()
                file.close()
                info["data"] = data
                jsondata = json.dumps(info)
                response.status = 200
                return jsondata
            else:
                response.status = 200
                return 'Hava not finished the process of this file'
    response.status = 200
    return 'Can not find this id'


@get('/annotations')
def id_list():
    path = str(request.query.get('key'))
    path_dic = path.split("/")
    id = path_dic[2].split("~")
    if (os.path.exists("/home/ubuntu/" + path_dic[1]) == False):
        os.mkdir("/home/ubuntu/" + path_dic[1])
    os.mkdir("/home/ubuntu/" + path_dic[1]+"/"+id[0])
    resource = boto3.resource('s3')
    my_bucket = resource.Bucket('gas-inputs')
    my_bucket.download_file(path, "/home/ubuntu/" + path_dic[1]+"/"+id[0]+"/"+path_dic[2])
    temp = "/home/ubuntu/" + path_dic[1]+"/"+id[0]+"/"+path_dic[2]
    p = subprocess.Popen('python /home/ubuntu/anntools/run.py ' + temp, shell=True)
    response.status = 200
    return id[0]
    # if (os.path.exists("/home/ubuntu/anntools/record.txt")):
    #     file = open("record.txt", "r")
    #     id_set = set()
    #     for i in file:
    #         content = i.split(" ")
    #         id_set.add(content[0])
    #     info = {}
    #     info["code"] = "200 OK"
    #     data = {}
    #     job = []
    #     for i in id_set:
    #         c = {}
    #         c["url"] = request.url + "/" + i
    #         c["job_id"] = i
    #         job.append(c)
    #     data["jobs"] = job
    #     info["data"] = data
    #     jsondata = json.dumps(info)
    #     response.status = 200
    #     return jsondata
    # else:
    #     response.status = 200
    #     return 'No Job id now'


run(host='0.0.0.0', port=8888, debug=True, reloader=True)
