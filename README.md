# Pydis

Pydis provides a transparent access mechanism for Redis from Python. It exposes
redis primitives (lists, dicts) by overriding the built in native access
mechanism for the equivalent Python type. It uses the redis-py library to
facilitate the data exchange and passes through any connection options redis-py
is capable of handling.

## Lists

For example a pydis list operates in the following manner:

```python
import pydis   # First, initialize the module (same arguments as redis-py)
pd = pydis.pydis(host='localhost', port=6379, db=15)

# Obtain a list-like object that will store the the redis key 'mylist'.
l = pd.list('mylist') 

# Manipulate the object as you would a python list
l.append(2)        
l.append(3)              
l.extend([5, 7])
l.pop()
```

In redis we now have:
```
>>lrange mylist 0 -1
1) "2"
2) "3"
3) "5"
```

The access semantics for a python list have been preserved as closely as
possible while using redis as a storage backend. All access to the redis
database is synchronous and blocking, there is no caching within the python
interpreter.

## Dictionaries / Hashes

Correspondingly for a dict:

```python
d = pd.dict('mydict')
d['somekey'] = 'astringkey'
d['numkey'] = 1234
d['complex'] = ["any", "json", {"encodable": "structure"}]
d['dontneed'] = 'soonforgotten'
del d['dontneed']
```

And in redis:

```
>>hgetall mydict
 1) "somekey"
 2) "\"astringkey\""
 3) "numkey"
 4) "1234"
 5) "complex"
 6) "[\"any\", \"json\", {\"encodable\": \"structure\"}]"
```

Additionally, pydis provides a mechanism for a 'nestedDict', which is a two
dimensional array. Such arrays are commonly represented in redis using the
the naming convention: "arrayName:firstDimKeyName"

```python
n = pd.nested('nestdict')
n['p1']['k1'] = 1234
n['p2']['m1'] = 4567
n['p1']['k2'] = "somestring"
```

```
>>keys nestdict*
nestdict:p1
nestdict:p2
rd>> hgetall nestdict:p1
k1
1234
k2
"somestring"
>> hgetall nestdict:p2
m1
4567
```
