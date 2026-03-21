# Retrieve Device List using Xthings API

> Source: https://developer.xthings.com/hc/en-us/articles/45075621965209-Retrieve-Device-List-using-Xthings-API

---
### POST Retrieve Device List

[https://api.u-tec.com/action](https://api.u-tec.com/action)

The Discovery interface describes the message used to identify the endpoints associated with a customer device account. You can issue this command, and Xthings OpenApi will respond with a list of all supported devices and their associated properties and capabilities.

Body raw (json)

```json
{
  "header": {
    "namespace": "Uhome.Device",
    "name": "Discovery",
    "messageId": "Unique identifier, preferably a version 4 UUID",
    "payloadVersion": "1"
  },
  "payload": {}
}
```