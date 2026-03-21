# Retrieve User Information using Xthings API

> Source: https://developer.xthings.com/hc/en-us/articles/45032812850841-Retrieve-User-Information-using-Xthings-API

---
### POST    Retrieve User Information

[https://api.u-tec.com/action](https://api.u-tec.com/action)

Retrieve the basic information of the current user.

**Body** raw (json)

```json
{
  "header": {
    "namespace": "Uhome.User",
    "name": "Get",
    "messageId": "<Unique identifier, preferably a version 4 UUID>",
    "payloadVersion": "1"
  },
  "payload": {}
}
```