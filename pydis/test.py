#!/usr/bin/env python

import json
import redis
import unittest
import collections

import base

settings = {'host':'localhost', 'port':6379, 'db':1}
compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

jd = json.dumps
jl = json.loads

class pdTesting(unittest.TestCase):
    def setUp(self):
        self.pd = base.pydis(**settings)
        self.pd.__redisConn__.flushdb()

    def test_list_append(self):
        print "Test Appends"
        l = self.pd.list('t1list', settings)
        l.append(1)
        l.append('hello')
        l.append({'a': 10, 'b': 20})
        l.append([1,2,3,7,11])
        l.append([1,1,2,3,5,8])
        l.append('world')
        l.append(7)
        assert(jd(l.native()) == jd([1, 'hello', {'a': 10, 'b': 20},
                [1,2,3,7,11], [1,1,2,3,5,8], 'world', 7]))

    def test_list_index(self):
        print "Test Indexing"
        l = self.pd.list('t2list', settings)
        l.extend(range(20))
        assert(jd([8, 9]) == jd(l[8:10]))
        assert(jd(range(10)) == jd(l[0:10]))
        assert(jd(range(10)[slice(0,10,2)]) ==
               jd(l[slice(0,10,2)]))
        assert(jd(range(10)[slice(0,7,2)]) ==
               jd(l[slice(0,7,2)]))

        assert(jd(range(20)[0:-1]) ==
               jd(l[0:-1]))
        assert(jd(range(20)[-1]) == jd(l[-1]))

    def test_list_del(self):
        print "Test Deletes"
        r = range(10)
        s = pd.list('t2list', settings)
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
        m = pd.list('t3list', settings)
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

if __name__ == "__main__":
    unittest.main()
