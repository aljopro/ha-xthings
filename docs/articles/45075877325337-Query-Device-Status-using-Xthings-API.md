# Query Device Status using Xthings API

> Source: https://developer.xthings.com/hc/en-us/articles/45075877325337-Query-Device-Status-using-Xthings-API

---
### POST  Query Device Status

[https://api.u-tec.com/action](https://api.u-tec.com/action)

Through this interface, you can query the real-time status information of Xthings devices.

**Body** raw (json)

```json
{
    "header": {
        "namespace": "Uhome.Device",
        "name": "Query",
        "messageId": "Unique identifier, preferably a version 4 UUID",
        "payloadVersion": "1"
    },
    "payload": {
        "devices": [
            {
                "id": "<Device ID>"
            }
        ]
    }
}
```