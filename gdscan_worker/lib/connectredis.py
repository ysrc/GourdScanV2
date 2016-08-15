#coding=utf-8
import redis
import json
import os

'''
Connect redis and excute the command of redis from other class.
'''

ROOT = os.path.dirname(os.path.abspath(__file__))
with open(ROOT+os.path.sep+".."+os.path.sep+"conf.json") as conf:
	workerconf = json.load(conf)
	redisconf = workerconf["redis"]
r = redis.StrictRedis(**redisconf)