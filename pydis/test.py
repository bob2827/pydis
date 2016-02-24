#!/usr/bin/env python

import json
import redis
import unittest
import collections

import base

settings = {'host':'localhost', 'port':6379, 'db':15}
compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

jd = json.dumps
jl = json.loads

class listTesting(unittest.TestCase):
    def setUp(self):
        self.pd = base.pydis(**settings)
        self.pd.__redisConn__.flushdb()

    def test_list_append(self):
        print "Test List Append"
        l = self.pd.list('t1list')
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
        print "Test List Indexing"
        l = self.pd.list('t2list')
        for i in range(20):
            self.pd.__redisConn__.rpush('t2list', i)
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
        print "Test List Deletes"
        #populate a list and do individual deletes of each element
        for i in range(10):
            self.pd.__redisConn__.rpush('t3list', i)
        s = self.pd.list('t3list')
        for i in range(len(s)-1, -1, -1):
            del s[i]
        assert jd([]) == jd(s.native())

        #repopulate and try slice deletes 
        r = range(10)
        for i in r:
            self.pd.__redisConn__.rpush('t3list', i)
        del r[5]
        del s[5]
        del r[-1]
        del s[-1]
        del r[0]
        del s[0]
        del r[2:5]
        del s[2:5]
        assert jd(r) == jd(s.native())

    def test_list_ins(self):
        print "Test List Inserts"
        n = range(10)
        for i in n:
            self.pd.__redisConn__.rpush('t4list', i)

        m = self.pd.list('t4list')
        m.insert(2,99)
        n.insert(2,99)
        m[3:4] = [10,20,30,40]
        n[3:4] = [10,20,30,40]
        m[slice(5, 10, 2)] = [11, 22, 33]
        n[slice(5, 10, 2)] = [11, 22, 33]
        assert jd(n) == jd(m.native())

class dictTesting(unittest.TestCase):
    def setUp(self):
        self.pd = base.pydis(**settings)
        self.pd.__redisConn__.flushdb()

    def test_dict_insert(self):
        print "Test Dict Inserts"
        d = {'a': 1, 'b': 'two', 'c': ['a', 'b']}
        rd = self.pd.dict('t1dict')
        for k, v in d.items():
            rd[k] = v
        assert jd(d) == jd(rd.native())

    def test_dict_del(self):
        print "Test Dict Deletes"
        self.pd.__redisConn__.hset('t2dict', 'a', 1)
        self.pd.__redisConn__.hset('t2dict', 'b', 'two')
        self.pd.__redisConn__.hset('t2dict', 'c', '["a", "b"]')
        rd = self.pd.dict('t2dict')
        assert len(rd.keys()) == 3
        del rd['b']
        assert len(rd.keys()) == 2
        del rd['c']
        assert len(rd.keys()) == 1
        assert jd({'a':1}) == jd(rd.native())

if __name__ == "__main__":
    unittest.main()
