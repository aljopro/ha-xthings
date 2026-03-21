# Switch Level Control using Xthings API

> Source: https://developer.xthings.com/hc/en-us/articles/45075286010265-Switch-Level-Control-using-Xthings-API

---
### POST Switch Level Control

[https://api.u-tec.com/action](https://api.u-tec.com/action)

Body raw (json)

```json
{
  "header": {
    "namespace": "Uhome.Device",
    "name": "Command",
    "messageId": "53e0f2ab-5bfd-434d-90b5-062520ded4e6",
    "payloadVersion": "1"
  },
  "payload": {
    "devices": [
      {
        "id": "70:04:1D:35:66:2A",
        "command": {
          "capability": "st.switchLevel",
          "name": "setLevel",
          "arguments": {
            "level": 50
          }
        }
      }
    ]
  }
}
```