# Switch Control using Xthings API

> Source: https://developer.xthings.com/hc/en-us/articles/45075158508441-Switch-Control-using-Xthings-API

---
### POST Switch Control

[https://api.u-tec.com/action](https://api.u-tec.com/action)

Body raw (json)

```json
{
  "header": {
    "namespace": "Uhome.Device",
    "name": "Command",
    "messageId": "94219111-6b72-40d4-949a-15c1795f70eb",
    "payloadVersion": "1"
  },
  "payload": {
    "devices": [
      {
        "id": "70:04:1D:35:66:2A",
        "command": {
          "capability": "st.switch",
          "name": "off"
        }
      }
    ]
  }
}
```