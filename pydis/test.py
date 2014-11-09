#!/usr/bin/env python

import redis
import pydis
import json

settings = {'host':'localhost', 'port':6379, 'db':0}

def testList():
    l = pydis.redisList('t1list', settings)
    for i in range(len(l)-1, -1, -1):
        del l[i]
    #del l[:]
    l.append(1)
    l.append('hello')
    l.append({'a': 10, 'b': 20})

    for i in l:
        print i
    print l[0:10]

if __name__ == "__main__":
    testList()
