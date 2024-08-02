import yaml


class WxPusherConfig:
    def __init__(self, appToken: str, topicIds: list):
        self.appToken = appToken
        self.topicIds = topicIds


class WeChatWorkConfig:
    def __init__(self, webhookKey: str):
        self.webhookKey = webhookKey


class WeatherConfig:
    def __init__(self, apiKey: str, city: int):
        self.apiKey = apiKey
        self.city = city


class LoverConfig:
    def __init__(
        self,
        expressLoveTimestamp: int,
        meetingTimestamp: int,
        monthOfBirthday: int,
        dayOfBirthday,
    ):
        self.expressLoveTimestamp = expressLoveTimestamp
        self.monthOfBirthday = monthOfBirthday
        self.dayOfBirthday = dayOfBirthday
        self.meetingTimestamp = meetingTimestamp


class Config:
    def __init__(
        self,
        wxPusher: WxPusherConfig,
        weChatWork: WeChatWorkConfig,
        weather: WeatherConfig,
        lover: LoverConfig,
    ):
        self.wxPusher = wxPusher
        self.weChatWork = weChatWork
        self.weather = weather
        self.lover = lover


def loadConfig(filePath: str) -> Config:
    with open(filePath, "r") as file:
        configData = yaml.safe_load(file)

    wxPusherConfig = WxPusherConfig(
        appToken=configData["wxPusher"]["appToken"],
        topicIds=configData["wxPusher"]["topicIds"],
    )

    weChatWorkConfig = WeChatWorkConfig(
        webhookKey=configData["wechatWork"]["webhookKey"]
    )

    weatherConfig = WeatherConfig(
        apiKey=configData["weather"]["apiKey"],
        city=configData["weather"]["city"],
    )

    loverConfig = LoverConfig(
        expressLoveTimestamp=configData["lover"]["expressLoveTimestamp"],
        meetingTimestamp=configData["lover"]["meetingTimestamp"],
        monthOfBirthday=configData["lover"]["monthOfBirthday"],
        dayOfBirthday=configData["lover"]["dayOfBirthday"],
    )

    return Config(
        wxPusher=wxPusherConfig,
        weChatWork=weChatWorkConfig,
        weather=weatherConfig,
        lover=loverConfig,
    )
