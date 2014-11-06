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
