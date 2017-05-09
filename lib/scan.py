#coding=utf-8

import re
import json
import time
import base64
import requests
import urlparse
import threading

from xml.dom import minidom
from base64 import decodestring as ds

from lib import out
from lib import config
from lib.redisopt import conn

'''
All those scan funcs and threads controll
'''


def thread_filled():
    running_length = conn.llen("running")
    if running_length < int(config.load()['threads_num']):
        return False
    else:
        return True


def time_requests(method, url, headers, postdata=""):
    try:
        time0 = time.time()
        if method == 'POST':
            res = requests.post(url=url, data=postdata, headers=headers)
        else:
            res = requests.get(url=url, headers=headers)
        time1 = time.time()
        return res.content, time1-time0
    except:
        return "Error", 0


def request_payload(request, payload, param, postdata=False, time_check=False):
    if postdata:
        postdata = request['postdata'].replace(param, param + payload)
        res, times = time_requests(request['method'], request['url'], request['headers'], postdata)
    elif urlparse.urlparse(request['url']).query != "":
        url = request['url'].replace(param, param + payload)
        res, times = time_requests(request['method'], url, request['headers'], request['postdata'])
    elif time_check:
        return "Error", 0
    else:
        return "Error"
    if time_check:
        return res, times
    else:
        return res


def query_collect(query, url):
    url = urlparse.urlparse(url)
    return urlparse.urlunparse((url.scheme, url.netloc, url.path, url.params, query, url.fragment))


def requests_convert(request):
    url = urlparse.urlparse(request['url'])
    query = re.sub("=$", "=1", url.query.replace("=&", "=1&"))
    request['url'] = query_collect(query, request['url'])
    return request


def scan_start():
    while config.load()['scan_stat'].lower() == "true":
        try:
            while thread_filled():
                time.sleep(5)
            reqhash = conn.rpoplpush("waiting", "running")
            if not reqhash:
                time.sleep(10)
                continue
            reqed = conn.hget("request", reqhash)
            request = json.loads(ds(reqed))
            rules = config.load_rule()['scan_type']
            url = urlparse.urlparse(request['url']).query
            if (request['method'] == "GET" and url != "") or (request['method'] == "POST" and (request["postdata"] != "" or url != "")):
                t = threading.Thread(target=new_scan, args=(reqhash, requests_convert(request), rules))
                t.start()
            else:
                conn.lrem("running", 1, reqhash)
                conn.lpush("finished", reqhash)
        except Exception,e:
            out.error(str(e))
    return


def new_scan(reqhash, request, rules):
    out.good("start new mission: %s" % reqhash)
    request_stat = 0
    request_message = []
    request_result = {}
    vulnerable = 0
    for rule in rules:
        if config.load()['scan_stat'].lower() == "true":
            message = eval(rule + "_scan")(request, int(config.load()['scan_level']))
            request_stat = message['request_stat']
            if request_stat > vulnerable:
                vulnerable = request_stat
            request_message = message['message'].split("|,|")
            request_result[rule] = {"stat": request_stat, "message": request_message}
    request_result['stat'] = vulnerable
    if vulnerable > 0:
        conn.lpush("vulnerable", reqhash)
    conn.hset("results", reqhash, base64.b64encode(json.dumps(request_result)))
    conn.lrem("running", 1, reqhash)
    conn.lpush("finished", reqhash)


def common_scan(request, config_level, re_test, scan_type):
    message = {"request_stat": 0, "message": ""}
    dom = minidom.parse(config.rule_read(scan_type, get_file_handle=True)).documentElement
    for node in dom.getElementsByTagName('couple'):
        couple_id = int(node.getAttribute("id"))
        if couple_id <= config_level:
            payloads = node.getElementsByTagName('requests')[0].childNodes[0].nodeValue.strip()
            for payload in payloads.splitlines():
                for param_name in urlparse.urlparse(request['url']).query.split("&"):
                    response = request_payload(request, payload.strip(), param_name)
                    for response_rule in node.getElementsByTagName('responses')[0].childNodes[0].nodeValue.strip().splitlines():
                        if re_test:
                            if re.search(response_rule.strip().encode("utf-8"), response):
                                message['request_stat'] = 3
                                message['message'] += "payload: %s|#|param: %s|#|findstr: %s|,|" % (payload.strip().encode('utf-8'), param_name.split("=")[0], response_rule.strip().encode('utf-8'))
                                if config.load()['only_one_match'].lower() == "true":
                                    return message
                        else:
                            if response_rule.strip().encode("utf-8") in response:
                            #rule format: unicode, it need to be encoded with utf-8
                                message['request_stat'] = 3
                                message['message'] += "payload: %s|#|param: %s|#|findstr: %s|,|" % (payload.strip().encode('utf-8'), param_name.split("=")[0], response_rule.strip().encode('utf-8'))
                                if config.load()['only_one_match'].lower() == "true":
                                    return message
                for param_name in request['postdata'].split("&"):
                    if request['postdata'] == "":
                        break
                    else:
                        response = request_payload(request, payload.strip(), param_name, postdata=True)
                    for response_rule in node.getElementsByTagName('responses')[0].childNodes[0].nodeValue.strip().splitlines():
                        if re_test:
                            if re.search(response_rule.strip().encode("utf-8"), response):
                                message['request_stat'] = 3
                                message['message'] += "payload: %s|#|param: %s|#|findstr: %s|,|" % (payload.strip().encode('utf-8'), param_name.split("=")[0], response_rule.strip().encode('utf-8'))
                                if config.load()['only_one_match'].lower() == "true":
                                    return message
                        else:
                            if response_rule.strip().encode("utf-8") in response:
                            #rule format: unicode, it need to be encoded with utf-8
                                message['request_stat'] = 3
                                message['message'] += "payload: %s|#|param: %s|#|findstr: %s|,|" % (payload.strip().encode('utf-8'), param_name.split("=")[0], response_rule.strip().encode('utf-8'))
                                if config.load()['only_one_match'].lower() == "true":
                                    return message
    return message


def sqlireflect_scan(request, level):
    message = common_scan(request, level, True, "sqlireflect")
    return message


def ldap_scan(request, level):
    message = common_scan(request, level, False, "ldap")
    return message


def lfi_scan(request, level):
    message = common_scan(request, level, True, "lfi")
    return message


def xpath_scan(request, level):
    message = common_scan(request, level, False, "xpath")
    return message


def xss_scan(request, config_level):
    message = {"request_stat": 0, "message": ""}
    dom = minidom.parse(config.rule_read("xss", get_file_handle=True)).documentElement
    for node in dom.getElementsByTagName('couple'):
        couple_id = int(node.getAttribute("id"))
        if couple_id <= config_level:
            payloads = node.getElementsByTagName('requests')[0].childNodes[0].nodeValue.strip()
            for payload in payloads.splitlines():
                for param_name in urlparse.urlparse(request['url']).query.split("&"):
                    response = request_payload(request, payload.strip(), param_name)
                    if payload.strip().encode("utf-8") in response:
                        message['request_stat'] = 1
                        message['message'] += "payload: %s|#|param: %s|#|findstr: %s|,|" % (payload.strip().encode('utf-8'), param_name.split("=")[0], payload.strip().encode('utf-8'))
                        if config.load()['only_one_match'].lower() == "true":
                            return message
                for param_name in request['postdata'].split("&"):
                    if request['postdata'] == "":
                        break
                    else:
                        response = request_payload(request, payload.strip(), param_name, postdata=True)
                    if payload.strip().encode("utf-8") in response:
                        message['request_stat'] = 1
                        message['message'] += "payload: %s|#|param: %s|#|findstr: %s|,|" % (payload.strip().encode('utf-8'), param_name.split("=")[0], payload.strip().encode('utf-8'))
                        if config.load()['only_one_match'].lower() == "true":
                            return message
    return message


def sqlibool_scan(request, config_level):
    message = {"request_stat": 0, "message": ""}
    dom = minidom.parse(config.rule_read("sqlibool", get_file_handle=True)).documentElement
    for node in dom.getElementsByTagName('couple'):
        couple_id = int(node.getAttribute("id"))
        if couple_id <= config_level:
            for compare in node.getElementsByTagName("compare"):
                compare1 = compare.getElementsByTagName("compare1")[0].childNodes[0].nodeValue
                compare11 = compare.getElementsByTagName("compare11")[0].childNodes[0].nodeValue
                compare2 = compare.getElementsByTagName("compare2")[0].childNodes[0].nodeValue
                compare22 = compare.getElementsByTagName("compare22")[0].childNodes[0].nodeValue
                for param_name in urlparse.urlparse(request['url']).query.split("&"):
                    response1 = request_payload(request, compare1, param_name)
                    response2 = request_payload(request, compare2, param_name)
                    response22 = request_payload(request, compare22, param_name)
                    time.sleep(1)#prevent time stamp in response
                    response11 = request_payload(request, compare11, param_name)
                    if response1 == response11 and response2 == response22 and response1 != response2:
                        message['request_stat'] = 2
                        message['message'] += "payload1: %s|#|payload2: %s|#|param: %s|,|" % (compare1.encode('utf-8'), compare2.encode('utf-8'), param_name.split("=")[0])
                        if config.load()['only_one_match'].lower() == "true":
                            return message
                for param_name in request['postdata'].split("&"):
                    if request['postdata'] == "":
                        break
                    response1 = request_payload(request, compare1, param_name, postdata=True)
                    response11 = request_payload(request, compare11, param_name, postdata=True)
                    response2 = request_payload(request, compare2, param_name, postdata=True)
                    response22 = request_payload(request, compare22, param_name, postdata=True)
                    if response1 == response11 and response2 == response22 and response1 != response2:
                        message['request_stat'] = 2
                        message['message'] += "payload1: %s|#|payload2: %s|#|param: %s|,|" % (compare1.encode('utf-8'), compare2.encode('utf-8'), param_name.split("=")[0])
                        if config.load()['only_one_match'].lower() == "true":
                            return message
    return message


def sqlitime_scan(request, config_level):
    message = {"request_stat": 0, "message": ""}
    dom = minidom.parse(config.rule_read("sqlitime", get_file_handle=True)).documentElement
    for node in dom.getElementsByTagName('couple'):
        couple_id = int(node.getAttribute("id"))
        if couple_id <= config_level:
            payloads = node.getElementsByTagName('requests')[0].childNodes[0].nodeValue.strip()
            for payload in payloads.splitlines():
                if "TIME_VAR" in payload:
                    for param_name in urlparse.urlparse(request['url']).query.split("&"):
                        response, time0 = request_payload(request, payload.strip().replace("TIME_VAR", "0"), param_name, time_check=True)
                        response, time3 = request_payload(request, payload.strip().replace("TIME_VAR", "3"), param_name, time_check=True)
                        if time3 - time0 >= 2:
                            response, time6 = request_payload(request, payload.strip().replace("TIME_VAR", "6"), param_name, time_check=True)
                            num = (time6 - time0) / (time3 - time0)
                            if num <= 2.3 and num >= 1.7:
                                message['request_stat'] = 3
                                message['message'] += "payload: %s|#|param: %s|,|" % (payload.strip().replace("TIME_VAR", '5').encode('utf-8'), param_name.split("=")[0])
                                if config.load()['only_one_match'].lower() == "true":
                                    return message
                    for param_name in request['postdata'].split("&"):
                        if request['postdata'] == "":
                            break
                        response, time0 = request_payload(request, payload.strip().replace("TIME_VAR", "0"), param_name, postdata=True, time_check=True)
                        response, time3 = request_payload(request, payload.strip().replace("TIME_VAR", "3"), param_name, postdata=True, time_check=True)
                        if time3 - time0 >= 2:
                            response, time6 = request_payload(request, payload.strip().replace("TIME_VAR", "6"), param_name, postdata=True, time_check=True)
                            num = (time6 - time0) / (time3 - time0)
                            if num <= 2.3 and num >= 1.7:
                                message['request_stat'] = 3
                                message['message'] += "payload: %s|#|param: %s|,|" % (payload.strip().replace("TIME_VAR", '5').encode('utf-8'), param_name.split("=")[0])
                                if config.load()['only_one_match'].lower() == "true":
                                    return message
                elif "NUM_VAR" in payload:
                    for param_name in urlparse.urlparse(request['url']).query.split("&"):
                        response, time0 = request_payload(request, payload.strip().replace("NUM_VAR", "0"), param_name, time_check=True)
                        VAR = '500000'
                        for NUM_VAR in range(3):
                            VAR += '0'
                            response, time_more = request_payload(request, payload.strip().replace("NUM_VAR", VAR), param_name, time_check=True)
                            if time_more - time0 >= 3:
                                response, time6 = request_payload(request, payload.strip().replace("NUM_VAR", str(int(VAR) * 2)), param_name, time_check=True)
                                num = (time6 - time0) / (time_more - time0)
                                if num <= 2.3 and num >= 1.7:
                                    message['request_stat'] = 3
                                    message['message'] += "payload: %s|#|param: %s|,|" % (payload.strip().replace("NUM_VAR", VAR).encode('utf-8'), param_name.split("=")[0])
                                    if config.load()['only_one_match'].lower() == "true":
                                        return message
                                    else:
                                        break
                                else:
                                    break
                    for param_name in request['postdata'].split("&"):
                        if request['postdata'] == "":
                            break
                        response, time0 = request_payload(request, payload.strip().replace("NUM_VAR", "0"), param_name, time_check=True)
                        VAR = '500000'
                        for NUM_VAR in range(3):
                            VAR += '0'
                            response, time_more = request_payload(request, payload.strip().replace("NUM_VAR", VAR), param_name, postdata=True, time_check=True)
                            if time_more - time0 >= 3:
                                response, time6 = request_payload(request, payload.strip().replace("NUM_VAR", str(int(VAR) * 2)), param_name, postdata=True, time_check=True)
                                num = (time6 - time0) / (time_more - time0)
                                if num <= 2.3 and num >= 1.7:
                                    message['request_stat'] = 3
                                    message['message'] += "payload: %s|#|param: %s|,|" % (payload.strip().replace("NUM_VAR", VAR).encode('utf-8'), param_name.split("=")[0])
                                    if config.load()['only_one_match'].lower() == "true":
                                        return message
                                    else:
                                        break
                                else:
                                    break
    return message


def sqlmap_scan(request, level):
    message = {"request_stat": 0, "message": ""}
    sqlmap_api = config.load_rule()["sqlmap_api"]
    sqlmap_conf = json.load(open(config.rule_read("sqlmap", get_file_handle=True)))
    conf_ban = ["url", "headers", "data", "taskid", "database"]
    for ban in conf_ban:
        if ban in sqlmap_conf.keys():
            del sqlmap_conf[ban]
    sqlmap_conf['url'] = request['url']
    sqlmap_conf['data'] = request['postdata']
    sqlmap_conf['headers'] = ""
    for header in request['headers'].keys():
        sqlmap_conf['headers'] += "%s: %s\r\n" % (header, request['headers'][header])
    json_headers = {"Content-Type": "application/json"}
    taskid = json.loads(requests.get("%s/task/new" % sqlmap_api).content)['taskid']
    data = json.dumps(sqlmap_conf)
    try:
        requests.post("%s/option/%s/set" % (sqlmap_api, taskid), data=json.dumps(sqlmap_conf), headers=json_headers)
        requests.post("%s/scan/%s/start" % (sqlmap_api, taskid), data="{}", headers=json_headers)
        while json.loads(requests.get("%s/scan/%s/status" % (sqlmap_api, taskid)).content)['status'] != "terminated":
            time.sleep(5)
        data = json.loads(requests.get("%s/scan/%s/data" % (sqlmap_api, taskid)).content)['data']
        if data != []:
            message['request_stat'] = 3
            message['message'] += "title: %s|#|payload: %s|#|taskid: %s|,|" % (data[0]['value'][0]['data']['1']['title'], data[0]['value'][0]['data']['1']['payload'], taskid)
    except Exception, e:
        print e
    finally:
        return message