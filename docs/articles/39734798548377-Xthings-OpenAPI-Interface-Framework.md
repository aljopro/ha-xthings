# Xthings OpenAPI Interface Framework

> Source: https://developer.xthings.com/hc/en-us/articles/39734798548377-Xthings-OpenAPI-Interface-Framework

---
Here is the Illustration of Xthings OpenAPI interface below: 

**Request URL**

[https://api.u-tec.com/action](https://api.u-tec.com/action)

**API Authentication**

**Method 1:** Use the access token provided by the OAuth2.0 server in the Authorization header to send requests to execute actions in the OpenAPI service.

```auto
POST /action HTTP/1.1
Host: api.u-tec.com
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```

**Method 2:** You can also choose to add **"authentication"** to the request body to add an access token.

```auto
{
    "header": {

        ......
    },

    "authentication": {

        "type": "Bearer",

        "token": "<ACCESS_TOKEN>"
    },

    "payload": {

        ......
    },
}
```

⛱ You can choose either of the above methods; however, if both methods are used, the first method (using the Authorization header) takes precedence.

**Request Body**

```auto
{
    "header": {

        "namespace": "Uhome.User",

        "name": "Get",

        "messageId": "Unique identifier, preferably a version 4 UUID",

        "payloadVersion": "1"

    },
    "payload": {}
}
```

📌   _messageId Format Description: A universally unique identifier (UUID) version 4, such as \`d290f1ee-6c54-4b01-90e6-d701748f0851\`. This is a 36-character string made up of 32 hexadecimal digits and 4 hyphens. The string is divided into 5 parts, with character counts as follows: 8-4-4-4-12._

**Response Body**

```auto
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

            "lastName": "Jiang",

            "FirstName": "Jacobs"

        }

    }

}
```

**Response Error**

```auto
 {
    "header": {

        "namespace": "Uhome.User",

        "name": "Get",

        "messageId": "Matches the one in the request header."

        "payloadVersion": "1"
    },
    "payload": {

        "error": {

            "code": "INVALID_TOKEN",

            "message": "Message didn't include the authorization token or 

the token is invalid, expired, or malformed."

        }

    }

}
```