# -*- coding: utf-8 -*-
import datetime, time
from datetime import timedelta


def str_to_int(str, default=0):
    try:
        return int(str)
    except Exception, e:
        return default


resource_url_base = "http://res.jianhu.com"


def get_resource_url():
    pass


def format_expire_time(time_data):
    three_day = timedelta(days=3)
    expire_time = time_data + three_day
    return expire_time.strftime('%Y-%m-%d %H:%M') + " 到期"


def format_time(time_data):
    if not time_data:
        return ''

    ts = int(time.mktime(time_data.timetuple()))
    delta = int(time.time()) - ts
    years = delta / (3600 * 24 * 365)
    months = delta / (3600 * 24 * 30)
    days = delta / (3600 * 24)
    hours = delta / 3600
    minis = delta / 60
    seconds = delta
    if years >= 1:
        return '%d年前' % years

    elif months >= 1:
        return '%d个月前' % months

    elif days >= 1:
        return '%d天前' % days

    elif hours >= 1:
        return "%d小时前" % hours

    elif minis >= 1:
        return "%d分钟前" % minis

    else:
        return "刚刚"


if __name__ == '__main__':
    format_expire_time(0)

    print "Test str_to_int: ", str_to_int("123")
    print "Test str_to_int: ", str_to_int("123", 1)
    print "Test str_to_int: ", str_to_int("a123")
    print "Test str_to_int: ", str_to_int("a123", 1)

