# Pydis - Transparent Redis bindings for Python
# Copyright (C) 2014 Bob Sherbert
# bob@carbidelabs.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import collections
import redis
import json
import inspect

#https://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute-in-python
"""
class attrdict(dict):
    def __init__(self, *args, **kwargs):
        super(attrdict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __save__(self, rdb, name):
	d = {}
	rdb.delete(name)
	for k,v in self.items():
		d[k] = json.dumps(v)
	rdb.hmset(name, d)

class rdict(attrdict):
	def __init__(self, rdb, name):
		d = rdb.hgetall(name)
		print d
		for k,v in d.items():
			d[k] = json.loads(v)
		super(rdict, self).__init__(d)

class Dict():
    def __init__(self):

    def widget(self, name):
        return redisDict(name)
"""


__redisConn__ = None

def connect(**kwargs):
    global __redisConn__
    __redisConn__ = redis.StrictRedis(**kwargs)

class pydisBase(object):
    def __init__(self, name):
        self._rname = name
        for mbr_name, val in inspect.getmembers(self):
            if isinstance(val, syncFactory):
                ch_redis_name = "%s:%s" % (self._rname, mbr_name)
                exec("self.%s = val.generate('%s')" % (mbr_name, ch_redis_name))


class syncFactory(object):
    def __init__(self):
        pass

class syncDictFactory(syncFactory):
    def __init__(self):
        pass

    def generate(self, name):
        return syncDict(name)

class syncListFactory(syncFactory):
    def __init__(self):
        pass

    def generate(self, name):
        return syncList(name)

class syncDict(collections.MutableMapping):
    def __init__(self, name):
        self._rname = name

    @property
    def rdb(self):
        return __redisConn__

    def __getitem__(self, key):
        v = self.rdb.hget(self._rname, key)
        try:
            return json.loads(v)
        except TypeError:
            raise KeyError

    def __setitem__(self, key, value):
        v = json.dumps(value)
        return self.rdb.hset(self._rname, key, v)

    def __delitem__(self, key):
        return self.rdb.hdel(self._rname, key)

    def __iter__(self):
        return iter(self.rdb.hkeys(self._rname))

    def __len__(self):
        return self.rdb.hlen(self._rname)

class syncList(collections.MutableSequence):
    def __init__(self, name, tag="__TAG__"):
        self._rname = name
        self.tag = tag

    @property
    def rdb(self):
        return __redisConn__

    def __adjbound__(self, key, l, check=True):
        if key < 0:
            key = l + key
            if check and (key < 0):
                raise IndexError("list assignment index out of range")
        return key

    def __indvset__(self, key, val):
        v = json.dumps(val)
        l = self.__len__()
        if isinstance(key, int):
            if key == 0:
                return self.rdb.lpush(self._rname, v)
            elif key >= l:
                return self.rdb.rpush(self._rname, v)
            else:
                return self.rdb.lset(self._rname, key, v)
        else:
            raise TypeError("an integer is required")

    def __indvdel__(self, key, check=True):
        l = self.__len__()
        key = self.__adjbound__(key, l)
        if key == 0:
            return self.rdb.lpop(self._rname)
        elif key == l-1: #or key == -1:
            return self.rdb.rpop(self._rname)
        elif (key >= l) or (key < 0):
            if check:
                raise IndexError("list assignment index out of range")
            else:
                return True
        else:
            print >> sys.stderr, "WARNING: Removing element %d from list of length %d" % (key, l)
            print >> sys.stderr, "Non-head/tail items have O(n) complexity in Redis"
            self.rdb.lset(self._rname, key, self.tag)
            return self.rdb.lrem(self._rname, 1, self.tag)

    def __getitem__(self, key):
        l = self.__len__()
        v = None

        if isinstance(key, slice):
            if key.step == 1 or key.step == None:
                v = self.rdb.lrange(self._rname, key.start, key.stop-1)
                v = [json.loads(val) for val in v]
            else:
                stop = key.stop
                if stop > l:
                    stop = l
                r = range(key.start, stop, key.step)
                val = [self.rdb.lindex(self._rname, v) for v in r]
                v = [json.loads(j) for j in val]

        elif isinstance(key, int):
            if key >= l:
                raise IndexError("list index out of range")
            v = self.rdb.lindex(self._rname, key)
            v = json.loads(v)

        else:
            raise TypeError("an integer is required")

        return v

    def __setitem__(self, key, val):
        l = self.__len__()
        if isinstance(key, slice):
            #TypeError("slice indices must be integers or None or have an __index__ method")
            #Check bounds and adjust for negative indicies
            start = self.__adjbound__(key.start, l)
            stop = self.__adjbound__(key.stop, l)
            step = 1
            if key.step:
                step = key.step

            # How the default list implementation deals with len(source) !=
            # len(dest) differs depending on the step size, WTF guys
            r = range(start, stop, step)
            if step == 1:
                count = 0
                #while within the bound of the dest size, overwrite
                while count < len(r):
                    self.__indvset__(start+count, val[count])
                    count += 1
                #once we're outside the dest size, we do mid-list insertions
                while count < len(val):
                    self.insert(start+count, val[count])
                    count += 1
            else:
                if len(r) != len(val):
                    raise ValueError("attempt to assign sequence of size %d to extended slice of size %d" % (len(val), len(r)))
                else:
                    count = 0
                    while count < len(r):
                        self.__indvset__(r[count], val[count])
                        count += 1
        else:
            return self.__indvset__(key, val)

    def __delitem__(self, key):
        l = self.__len__()
        if isinstance(key, slice):
            print key
            start = key.start
            stop = key.stop
            step = 1
            if key.step:
                step = key.step
            r = range(start, stop, step)
            r = [self.__adjbound__(i, l, check=False) for i in r]

            if (min(r) <= 0) or (max(r) < l-1):
                previous = 0
                for i in sorted(r):
                    self.__indvdel__(i-previous, check=False)
                    previous += 1
            elif max(r) >= l-1:
                for i in sorted(r, reverse=True):
                    self.__indvdel__(i, check=False)
            else:
                raise Exception("PANIC")

        elif isinstance(key, int):
            self.__indvdel__(key)
        else:
            print type(key)
            raise Exception("PANIC")

    def __len__(self):
        return self.rdb.llen(self._rname)

    def insert(self, key, val):
        v = json.dumps(val)
        l = self.__len__()
        if key == 0:
            return self.rdb.lpush(self._rname, v)
        elif key >= l:
            return self.rdb.rpush(self._rname, v)
        else:
            print >> sys.stderr, "WARNING: Inserting element at position %d on list of length %d" % (key, l)
            print >> sys.stderr, "Non-head/tail items have O(n) complexity in Redis"
            t = self.rdb.lindex(self._rname, key)
            self.rdb.lset(self._rname, key, self.tag)
            self.rdb.linsert(self._rname, 'BEFORE', self.tag, v)
            self.rdb.linsert(self._rname, 'BEFORE', self.tag, t)
            self.rdb.lrem(self._rname, 1, self.tag)

"""
Provides 2D mapping capability
d = syncNestedDict('prefix')
Python                Redis
d['a']['b'] = 10 -->  prefix:a [b = 10, c = 20]
d['a']['c'] = 20
"""
class syncNestedDict(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def __getitem__(self, key):
        sd = syncDict("%s:%s" % (self.prefix, key))
        return sd
