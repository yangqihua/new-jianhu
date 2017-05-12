# -*- coding: utf-8 -*-

import json
from wx_base import WxPayConf_pub
from wx_base.backends.dj import Helper


def jsapi_sign(request):
	url = "http://" + request.get_host() + request.get_full_path()
	sign = Helper.jsapi_sign(url)
	sign["appId"] = WxPayConf_pub.APPID
	return json.dumps(sign)
