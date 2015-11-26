#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: LuHao
# @Date:   2015-11-26 20:08:38
# @Last Modified by:   LuHao
# @Last Modified time: 2015-11-26 20:10:51

from decorators import async
import urllib
import urllib2

# 异步发送短信
def send_sms(phone_number, content):
	params = urllib.urlencode({'smsMob': phone_number, 'Uid': 'dingfanla', 'Key': '19c35d39ee379898d25e', 'smsText': content})
	url = 'http://utf8.sms.webchinese.cn/?' + params
	req = urllib2.Request(url)
	print ">>>send_sms: " + urllib2.urlopen(req).read()

@async
def send_async_sms(phone_number, content):
    send_sms(phone_number, content)
