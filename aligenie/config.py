# coding: utf-8

import logging

import voluptuous as vol
from homeassistant.helpers import config_validation as cv


MAIN = 'aligenie'
EXPIRE_HOURS = 'expire_hours'
DOMAIN       = 'aligenie'
LOGGER = logging.getLogger('component/aligenie')

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(EXPIRE_HOURS): cv.positive_int
    })
}, extra=vol.ALLOW_EXTRA)

DEVICE_TYPES_ICON = {
    'light': 'https://home-assistant.io/images/favicon-192x192.png',
    'sensor': 'https://home-assistant.io/images/favicon-192x192.png',
    'outlet': 'https://home-assistant.io/images/favicon-192x192.png',
    'switch': 'https://home-assistant.io/images/favicon-192x192.png',
}

DEVICE_TYPES = [
    'television',#: '电视',
    'light',#: '灯',
    'aircondition',#: '空调',
    'airpurifier',#: '空气净化器',
    'outlet',#: '插座',
    'switch',#: '开关',
    'roboticvacuum',#: '扫地机器人',
    'curtain',#: '窗帘',
    'humidifier',#: '加湿器',
    'fan',#: '风扇',
    'bottlewarmer',#: '暖奶器',
    'soymilkmaker',#: '豆浆机',
    'kettle',#: '电热水壶',
    'watercooler',#: '饮水机',
    'cooker',#: '电饭煲',
    'waterheater',#: '热水器',
    'oven',#: '烤箱',
    'waterpurifier',#: '净水器',
    'fridge',#: '冰箱',
    'STB',#: '机顶盒',
    'sensor',#: '传感器',
    'washmachine',#: '洗衣机',
    'smartbed',#: '智能床',
    'aromamachine',#: '香薰机',
    'window',#: '窗',
    'kitchenventilator',#: '抽油烟机',
    'fingerprintlock',#: '指纹锁'
    'telecontroller',#: '万能遥控器'
    'dishwasher',#: '洗碗机'
    'dehumidifier',#: '除湿机'
]

INCLUDE_DOMAINS = {
    'climate': 'aircondition',
    'fan': 'fan',
    'light': 'light',
    'media_player': 'television',
    'remote': 'telecontroller',
    'switch': 'switch',
    'vacuum': 'roboticvacuum',
    }

EXCLUDE_DOMAINS = [
    'automation',
    'binary_sensor',
    'device_tracker',
    'group',
    'zone',
    ]

ALL_ACTIONS = [
    'TurnOn',
    'TurnOff',
    'SelectChannel',
    'AdjustUpChannel',
    'AdjustDownChannel',
    'AdjustUpVolume',
    'AdjustDownVolume',
    'SetVolume',
    'SetMute',
    'CancelMute',
    'Play',
    'Pause',
    'Continue',
    'Next',
    'Previous',
    'SetBrightness',
    'AdjustUpBrightness',
    'AdjustDownBrightness',
    'SetTemperature',
    'AdjustUpTemperature',
    'AdjustDownTemperature',
    'SetWindSpeed',
    'AdjustUpWindSpeed',
    'AdjustDownWindSpeed',
    'SetMode',
    'SetColor',
    'OpenFunction',
    'CloseFunction',
    'Cancel',
    'CancelMode']


mapping = lambda dict, key: dict[key] if key in dict else key
TRANSLATIONS = {
    'cover': {
        'TurnOn':  'open_cover',
        'TurnOff': 'close_cover'
    },
    'vacuum': {
        'TurnOn':  'start',
        'TurnOff': 'return_to_base'
    },
    'light': {
        'TurnOn':  'turn_on',
        'TurnOff': 'turn_off',
        'SetBrightness':        lambda state, payload: ('turn_on', {'brightness_pct': mapping({'max': 100, 'min': 1}, payload['value'])}),
        'AdjustUpBrightness':   lambda state, payload: ('turn_on', {'brightness_pct': min(state.attributes['brightness'] * 100 // 255 + int(payload['value']), 100)}),
        'AdjustDownBrightness': lambda state, payload: ('turn_on', {'brightness_pct': max(state.attributes['brightness'] * 100 // 255 - int(payload['value']), 0)}),
        'SetColor':             lambda state, payload: ('turn_on', {"color_name": payload['value']})
    },
    'climate': {
        'TurnOn': 'turn_on',
        'TurnOff': 'turn_off',
        'SetTemperature': lambda state, payload: ('set_temperature', {'temperature': int(payload['value'])}),
        'AdjustUpTemperature': lambda state, payload: ('set_temperature', {'temperature': min(state.attributes['temperature'] + int(payload['value']), state.attributes['max_temp'])}),
        'AdjustDownTemperature': lambda state, payload: ('set_temperature', {'temperature': max(state.attributes['temperature'] - int(payload['value']), state.attributes['min_temp'])}),
        'SetMode': lambda state, payload: ('set_operation_mode', {'operation_mode': mapping({'cold': 'cool'}, payload['value'])}),
        'SetWindSpeed': lambda state, payload: ('set_fan_mode', {'fan_mode': mapping({'max': 'high', 'min': 'low'}, payload['value'])}),
    },
    'fan': {
        'TurnOn': 'turn_on',
        'TurnOff': 'turn_off',
        'SetWindSpeed': lambda state, payload: ('set_speed', {'speed':mapping({'max': 'high', 'min': 'low'}, payload['value'])}),
        'OpenSwing': lambda state, payload: ('oscillate', {'oscillating': True}),
        'CloseSwing': lambda state, payload: ('oscillate', {'oscillating': False}),
    }
}

PLACES = ["门口","客厅","卧室","客房","主卧","次卧","书房","餐厅","厨房","洗手间","浴室","阳台","宠物房","老人房","儿童房","婴儿房","保姆房","玄关","一楼","二楼","三楼","四楼","楼梯","走廊","过道","楼上","楼下","影音室","娱乐室","工作间","杂物间","衣帽间","吧台","花园","温室","车库","休息室","办公室","起居室"]

ALIASES = [{"key":"除湿机","value":["除湿机","除湿器"]},{"key":"冰箱","value":["冰箱"]},{"key":"风扇","value":["风扇","电风扇","落地扇","电扇","台扇","壁扇","顶扇","驱蚊风扇","暖风扇","净化暖风扇","冷风扇","塔扇"]},{"key":"窗帘","value":["窗帘","窗纱","布帘","纱帘","百叶帘","卷帘"]},{"key":"空气净化器","value":["净化器","空气净化器"]},{"key":"扫地机器人","value":["扫地机器人","扫地机","打扫机","自动打扫机"]},{"key":"加湿器","value":["加湿器","空气加湿器","加湿机","空气加湿机"]},{"key":"空气净化器","value":["空气净化器","空净","空气清洁器"]},{"key":"冰箱","value":["双开门冰箱","冰柜"]},{"key":"温控器","value":["温控器","温控"]},{"key":"地暖","value":["地暖"]},{"key":"洗碗机","value":["洗碗机","洗碗器"]},{"key":"干衣机","value":["干衣机","干衣器"]},{"key":"红外幕帘探测器","value":["幕帘"]},{"key":"声光报警器","value":["声光报警器"]},{"key":"水族箱控制器","value":["智能鱼缸","鱼缸"]},{"key":"电蒸箱","value":["电蒸箱"]},{"key":"遥控器","value":["遥控器"]},{"key":"暖气","value":["暖气","暖气机","电暖","电暖气"]},{"key":"空气清新机","value":["空气清新机"]},{"key":"热水器","value":["热水器","电热水器","燃气热水器"]},{"key":"灯","value":["灯","房灯","吸顶灯","床头灯","床灯","电灯","吊灯","台灯","落地灯","壁灯","挂灯","射灯","筒灯","灯带","灯条","暗藏灯","背景灯","阅读灯","柜灯","衣柜灯","天花灯","路灯","彩灯"]},{"key":"电饭煲","value":["电饭煲","电饭锅","饭煲","饭锅"]},{"key":"烤箱","value":["烤箱","嵌入式烤箱"]},{"key":"摄像头","value":["摄像头","摄像","摄像机"]},{"key":"插座","value":["插座","插头","排插单孔单控"]},{"key":"空气监测仪","value":["空气监测仪","空气检测器"]},{"key":"路由器","value":["路由器","路由","智能路由器"]},{"key":"抽油烟机","value":["抽油烟机","抽烟机","烟机"]},{"key":"饮水机","value":["饮水机"]},{"key":"净水器","value":["净水器；净水机"]},{"key":"晾衣架","value":["晾衣架","衣架","晒衣架"]},{"key":"报警器","value":["报警器"]},{"key":"电压力锅","value":["压力锅","高压锅"]},{"key":"微波炉","value":["微波炉"]},{"key":"取暖器","value":["取暖器","加热器"]},{"key":"电热水壶","value":["养生水壶","水壶","养生壶","热水壶","电水壶"]},{"key":"电热毯","value":["电热毯"]},{"key":"足浴器","value":["足浴器","足浴盆","洗脚盆"]},{"key":"暖灯","value":["暖灯"]},{"key":"浴霸","value":["浴霸"]},{"key":"空气炸锅","value":["空气炸锅"]},{"key":"面包机","value":["面包机"]},{"key":"消毒碗柜","value":["消毒碗柜","消毒柜"]},{"key":"电炖锅","value":["电炖锅","炖锅","慢炖锅"]},{"key":"豆浆机","value":["豆浆机"]},{"key":"血糖仪","value":["血糖仪"]},{"key":"电子秤","value":["电子秤","体重秤"]},{"key":"血压计","value":["血压计","血压器"]},{"key":"按摩仪","value":["按摩仪"]},{"key":"油汀","value":["油汀"]},{"key":"燃气灶","value":["燃气灶"]},{"key":"新风机","value":["新风机"]},{"key":"吸奶器","value":["吸奶器"]},{"key":"婴童煲","value":["婴童煲"]},{"key":"按摩椅","value":["按摩椅"]},{"key":"头带","value":["头带"]},{"key":"手环","value":["手环"]},{"key":"手表","value":["手表","表"]},{"key":"智能门控","value":["智能门锁","门锁","电子锁"]},{"key":"煤气盒子","value":["煤气盒子"]},{"key":"空气盒子","value":["空气盒子"]},{"key":"背景音乐系统","value":["背景音乐系统"]},{"key":"辅食机","value":["辅食机"]},{"key":"烟雾报警器","value":["烟雾报警器"]},{"key":"动感单车","value":["动感单车"]},{"key":"美容喷雾机","value":["美容喷雾机"]},{"key":"冰淇淋机","value":["冰淇淋机"]},{"key":"挂烫机","value":["挂烫机"]},{"key":"箱锁柜锁","value":["箱锁柜锁"]},{"key":"料理棒","value":["料理棒"]},{"key":"心率仪","value":["心率仪"]},{"key":"体温计","value":["体温计"]},{"key":"电饼铛","value":["电饼铛"]},{"key":"智能语音药盒","value":["智能语音药盒"]},{"key":"浴缸","value":["浴缸"]},{"key":"原汁机","value":["原汁机"]},{"key":"破壁机","value":["破壁机","超跑"]},{"key":"入墙开关","value":["单开开关"]},{"key":"保险箱","value":["保险箱"]},{"key":"料理机","value":["料理机"]},{"key":"榨油机","value":["榨油机"]},{"key":"电视盒子","value":["电视盒子","盒子","小米盒子","荣耀盒子","乐视盒子","智能盒子"]},{"key":"网关","value":["网关"]},{"key":"智能音箱","value":["音箱"]},{"key":"暖奶器","value":["暖奶器","热奶器","牛奶","调奶器","温奶器","冲奶机"]},{"key":"咖啡机","value":["咖啡机"]},{"key":"故事机","value":["故事机"]},{"key":"嵌入式电蒸箱","value":["嵌入式电蒸箱"]},{"key":"嵌入式微波炉","value":["嵌入式微波炉"]},{"key":"水浸探测器","value":["水浸探测器"]},{"key":"跑步机","value":["跑步机"]},{"key":"智能牙刷","value":["智能牙刷"]},{"key":"门禁室内机","value":["门禁室内机"]},{"key":"WIFI中继器","value":["WIFI中继器"]},{"key":"种植机","value":["种植机"]},{"key":"美容仪","value":["美容仪"]},{"key":"智能场景开关","value":["智能场景开关"]},{"key":"智能云音箱","value":["音箱"]},{"key":"投影仪","value":["投影仪","投影机","投影","背投"]},{"key":"门磁","value":["门磁"]},{"key":"血糖","value":["血糖仪"]},{"key":"磁感应开关","value":["磁感应开关"]},{"key":"红外探测器","value":["人体检测器","人体检测仪"]},{"key":"报警套件","value":["报警套件"]},{"key":"防丢报警器","value":["防丢报警器"]},{"key":"胎音仪","value":["胎音仪"]},{"key":"净水器","value":["净水器箱型"]},{"key":"洗衣机","value":["顶开式洗衣机","滚筒洗衣机"]},{"key":"足浴盆","value":["足浴盆"]},{"key":"洗脚盆","value":["洗脚盆","脚盆"]},{"key":"衣架","value":["衣架","衣架"]},{"key":"空气检测器","value":["空气检测器"]},{"key":"电饭锅","value":["电饭锅"]},{"key":"空调","value":["空调","空气调节器","挂式空调"]},{"key":"煤气灶","value":["煤气灶","煤气"]},{"key":"吹风机","value":["吹风机","电吹风"]},{"key":"门","value":["门"]},{"key":"烹饪机","value":["烹饪机"]},{"key":"电磁炉","value":["磁炉","电磁炉"]},{'key': '电视', 'value': ['电视机']}]
