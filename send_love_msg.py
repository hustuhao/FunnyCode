import json
from datetime import datetime

import pytz
import requests

from config import loadConfig

# Load configuration
config = loadConfig("config.yaml")
qywxWebhookKey = config.weChatWork.webhookKey
wxpushAppToken = config.wxPusher.appToken
city = config.weather.city
monthOfBirthday = config.lover.monthOfBirthday
dayOfBirthday = config.lover.dayOfBirthday
expressLoveTimestamp = config.lover.expressLoveTimestamp
meetingTimestamp = config.lover.meetingTimestamp
weatherApiKey = config.weather.apiKey


def getMsgHeader():
    tz = pytz.timezone("Asia/Shanghai")
    dt = datetime.now(tz)
    h = '今天是 <font color="info">{}</font>'.format(dt.strftime("%Y-%m-%d %A"))
    return h


def getMsgHeaderToWechat():
    tz = pytz.timezone("Asia/Shanghai")
    dt = datetime.now(tz)
    h = '今天是 <font color="#87CEEB">{}</font>'.format(dt.strftime("%Y-%m-%d %A"))
    return h


class Weather:
    def __init__(self):
        self.city = ""
        self.adcode = ""
        self.province = ""
        self.reporttime = ""
        self.date = ""
        self.week = ""
        self.dayweather = ""
        self.nightweather = ""
        self.daytemp = ""
        self.nighttemp = ""
        self.daywind = ""
        self.nightwind = ""
        self.daypower = ""
        self.nightpower = ""

    def isValide(self) -> bool:
        return self.city != ""

    def jsonDecode(self, jsonTex):
        self.city = jsonTex["city"]
        self.adcode = jsonTex["adcode"]
        self.province = jsonTex["province"]
        self.reporttime = jsonTex["reporttime"]
        casts = jsonTex["casts"][0]
        self.date = casts["date"]
        self.week = casts["week"]
        self.dayweather = casts["dayweather"]
        self.nightweather = casts["nightweather"]
        self.daytemp = casts["daytemp"]
        self.nighttemp = casts["nighttemp"]
        self.daywind = casts["daywind"]
        self.nightwind = casts["nightwind"]
        self.daypower = casts["daypower"]
        self.nightpower = casts["nightpower"]

    def getWeatherTextToWechatWork(self):
        tex = '武汉天气\n > <font color="info">{}</font>, 白天温度: <font color="info">{}</font> ~ 晚上温度: <font color="info">{}</font>\n白天风力:{}-{}，晚上风力:{}-{}。'.format(
            self.dayweather,
            self.daytemp,
            self.nighttemp,
            self.daypower,
            self.daywind,
            self.nightpower,
            self.nightwind,
        )
        return tex

    def getWeatherTextToWechat(self):
        tex = '<hr>武汉天气 <br> <font color="green">{}</font>, 白天温度: <font color="green">{}</font> ~ 晚上温度: <font color="green">{}</font>， 白天风力:{}-{}，晚上风力:{}-{}。'.format(
            self.dayweather,
            self.daytemp,
            self.nighttemp,
            self.daypower,
            self.daywind,
            self.nightpower,
            self.nightwind,
        )
        return tex


def getWeather() -> Weather:
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "city": city,
        "extensions": "all",
        "key": weatherApiKey,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()

        if data.get("status") != "1":
            raise ValueError(f"API Error: {data.get('info')}")

        forecasts_data = data.get("forecasts", [])
        if not forecasts_data:
            raise ValueError("No forecasts data available.")

        forecast = forecasts_data[0]
        weather = Weather()
        weather.jsonDecode(forecast)

        return weather

    except requests.RequestException as e:
        print(f"Request error: {e}")
    except ValueError as e:
        print(f"Value error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return Weather()  # 返回一个无效的 Weather 对象


def getMeetingDay():
    tz = pytz.timezone("Asia/Shanghai")
    now = datetime.now(tz)
    day = int((now.timestamp() - meetingTimestamp) / (24 * 60 * 60))
    print(day)
    print("相遇的:", day)
    return day


def getBirthDayOfLover():
    tz = pytz.timezone("Asia/Shanghai")
    yearNow = datetime.now(tz)
    dt = datetime(yearNow.year, yearNow.month, yearNow.day)
    # 判断今年的生日是否已经过去
    birthday = datetime(yearNow.year, monthOfBirthday, dayOfBirthday)
    if birthday.timestamp() < yearNow.timestamp():
        # 下一年的生日
        birthday = datetime(birthday.year + 1, monthOfBirthday, dayOfBirthday)
    day = int((birthday.timestamp() - dt.timestamp()) / (24 * 60 * 60))
    print("生日:", day)
    return day


def getExpressLoveDay():
    # unixTimeStamp = 1599148800
    tz = pytz.timezone("Asia/Shanghai")
    now = datetime.now(tz)
    day = int((now.timestamp() - expressLoveTimestamp) / (24 * 60 * 60))
    print(day)
    print("相爱的天:", day)
    return day


class DailyWord:
    def __init__(self):
        self.sid = ""
        self.note = ""
        self.content = ""
        self.pic = ""

    def isValide(self) -> bool:
        return self.sid != ""

    def getDailyWordHtml(self) -> str:
        return '<br>每日一句<br>{}<br>{}<br><img src="{}" align="center">'.format(
            self.content, self.note, self.pic
        )


def getDailyWord() -> DailyWord:
    url = "http://open.iciba.com/dsapi"
    r = requests.get(url)
    r.encoding = "utf-8"
    result = r.json()
    dw = DailyWord()
    if result.get("sid"):
        dw.sid = result["sid"]
        dw.note = result["note"]
        dw.content = result["content"]
        dw.pic = result["fenxiang_img"]
    return dw


def sendDailyWordToWechatWork(dw: DailyWord):
    if dw.isValide():
        webhook = (
            f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={qywxWebhookKey}"
        )
        header = {"Content-Type": "application/json", "Charset": "UTF-8"}
        message = {
            "msgtype": "news",
            "news": {
                "articles": [
                    {
                        "title": "每日一句",
                        "description": dw.content,
                        "url": dw.pic,
                        "picurl": dw.pic,
                    }
                ]
            },
        }
        message_json = json.dumps(message)
        requests.post(url=webhook, data=message_json, headers=header)
    return


def sendAlarmMsg(mdTex):
    wechatwork(mdTex)


def wechatwork(tex):
    webhook = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={qywxWebhookKey}"
    header = {"Content-Type": "application/json", "Charset": "UTF-8"}
    message = {"msgtype": "markdown", "markdown": {"content": tex}}
    print(f"wechat send msg, key:{qywxWebhookKey}")
    print(message)
    message_json = json.dumps(message)
    try:
        requests.post(url=webhook, data=message_json, headers=header)
    except requests.exceptions.RequestException as e:
        print("unable to connect to wechat server, err:", e)
    except Exception as e2:
        print("send message to wechat server, err:", e2)
        sendAlarmMsg(str(e2))


def wxPusher(tex):
    url = "http://wxpusher.zjiecode.com/api/send/message"
    header = {"Content-Type": "application/json", "Charset": "UTF-8"}
    message = {
        "appToken": wxpushAppToken,
        "content": tex,
        "summary": "相爱一生",
        "contentType": 2,
        "topicIds": [6931],
        "url": "http://wxpusher.zjiecode.com",
    }
    message_json = json.dumps(message)
    try:
        info = requests.post(url=url, data=message_json, headers=header)
        print(info.text)
    except requests.exceptions.RequestException as e:
        print("unable to connect to wx, err:", e)
        sendAlarmMsg(str(e))
    except Exception as e:
        print("send message to wx, err:", e)
        sendAlarmMsg(str(e))


if __name__ == "__main__":
    h = getMsgHeader()
    w = getWeather()
    bd = getBirthDayOfLover()
    md = getMeetingDay()
    ed = getExpressLoveDay()
    dw = getDailyWord()

    # 企业微信
    w1 = w.getWeatherTextToWechatWork()
    # tex1 = '{}\n> 今天是我们相爱的<font color="warning"> {} </font>天\n我们已经相遇<font color="warning"> {}
    # </font>天({})\n距离你的生日还有<font color="warning"> {} </font>天\n\n{}'.format(
    #   h, ed, md,datetime.utcfromtimestamp(meetingTimestamp).strftime('%Y-%m-%d %H:%M:%S') , bd, w1
    #    )

    # 一行代码完成转换和格式化，并插入到原始字符串中

    tex1 = (
        '{}\n> 今天是我们相爱的<font color="warning"> {} </font>天（{}）\n'
        '我们已经相遇<font color="warning"> {} </font>天（{}）\n'
        '距离你的生日还有<font color="warning"> {} </font>天'
    ).format(
        h,
        ed,
        datetime.fromtimestamp(expressLoveTimestamp, tz=pytz.utc)
        .astimezone(pytz.timezone("Asia/Shanghai"))
        .strftime("%Y-%m-%d"),
        md,
        datetime.fromtimestamp(meetingTimestamp, tz=pytz.utc)
        .astimezone(pytz.timezone("Asia/Shanghai"))
        .strftime("%Y-%m-%d"),
        bd,
    )

    wechatwork(tex1)
    sendDailyWordToWechatWork(dw)

    # wxpusher
    h2 = getMsgHeaderToWechat()
    w2 = w.getWeatherTextToWechat()
    dw2 = dw.getDailyWordHtml()
    tex2 = (
        '{}<br> 今天是我们相爱的<font color="green"> {} </font>天（{}）<br>'
        '我们已经相遇<font color="green">{}</font>天（{}）<br>'
        '距离你的生日还有<font color="green"> {} </font>天<br><br>{}<br>{}'
    ).format(
        h2,
        ed,
        datetime.fromtimestamp(expressLoveTimestamp, tz=pytz.utc)
        .astimezone(pytz.timezone("Asia/Shanghai"))
        .strftime("%Y-%m-%d"),
        md,
        datetime.fromtimestamp(meetingTimestamp, tz=pytz.utc)
        .astimezone(pytz.timezone("Asia/Shanghai"))
        .strftime("%Y-%m-%d"),
        bd,
        w2,
        dw2,
    )
    wxPusher(tex2)
