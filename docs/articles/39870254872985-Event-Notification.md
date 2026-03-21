# Event Notification

> Source: https://developer.xthings.com/hc/en-us/articles/39870254872985-Event-Notification

---
📌 Under normal procedures, after successful OAuth2 authentication, developers can update the [Notification Url](https://u1r8ceilva.feishu.cn/docx/VbGxdG0Yuok6rQxVKc6cRjZtnvg#share-QlXDdRPybooy4uxCqr3cgdKenVb)  through the registration interface.

Request Authentication

POST <path> HTTP/1.1  

Host: <host>  

Content-Type: application/json  

Authorization: Bearer **<ACCESS\_TOKEN>**

**Uhome.Notification**

DeviceState

{  

    "header": {  

        "namespace": "Uhome.Notification",  

        "name": "DeviceState",  

        "messageId": "Unique identifier, preferably a version 4 UUID",  

        "playloadVersion": "1"  

    },  

    "payload": {  

        "devices": \[  

            {  

                "id": "Device ID from discovery list",  

                "states": {  

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

                }  

            }  

        \]  

    }  

}

DeviceSync

{  

    "header": {  

        "namespace": "Uhome.Notification",  

        "name": "DeviceSync",  

        "messageId": "Unique identifier, preferably a version 4 UUID",  

        "playloadVersion": "1"  

    },  

    "payload": {  

        "devices": \[  

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

                "handleType": "[utec-bulb-color-rgbw](https://developer.smartthings.com/docs/devices/cloud-connected/device-handler-types)",  

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

        \]  

    }  

}

DeviceDelete

{  

    "header": {  

        "namespace": "Uhome.Notification",  

        "name": "DeviceDelete",  

        "messageId": "Unique identifier, preferably a version 4 UUID",  

        "playloadVersion": "1"  

    },  

    "payload": {  

        "devices": \[  

            {  

                "id": "Unique ID of the endpoint"  

            },  

            {  

                "id": "Unique ID of the endpoint"  

            }  

        \]  

    }  

}