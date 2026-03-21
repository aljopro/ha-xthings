# Developer Foundational APIs

> Source: https://developer.xthings.com/hc/en-us/articles/39867633454361-Developer-Foundational-APIs

---
The Xthings foundational API reference contains the definitions for all skill interfaces. These APIs include general directives, response events, discovery, state reporting, change reporting, and error reporting.

**Uhome.Configure**

SET

This interface is primarily used to register URIs for Xthings related event notifications, such as device change notifications and event reports.

```auto
//Request Example

{
    "header": {

        "namespace": "Uhome.Configure",

        "name": "Set",

        "messageId": "Unique identifier, preferably a version 4 UUID",

        "playloadVersion": "1"

    },

    "payload": {

        "configure": {

            "notification": {

                "access_token": "xxxxx-xxxxx-xxxxx-xxxxx",

                "url": "https://xxxxxxxxx"
            }

        }

    }

}
```

acces\_token: When sending push notifications, essential valid authentication information is required. It is recommended that users periodically update this value to ensure connection security. For detailed usage instructions, refer to the [Event Notification](https://u1r8ceilva.feishu.cn/docx/VbGxdG0Yuok6rQxVKc6cRjZtnvg#share-IeVHdyjk7ocF6WxW8FGc1npHnmb) documentation.

URL: The registered notification URI address supports only http:// and https:// protocols. When using https://, the SSL/TLS certificate must be obtained from a trusted Certificate Authority (CA).

**Uhome.User**

GET

**Retrieve the basic information of the current user**.

```auto
//Request Example

{

    "header": {

        "namespace": "Uhome.User",

        "name": "Get",

        "messageId": "Unique identifier, preferably a version 4 UUID",

        "playloadVersion": "1"

    },

    "payload": {},
}

//Response

{

    "header": {

        "namespace": "Uhome.User",

        "name": "Get",

        "messageId": "Matches the one in the request header."

        "payloadVersion": "1"

    },

    "payload": {

        "user": {

            "id": "abc-ddd-eee-ff",

            "lastName": "Lastname",

            "FirstName": "Firstname"

        }

    }

}
```

Logout 

**Log out the current user.**

```auto
//Request Example

{
    "header": {

        "namespace": "Uhome.User",

        "name": "Logout",

        "messageId": "Unique identifier, preferably a version 4 UUID",

        "playloadVersion": "1"

    },

    "payload": {},

}
```

**Uhome.Device**

DISCOVERY

The Discovery interface describes the message used to identify the endpoints associated with a customer device account. You can issue this command and Xthings OpenApi will respond with a list of all supported devices and their associated properties and capabilities.

```auto
//Request Example

{
    "header": {

        "namespace": "Uhome.Device",

        "name": "Discovery",

        "messageId": "Unique identifier, preferably a version 4 UUID",

        "playloadVersion": "1"

    },
    "payload": {}

}

//Reponse

{
    "header": {

        "namespace": "Uhome.Device",

        "name": "Discovery",

        "messageId": "Matches the one in the request header."

        "payloadVersion": "1"
    },

    "payload": {

        "devices": [

            {
                "id": "Unique ID of the endpoint",

                "name": "Sample Lock",

                "category": "LOCK",

                "handleType": "utec-lock",

                "deviceInfo": {

                    "manufacturer": "U-tec",

                    "model": "U-Bolt-Pro-WiFi",

                    "hwVersion": "03.40.0023"

                },

                "customData": {

                    "userId": 123,

                    "otherData": "abc"

                }

            },

            {
                "id": "Unique ID of the endpoint",

                "name": "Sample Light",

                "type": "LIGHT",

                "handleType": "utec-bulb-color-rgbw",

                "deviceInfo": {

                    "manufacturer": "U-tec",

                    "model": "A19-C1",

                    "hwVersion": "03.40.0023"

                },

                "attributes": {

                     "colorModel": "RGB",

                     "colorTemperatureRange": {

                         "min": 2000,

                         "max": 9000,

                         "step": 1

                     }   

                }

            }

        ]

    }

}
```

**Device Parameter Description Example**

<table style="border-spacing: 0px; border-style: solid; border-width: 1px;"><tbody><tr style="height: 44px;"><td style="border-style: solid; border-width: 1px; height: 44px; text-align: center;"><strong>Attribute </strong><span style="font-family: Microsoft JhengHei;"><strong>Name</strong></span></td><td style="border-style: solid; border-width: 1px; height: 44px; text-align: center;"><strong>Data type</strong></td><td style="border-style: solid; border-width: 1px; height: 44px; text-align: center;"><strong>Description</strong></td></tr><tr style="height: 69px;"><td style="border-style: solid; border-width: 1px; height: 69px;"><span style="color: #1f2329;">id</span></td><td style="border-style: solid; border-width: 1px; height: 69px;"><span style="color: #1f2329;">String</span></td><td style="border-style: solid; border-width: 1px; height: 69px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">The unique ID of the device (currently the device's BLE MAC address or serial number, which is encrypted once more for privacy compliance).</span></span></td></tr><tr style="height: 23px;"><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;">name</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;">String</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Device Name</span></span></td></tr><tr style="height: 45px;"><td style="border-style: solid; border-width: 1px; height: 45px;"><span style="color: #1f2329;">category</span></td><td style="border-style: solid; border-width: 1px; height: 45px;"><span style="color: #1f2329;">String<span style="font-family: 宋体;">（</span>Enum)</span></td><td style="border-style: solid; border-width: 1px; height: 45px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Predefined Device Types</span></span></td></tr><tr style="height: 45px;"><td style="border-style: solid; border-width: 1px; height: 45px;"><span style="color: #1f2329;">handleType</span></td><td style="border-style: solid; border-width: 1px; height: 45px;"><span style="color: #1f2329;">String<span style="font-family: 宋体;">（</span>Enum)</span></td><td style="border-style: solid; border-width: 1px; height: 45px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Predefined Set of Device Functions</span></span></td></tr><tr style="height: 23px;"><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;">deviceInfo</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;">Object</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Device Basic Information</span></span></td></tr><tr style="height: 23px;"><td style="border-style: solid; border-width: 1px; height: 23px; text-align: center;"><span style="color: #1f2329;">manufacturer</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;">String</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Device Manufacturer</span></span></td></tr><tr style="height: 23px;"><td style="border-style: solid; border-width: 1px; height: 23px; text-align: center;"><span style="color: #1f2329;">model</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;">String</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Device Model</span></span></td></tr><tr style="height: 23px;"><td style="border-style: solid; border-width: 1px; height: 23px; text-align: center;"><span style="color: #1f2329;">hwVersion</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;">String</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Firmware Version</span></span></td></tr><tr style="height: 23px;"><td style="border-style: solid; border-width: 1px; height: 23px; text-align: left;"><span style="color: #1f2329;">attributes</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;">Object</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Configuration of parameters defined by `handleType`.</span></span></td></tr><tr style="height: 46px;"><td style="border-style: solid; border-width: 1px; height: 46px; text-align: center;"><span style="color: #1f2329;">colorModel</span></td><td style="border-style: solid; border-width: 1px; height: 46px;"><span style="color: #1f2329;">String</span></td><td style="border-style: solid; border-width: 1px; height: 46px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Color configuration types (e.g., RGB, HSL), to be defined.</span></span></td></tr><tr style="height: 51px;"><td style="border-style: solid; border-width: 1px; height: 51px;"><span style="color: #1f2329;">colorTemperatureRange</span></td><td style="border-style: solid; border-width: 1px; height: 51px;"><span style="color: #1f2329;">Object</span></td><td style="border-style: solid; border-width: 1px; height: 51px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Color Temperature Configuration</span></span></td></tr><tr style="height: 23px;"><td style="border-style: solid; border-width: 1px; height: 23px; text-align: center;"><span style="color: #1f2329;">min</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;">Integer</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Supported Minimum Color Temperature Value</span></span></td></tr><tr style="height: 23px;"><td style="border-style: solid; border-width: 1px; height: 23px; text-align: center;"><span style="color: #1f2329;">max</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;">Integer</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Supported M</span>axi<span style="font-family: 宋体;">mum Color Temperature Value</span></span></td></tr><tr style="height: 23px;"><td style="border-style: solid; border-width: 1px; height: 23px; text-align: center;"><span style="color: #1f2329;">step</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;">Integer</span></td><td style="border-style: solid; border-width: 1px; height: 23px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Supported Color Temperature Adjustment Steps</span></span></td></tr><tr style="height: 46px;"><td style="border-style: solid; border-width: 1px; height: 46px;"><span style="color: #1f2329;">......</span></td><td style="border-style: solid; border-width: 1px; height: 46px;">&nbsp;</td><td style="border-style: solid; border-width: 1px; height: 46px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Subsequently, parameters will be gradually added based on supported devices.</span></span></td></tr><tr style="height: 69px;"><td style="border-style: solid; border-width: 1px; height: 69px;"><span style="color: #1f2329;">customData</span></td><td style="border-style: solid; border-width: 1px; height: 69px;"><span style="color: #1f2329;">Object</span></td><td style="border-style: solid; border-width: 1px; height: 69px;"><span style="color: #1f2329;"><span style="font-family: 宋体;">Custom return data must be included with each device operation request to customer service. This can be used for purposes such as door unlock verification.</span></span></td></tr></tbody></table>

QUERY

Through this interface, you can query the real-time status information of **Xthings** devices.

```auto
//Request Example

{
    "header": {

        "namespace": "Uhome.Device",

        "name": "Query",

        "messageId": "Unique identifier, preferably a version 4 UUID",

        "playloadVersion": "1"

    },

    "payload": {

        "devices": [

            {
                "id": "Device ID from discovery list",

                "customData": {

                    "userId": 123,

                    "otherData": "abc"

                }

            },

            {

                "id": "Device ID from discovery list"

            }

        ]

    }

}

//Response

{

    "header": {

        "namespace": "Uhome.Device",

        "name": "Query",

        "messageId": "Matches the one in the request header."

        "payloadVersion": "1"

    },

    "payload": {

        "devices": [

            {

                "id": "Unique ID of the endpoint",

                "states": [

                    {

                        "capability": "st.healthCheck",

                        "name": "status",

                        "value": "online"

                    },

                    {

                        "capability": "st.Lock",

                        "name": "lockState",

                        "value": "locked"

                    },

                    {

                        "capability": "st.BatteryLevel",

                        "name": "level",

                        "value": 2

                    }

                ]

            }

        ]

    }

}
```

COMMAND

**Handle the Command request by triggering the commands for the list of devices.**

```auto
//Request Example

{

    "header": {

        "namespace": "Uhome.Device",

        "name": "Command",

        "messageId": "Unique identifier, preferably a version 4 UUID",

        "playloadVersion": "1"

    },

    "payload": {

        "devices": [

            {

                "id": "Device ID from discovery list",

                "customData": {

                    "userId": 123,

                    "otherData": "abc"

                },

                "command": {

                    "capability": "st.switch",

                    "name": "setLevel",

                    "arguments": {

                        "level": 100

                    }

                }

            }

        ]

    }

}

//Reponse

{

    "header": {

        "namespace": "Uhome.Device",

        "name": "Command",

        "messageId": "Matches the one in the request header."

        "payloadVersion": "1"

    },

    "payload": {

        "devices": [

            {

                "id": "Unique ID of the endpoint",

                "states": [

                    {

                        "capability": "st.deferredResponse",

                        "name": "seconds",

                        "value": 10

                    }

                ]

            }

        ]

    }

}
```