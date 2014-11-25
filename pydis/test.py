#!/usr/bin/env python

import redis
import pydis
import json

settings = {'host':'localhost', 'port':6379, 'db':0}

def testList():
    l = pydis.syncList('t1list', settings)
    print "Clear List"
    for i in range(len(l)-1, -1, -1):
        del l[i]
    print ""

    print "Build List"
    l.append(1)
    l.append('hello')
    l.append({'a': 10, 'b': 20})
    l.append([1,2,3,7,11])
    l.append([1,1,2,3,5,8])
    l.append('world')
    l.append(7)
    for i in l:
        print i
    print ""

    print "Test Get: Slicing/Indexing"
    print l[8:10]
    print l[0:10]
    print l[slice(0,10,2)]
    print l[slice(0,7,2)]
    print l[0:-1]
    print l[-1]
    print ""

    print "Test Deletes"
    r = range(10)
    s = pydis.syncList('t2list', settings)
    for i in range(len(s)-1, -1, -1):
        del s[i]
    #del s[:]
    s.extend(range(10))
    del r[5]
    del s[5]
    del r[-1]
    del s[-1]
    del r[0]
    del s[0]
    del r[2:5]
    del s[2:5]
    print "Ref:", r
    print "PyDis:", [i for i in s]
    print ""

    print "Test Inserts"
    m = pydis.syncList('t3list', settings)
    for i in range(len(m)-1, -1, -1):
        del m[i]
    m.extend(range(10))
    n = range(10)
    m.insert(2,99)
    n.insert(2,99)
    m[3:4] = [10,20,30,40]
    n[3:4] = [10,20,30,40]
    m[slice(5, 10, 2)] = [11, 22, 33]
    n[slice(5, 10, 2)] = [11, 22, 33]
    print "Ref:", n
    print "PyDis:", [i for i in m]
    print ""

if __name__ == "__main__":
    testList()
