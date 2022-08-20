#!/usr/bin/python3
# -*- coding: utf-8 -*-
from calendar import month
from cgi import print_form
from copyreg import pickle
from datetime import datetime
from errno import E2BIG
from time import time
import pytz
import requests
import json
from urllib3.exceptions import *

ali_weather_appcode = "xxxxxxxxxx" # 阿里天气 https://market.aliyun.com/products/57126001/cmapi014302.html#sku=yuncode830200000

def getMsgHeader():
    tz = pytz.timezone('Asia/Shanghai')
    dt = datetime.now(tz)
    h = "今天是 <font color=\"info\">{}</font>".format(dt.strftime('%Y-%m-%d %A'))
    return h
def getMsgHeaderToWechat():
    tz = pytz.timezone('Asia/Shanghai')
    dt = datetime.now(tz)
    h = "今天是 <font color=\"#87CEEB\">{}</font>".format(dt.strftime('%Y-%m-%d %A'))
    return h
class Aqiinfo:
    level = ''
    color = ''
    affect = ''
    measure = ''
    # def __init__(self, level, color, affect, measure):
    #     self.level = level
    #     self.color = color
    #     self.affect = affect
    #     self.measure = measure
class Aqi:
    quality = ''
    aqiinfo = Aqiinfo()
class Weather:
    city = ''
    date = ''
    weather = ''
    temphigh = ''
    templow = ''
    windspeed = ''
    winddirect = ''
    windpower = ''
    aqi = ''
    def isValide(self) -> bool:
        if self.city != '':
            return True
        return False
    def jsonDecode(self, jsonTex):
        self.city = jsonTex['city']
        self.date = jsonTex['date']
        self.weather = jsonTex['weather']
        self.temphigh = jsonTex['temphigh']
        self.templow = jsonTex['templow']
        self.windspeed = jsonTex['windspeed']
        self.winddirect = jsonTex['winddirect']
        self.windpower = jsonTex['windpower']
        aqi = Aqi()
        aqi.quality = jsonTex['aqi']['quality']
        self.aqi = aqi
        aqiinfo = Aqiinfo()
        aqiinfo.level = jsonTex['aqi']['quality']
        aqiinfo.color = jsonTex['aqi']['aqiinfo']['color']
        aqiinfo.affect = jsonTex['aqi']['aqiinfo']['affect']
        aqiinfo.measure = jsonTex['aqi']['aqiinfo']['measure']
        aqi.aqiinfo = aqiinfo  
    def getWeatherTextToWechatWork(self):
        tex = "武汉天气\n > <font color=\"info\">{}</font>, 温度: <font color=\"info\">{}</font> ~ <font color=\"info\">{}</font>\n{}-{}-风速{}，空气质量:<font color=\"info\">{}</font>，{}。".format(
            self.weather,
            self.templow,
            self.temphigh,
            self.windpower,
            self.winddirect,
            self.windspeed,
            self.aqi.quality,
            self.aqi.aqiinfo.affect,
            self.aqi.aqiinfo.measure
        )
        return tex
    def getWeatherTextToWechat(self):
        tex = "<hr>武汉天气 <br> <font color=\"green\">{}</font>, 温度: <font color=\"green\">{}</font> ~ <font color=\"green\">{}</font>， 空气质量:<font color=\"green\">{}</font>，{}。".format(
            self.weather,
            self.templow,
            self.temphigh,
            self.aqi.quality,
            self.aqi.aqiinfo.affect,
            self.aqi.aqiinfo.measure
        )
        return tex
         
def getWeather() -> Weather:
    url = 'https://jisutqybmf.market.alicloudapi.com/weather/query?city=武汉'
    headers={'Authorization': 'APPCODE'+ ' '+ ali_weather_appcode}
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    msg = r.json()['msg']
    w = Weather()
    if msg != 'ok':
        return w
    result = r.json()['result']
    w.jsonDecode(result)
    return w


def getMeetingDay():
    # 2019-10-23 00:00:00  1571760000
    unixTimeStamp = 1571760000
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    day = int((now.timestamp() - unixTimeStamp) / (24 * 60 * 60))
    print(day)
    print('相遇的:',day)
    return day

def getBirthDayOfMa():
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    dt = datetime(now.year, now.month, now.day) 
    birthday = datetime(now.year, 9, 13) 
    day = int((birthday.timestamp() -dt.timestamp()) / (24*60*60))
    print('生日:',day)
    return day

def getExpressLoveDay():
     # 2020-09-04 00:00:00  1599148800
    unixTimeStamp = 1599148800
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    day = int((now.timestamp() - unixTimeStamp) / (24 * 60 * 60))
    print(day)
    print('相爱的天:',day)
    return day


class DailyWord:
    sid = ''
    note = ''
    content = ''
    pic = ''
    def __init__(self) -> None:
        pass
    def isValide(self) -> bool:
        if self.sid != "":
            return True
        return False   
    def getDailyWordHtml(self) -> str:
        return "<br>每日一句<br>{}<br>{}<br><img src=\"{}\" align=\"center\">".format(self.content, self.note, self.pic)

def getDailyWord() -> DailyWord:
    url = "http://open.iciba.com/dsapi"
    r = requests.get(url)
    r.encoding = 'utf-8'
    result = r.json()
    dw = DailyWord()
    if result.get('sid'):
        sid = result['sid']
        n = result['note']
        c = result['content']
        pic = result['fenxiang_img']
        dw.sid = sid
        dw.note = n
        dw.content = c
        dw.pic = pic
    return dw

        
def sendDailyWordToWechatWork(dw: DailyWord):
    if dw.isValide:
        webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxxxxxxxx"
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }
        message = {
            "msgtype": "news",
            "news": {
                "articles":[{
                    "title": "每日一句",
                    "description": dw.content,
                    "url": dw.pic,
                    "picurl": dw.pic
                }]
            }
        }
        message_json = json.dumps(message)
        info = requests.post(url=webhook,data=message_json,headers=header)
    return

# @mdTex 企业微信支持的 markdown 格式文字
def sendAlarmMsg(mdTex):
    wechatwork(mdTex)

# 企业微信推送
def wechatwork(tex):
    webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxxxxxxx"
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    message = {
        "msgtype": "markdown",
        "markdown": {
            "content": tex
        }
    }
    print(message)
    message_json = json.dumps(message)
    try:
        info = requests.post(url=webhook,data=message_json,headers=header)
    except (NewConnectionError, MaxRetryError, ConnectTimeoutError) as e:
        print("unable to connect to wechat server, err:", e)
    except Exception as e2:
        m = print("send message to wechat server, err:", e2)
        sendAlarmMsg(m)

# 微信推送
def wxPusher(tex):
    url = "http://wxpusher.zjiecode.com/api/send/message"
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    message = {
        "appToken":"xxxxxxxxxxxxxxxxx",
        "content": tex,
        "summary":"相爱一生",
        "contentType":2,
        "topicIds":[6666],
        "url":"http://wxpusher.zjiecode.com"
    }
    message_json = json.dumps(message)

    try:
        info = requests.post(url=url,data=message_json, headers=header)
        print(info.text)
    except (NewConnectionError, MaxRetryError, ConnectTimeoutError) as e:
        m = print("unable to connect to wx, err:", e)
        sendAlarmMsg(m)
    except Exception as e: 
        m = print("send message to wx , err:", e)
        sendAlarmMsg(m)
    

 
if __name__=="__main__":
    # 今天是我们相爱的{}天
    # 我们已经相遇{}
    # 距离你的生日还{}天
    h  = getMsgHeader()
    w  = getWeather()
    bd = getBirthDayOfMa()
    md = getMeetingDay()
    ed = getExpressLoveDay()
    dw = getDailyWord()

    # 企业微信
    w1 = w.getWeatherTextToWechatWork()
    tex1 = "{}\n> 今天是我们相爱的<font color=\"warning\"> {} </font>天\n我们已经相遇<font color=\"warning\"> {} </font>天\n距离你的生日还有<font color=\"warning\"> {} </font>天\n\n{}".format(h,ed, md, bd, w1)
    wechatwork(tex1)
    sendDailyWordToWechatWork(dw)
    # wxpusher
    h2 = getMsgHeaderToWechat()
    w2 = w.getWeatherTextToWechat()
    dw2 = dw.getDailyWordHtml()
    tex2 = "{}<br> 今天是我们相爱的<font color=\"#F5BCA9\"> {} </font>天<br>我们已经相遇<font color=\"#F5BCA9\"> {} </font>天<br>距离你的生日还有<font color=\"#F5BCA9\"> {} </font>天<br><br>{}<hr>{}".format(h2,ed, md, bd, w2, dw2)
    wxPusher(tex2)
    
