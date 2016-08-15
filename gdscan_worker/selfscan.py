from module.general import general
from lib.isqlmap import isqlmap
import lib.multihread as multihread
from lib.connectredis import r
from base64 import encodestring as es
from base64 import decodestring as ds
from time import sleep
import requests
import json
from lib.connectredis import workerconf
USESQLMAPAPI = workerconf["use_sqlmapapi"]
def check_status(taskid, api):
    try:
        status = json.loads(requests.get(api + '/scan/' + taskid + '/status', timeout=10).text)['status']
    except:
        status = ""
    return status == "terminated"
def isvulun(taskid, api):
    try:
        data = json.loads(requests.get(api + '/scan/' + taskid + '/data', timeout=10).text)['data']
    except:
        data = ""
    return len(data), data
def updaterequest(reqhash, taskid, sqlmapapi, sqlidata):
    oldrequest = json.loads(ds(r.hget("request", reqhash)))
    oldrequest["taskid"] = taskid
    oldrequest["sqlmapapi"] = sqlmapapi
    oldrequest["dbms"] = sqlidata[0]['value'][0]['dbms']
    oldrequest["os"] = sqlidata[0]['value'][0]['os']
    oldrequest["parameter"] = sqlidata[0]['value'][0]['parameter']
    oldrequest["sqlititle"] = sqlidata[0]['value'][0]['data']['1']['title']
    b64req =  es(json.dumps(oldrequest))
    r.hset("request",reqhash, b64req)

def Start_Scan(nothing):

    '''
    Main function of the scan worker, including xss,sqli,xpath,ldap,lfi,sqli_time scan rule. if USESQLMAPAPI= True, user sqlmapapi.
    sqli: post all the data to sqlmapapi or rule, if is vulun, update taskid to redis server.
    '''

    while True:
        reqhash=r.rpoplpush("waiting", "running")
        reqed = r.hget("request", reqhash)
        if not reqed:
            continue
        request = json.loads(ds(reqed))

        rules=['xss','sqli','xpath','ldap','lfi','sqli_time']
        for rule in rules:
            try:
                if rule == 'sqli' and USESQLMAPAPI:
                    newsql = isqlmap()#here wrong!
                    if request.get("uri"):
                        uri = request.get("uri")
                    else:
                        uri = "http://"+request['host']+request['url']
                    taskid, api = newsql.extract_request(uri, request['method'], request['headers'], request['postdata'])
                    print taskid, api
                    while not check_status(taskid, api):
                        sleep(7)
                    sqlilen, sqlidata = isvulun(taskid, api)
                    if sqlilen:
                        r.lpush("sqli", reqhash)
                        updaterequest(reqhash, taskid, api, sqlidata)
                else:
                    scan_obj=general(request['url'],request['host'],request['postdata'],request['headers'],request['method'],request.get('uri'))
                    if 'time' in rule:
                        scan_obj.timecheck=True
                    scan_obj.setname(rule)
                    scan_obj.loadrule()
                    scan_obj.run()
                    if scan_obj.bingo_payload!='':
                        r.lpush(rule, reqhash)
                        r.hset("bingo_payload", reqhash, scan_obj.bingo_payload)
            except:
                pass
        r.lpush("finish", reqhash)

multihread.multi_thread(Start_Scan,1,50)