# Lock User Management using Xthings API

> Source: https://developer.xthings.com/hc/en-us/articles/45078204040729-Lock-User-Management-using-Xthings-API

---
### POST  Lock User Management

[https://api.u-tec.com/action](https://api.u-tec.com/action)

Body raw (json)

```json
{
  "header": {
    "namespace": "Uhome.Device",
    "name": "Command",
    "messageId": "a4fdcb21-c6f4-43b3-a904-18d8823319e2",
    "payloadVersion": "1"
  },
  "payload": {
    "devices": [
      {
        "id": "64:E8:33:8E:20:D1",
        "command": {
          "capability": "st.lockUser",
          "name": "list"
        }
      }
    ]
  }
}
```