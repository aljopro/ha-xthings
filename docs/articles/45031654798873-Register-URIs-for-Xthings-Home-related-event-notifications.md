# Register URIs for Xthings Home-related event notifications

> Source: https://developer.xthings.com/hc/en-us/articles/45031654798873-Register-URIs-for-Xthings-Home-related-event-notifications

---
### POST   **Register Notification URL**

[https://api.u-tec.com/action](https://api.u-tec.com/action)

This interface is primarily used to register URIs for Xthings Home-related event notifications, such as device change notifications and event reports.

**access\_token:** When sending push notifications, essential valid authentication information is required. It is recommended that users periodically update this value to ensure connection security. For detailed usage instructions, refer to the Event Notification documentation

**URL:** The registered notification URI address supports only http:// and https:// protocols. When using https://, the SSL/TLS certificate must be obtained from a trusted Certificate Authority (CA).

**Body** raw (json)

```json
{
    "header": {
        "namespace": "Uhome.Configure",
        "name": "Set",
        "messageId": "<Unique identifier, preferably a version 4 UUID>",
        "payloadVersion": "1"
    },
    "payload": {
        "configure": {
            "notification": {
                "access_token": "<access_token>",
                "url": "<notification_url>"
            }
        }
    }
}
```