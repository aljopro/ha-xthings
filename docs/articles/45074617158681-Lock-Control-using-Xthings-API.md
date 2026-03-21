# Lock Control using Xthings API

> Source: https://developer.xthings.com/hc/en-us/articles/45074617158681-Lock-Control-using-Xthings-API

---
### POST    Lock Control

[https://api.u-tec.com/action](https://api.u-tec.com/action)

Body  raw (json)

```json
{
  "header": {
    "namespace": "Uhome.Device",
    "name": "Command",
    "messageId": "178854f9-1fa7-4432-89c3-456c3d4b984b",
    "payloadVersion": "1"
  },
  "payload": {
    "devices": [
      {
        "id": "64:E8:33:8E:20:D1",
        "command": {
          "capability": "st.lock",
          "name": "lock"
        }
      }
    ]
  }
}
```