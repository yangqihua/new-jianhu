# -*- coding: utf-8 -*-

import oss2
import requests
from common.sys_config import log
from settings import ALI_ACCESS_KEY, ALI_ACCESS_SECRET

# osspython sdk： https://help.aliyun.com/document_detail/32026.html?spm=5176.doc32039.6.304.J2Ctrr
# oss出错处理： https://help.aliyun.com/document_detail/32039.html?spm=5176.doc32029.6.317.yvhgR0

class OSSTools(object):

    def __init__(self, bucket_name):
        auth = oss2.Auth(ALI_ACCESS_KEY, ALI_ACCESS_SECRET)
        self.bucket = oss2.Bucket(auth, 'http://oss-cn-shanghai.aliyuncs.com', bucket_name, connect_timeout=3)

    def upload_from_url(self, picname, content):
        #从腾讯拉取图片可能失败
        #放入oss中可能失败
        #以后要进行后台检查，检查失败率
        #以后图片上传成功一次，就调用一次服务器接口进行转存，否则在接口调用时再转存，慢了，尤其是图片多的情况; 判断图片是否是上次已经传过, 如果是，则不再重复上传
        self.bucket.put_object(picname, content)

