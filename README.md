# aligenie

直接使用 Home Assistant 作为服务器和 OAuth, 接入 Home Assistant 的大部分设备到天猫精灵

## 修改自:
- https://github.com/Yonsm/HAExtra
- https://github.com/feversky/aligenie
> 由衷地感谢大神们

## 变更:
- 修复 0.10x.x 版本无法启动的问题
- 支持自定义设备图标(天猫精灵中设备列表好看些)

## 开始使用
1. 下载 aligenie 文件夹并复制到 Home Assistant 的 custom_components 目录
2. 配置文件开启
```yaml
# configuration.yaml
aligenie:
    expire_hours: 30
```
> 想要开启调试, 需要增加
```yaml
# configuration.yaml

logger:
    default: info
```

3. 添加或修改自定义组件名称, 类型等
```yaml
# customize.yaml

switch.mi_power_strip:
  hagenie_zone: 卧室
  hagenie_deviceName: 小米插排
  hagenie_deviceType: outlet

light.gateway_light_xxx:
  hagenie_zone: 卧室
  hagenie_deviceName: 灯
  hagenie_deviceType: light

sensor.humidity_xxxxxxxxx:
  friendly_name: 湿度
  hagenie_zone: 卧室
  hagenie_deviceType: sensor
  hagenie_propertyName: humidity
```
上面各项为非必填项, 相应字段含义如下
|  字段   | 类型 | 说明 |
|  ----  | ----  | ----  |
| hagenie_zone | String | 设备区域 |
| hagenie_deviceName | String | 设备名称(天猫精灵设备列表中) |
| hagenie_deviceIcon | String | 设备图标URL |
| hagenie_deviceType | String | 设备类型 |
| hagenie_propertyName | String | 设备属性 |
