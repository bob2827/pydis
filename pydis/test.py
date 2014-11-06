import redis
import pydis
import json

__rdb__ = redis.StrictRedis(host='localhost', port=6379, db=0)

d = pydis.attrdict()
d[5] = 50
d[6] = 66
d.somevar = 'someval'
d.__save__(__rdb__, 'imadtoo')

e = pydis.rdict(__rdb__, 'imadtoo')
print e
print e.somevar
