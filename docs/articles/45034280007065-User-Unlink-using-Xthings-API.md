# User Unlink using Xthings API

> Source: https://developer.xthings.com/hc/en-us/articles/45034280007065-User-Unlink-using-Xthings-API

---
### POST   User Unlink

[https://api.u-tec.com/action](https://api.u-tec.com/action)

Log out the current user.

Body raw (json)

```json
{
  "header": {
    "namespace": "Uhome.User",
    "name": "Logout",
    "messageId": "<Unique identifier, preferably a version 4 UUID>",
    "payloadVersion": "1"
  },
  "payload": {}
}
```