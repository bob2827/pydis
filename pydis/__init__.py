import collections
import redis
import json

#https://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute-in-python
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

class redisDict(collections.MutableMapping):
    def __init__(self, name, conn):
        self.name = name
        self.rdb = redis.StrictRedis(**conn)

    def __getitem__(self, key):
        v = self.rdb.hget(self.name, key)
        try:
            return json.loads(v)
        except TypeError:
            raise KeyError

    def __setitem__(self, key, value):
        v = json.dumps(value)
        return self.rdb.hset(self.name, key, v)

    def __delitem__(self, key):
        return self.rdb.hdel(self.name, key)

    def __iter__(self):
        return iter(self.rdb.hkeys(self.name))

    def __len__(self):
        return self.rdb.hlen(self.name)

class redisList(collections.MutableSequence):
    def __init__(self, name, conn):
        self.name = name
        self.rdb = redis.StrictRedis(**conn)

    def __getitem__(self, key):
        l = self.__len__()
        v = None

        if isinstance(key, slice):
            if key.step == 1 or key.step == None:
                v = self.rdb.lrange(self.name, key.start, key.stop-1)
                v = [json.loads(val) for val in v]
            else:
                raise Exception("TODO")

        elif isinstance(key, int):
            if key >= l:
                raise IndexError("list index out of range")
            v = self.rdb.lindex(self.name, key)
            v = json.loads(v)

        else:
            raise TypeError("an integer is required")

        return v

    def __setitem__(self, key, val):
        print "Setting %s: %s" % (str(key), str(val))
        l = self.__len__()
        v = json.dumps(val)
        if isinstance(key, slice):
            raise Exception("TODO")
        elif isinstance(key, int):
            if key == 0:
                return self.rdb.lpush(self.name, v)
            elif key >= l:
                return self.rdb.rpush(self.name, v)
        else:
            raise TypeError("an integer is required")

    def __delitem__(self, key):
        l = self.__len__()
        if isinstance(key, slice):
            raise Exception("TODO")
        elif isinstance(key, int):
            if key == 0:
                return self.rdb.lpop(self.name)
            elif (key == l-1): #or key == -1:
                return self.rdb.rpop(self.name)
            elif key >= l:
                raise IndexError("list assignment index out of range")
            elif key < 0:
                raise Exception("TODO")
            else:
                return self.rdb.lrem(self.name, 1, key)

        raise Exception("PANIC")

    def __len__(self):
        return self.rdb.llen(self.name)

    def insert(self, key, val):
        print "Setting %s: %s" % (str(key), str(val))
        v = json.dumps(val)
        l = self.__len__()
        if key == 0:
            return self.rdb.lpush(self.name, v)
        elif key >= l:
            return self.rdb.rpush(self.name, v)
        else:
            return self.rdb.linsert(self.name, 'BEFORE', key, v)
