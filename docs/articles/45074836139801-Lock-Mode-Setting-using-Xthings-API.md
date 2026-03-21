# Lock Mode Setting using Xthings API

> Source: https://developer.xthings.com/hc/en-us/articles/45074836139801-Lock-Mode-Setting-using-Xthings-API

---
### POST  Lock Mode Setting

[https://api.u-tec.com/action](https://api.u-tec.com/action)

Body raw (json)

```json
{
  "header": {
    "namespace": "Uhome.Device",
    "name": "Command",
    "messageId": "8137bbdb-7616-401c-bae8-76452e7aba94",
    "payloadVersion": "1"
  },
  "payload": {
    "devices": [
      {
        "id": "64:E8:33:8E:20:D1",
        "command": {
          "capability": "st.lock",
          "name": "setMode",
          "arguments": {
            "mode": 0
          }
        }
      }
    ]
  }
}
```