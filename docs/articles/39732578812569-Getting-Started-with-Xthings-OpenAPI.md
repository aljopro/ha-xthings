# Getting Started with Xthings OpenAPI

> Source: https://developer.xthings.com/hc/en-us/articles/39732578812569-Getting-Started-with-Xthings-OpenAPI

---
**Get Started with Xthings OpenAPI**

**Development Workflow**

Register at [ULTRALOQ Community - We look forward to your joining and sharing your idea here](https://community.u-tec.com/?_gl=1*nh74hv*_gcl_au*MTIxOTE3MTgwNC4xNzMwOTYzMzE1*_ga*MTEyODc1NTgwOS4xNzIyOTkzNzg3*_ga_FLGV8Z6SQM*MTczNjgzMzg1MC4xMy4xLjE3MzY4MzUyMjkuNjAuMC41NzA4MDY2NDg.*_ga_X1S9Q61BX4*MTczNjgzMzg1MC41LjEuMTczNjgzNTIyOS42MC4wLjE3NjU4NjcwODE.) and then click on Sign Up.

The Xthings OpenAPI integration consists of three parts:

 \- OAuth2 Authentication Service for cloud access.

\- API Interfaces for device interaction.

\- Device Status Updates and Event Push Notifications.

**#OAuth2 Authentication Service**

OAuth 2.0 is the industry-standard protocol for authorization. OAuth 2.0 focuses on client developer simplicity while providing specific authorization flows for web applications, desktop applications, mobile phones, and living room devices.

**In the most typical scenario, your service does not get an access token directly: it must first get an authorization code and then exchange that for an access token (and, optionally, a refresh token so that it can request a new access token when the old access token expires). The following figure shows the relationship between the key components of account linking, which are described later in this topic. For an example of how users experience the account linking flow.**

**Authorization URI**

https://oauth.u-tec.com/authorize?response\_type=code&client\_id=_{Client ID}_&client\_secret=_{client Secret}_&scope=_{Scope}_&redirect\_uri=_{Redirect URI}_&state_\={state}_

**Callback Redirect URI**

https://_{Redirect URI}_?authorization\_code=_{code}_&state=_{state}_

**Access token URI**

https://oauth.u-tec.com/token?grant\_type=authorization\_code&client\_id=_{Client ID}_&code=_{code}_