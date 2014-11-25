#!/usr/bin/env python

import redis
import pydis
import json

settings = {'host':'localhost', 'port':6379, 'db':0}

class syncBacked(pydis.pydisBase):
    adict = pydis.syncDictFactory()
    alist = pydis.syncListFactory()

    def __init__(self, name):
        super(syncBacked, self).__init__(name)

def main():
    pydis.connect(settings)
    s = syncBacked('imabacked')
    s.adict['key'] = 'val'
    s.adict['key2'] = 'val2'
    s.alist.extend(range(10))
    print s.adict.items()
    print list(s.alist)

if __name__ == "__main__":
    main()
