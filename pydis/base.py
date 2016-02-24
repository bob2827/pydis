# Pydis - Transparent Redis bindings for Python
# Copyright (C) 2014-2016 Bob Sherbert
# bob.sherbert@gmail.com
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

class pydis(object):
    def __init__(self, **kwargs):
        self.__redisConn__ = redis.StrictRedis(**kwargs)

    def flushdb(self):
        self.__redisConn__.flushdb()

    def dict(self, name):
        return syncDict(name, self.__redisConn__)

    def list(self, name, tag="__TAG__"):
        return syncList(name, self.__redisConn__, tag)

    def nested(self, prefix):
        return syncNestedDict(prefix, self.__redisConn__)

class expireFeature(object):
    def expire(self, timeout):
        self.rdb.expire(self._rname, timeout)

class syncDict(collections.MutableMapping, expireFeature):
    def __init__(self, name, rdb):
        self._rname = name
        self.rdb = rdb

    def __getitem__(self, key):
        v = self.rdb.hget(self._rname, key)
        try:
            return json.loads(v)
        except TypeError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        v = json.dumps(value)
        return self.rdb.hset(self._rname, key, v)

    def __delitem__(self, key):
        return self.rdb.hdel(self._rname, key)

    def __iter__(self):
        return iter(self.rdb.hkeys(self._rname))

    def __len__(self):
        return self.rdb.hlen(self._rname)

    def native(self):
        """ Return a native python dict containing the same information as the
        redis backing key for this object """
        d = self.rdb.hgetall(self._rname)
        dr = {}
        for k,v in d.items():
            dr[k] = json.loads(v)
        return dr

class syncList(collections.MutableSequence, expireFeature):
    def __init__(self, name, rdb, tag="__TAG__"):
        self._rname = name
        self.tag = tag
        self.rdb = rdb

    def native(self):
        """ Return a native python list containing the same information as the
        redis backing key for this object """

        l = []
        for i in range(len(self)):
            l.append(self[i])
        return l

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
class syncNestedDict(collections.Mapping):
    def __init__(self, prefix, rdb):
        self.prefix = prefix
        self.rdb = rdb

    def __getitem__(self, key):
        sd = syncDict("%s:%s" % (self.prefix, key), self.rdb)
        return sd

    def __delitem__(self, key):
        return self.rdb.delete("%s:%s" % (self.prefix, key))

    def __iter__(self):
        return (s.split(':')[1] for s in self.rdb.keys("%s:*" % self.prefix))

    def __len__(self):
        return len(self.rdb.keys("%s:*" % self.prefix))

    def expire(self, key, timeout):
        self.rdb.expire("%s:%s" % (self.prefix, key), timeout)
