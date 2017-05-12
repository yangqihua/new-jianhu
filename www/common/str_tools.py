# -*- coding: utf-8 -*-

import uuid

def gen_uuid():
    return uuid.uuid4()

def gen_short_uuid():
    uuid_str = str(uuid.uuid4())
    return uuid_str.replace('-', '')

if __name__ == '__main__':
    print "gen_uuid: ", gen_uuid()
    print "gen_short_uuid: ", gen_short_uuid()
