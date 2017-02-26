# MenloHacks Vivere
### Introduction
MenloHacks Vivere is the backend system for all day-of-operations.
It is written in Python using the Flask framework and uses MongoDB for its datastore.

All endpoints are relative to `api.menlohacks.com` and for endpoints that require
authorization the authorization token should be placed in the `X-MenloHacks-Authorization` field.

All parameters should be end in the body of POST requests formatted as JSON
(with content-type application/json) and all parameters for GET requests should
be included in the URL.

This document will be updated as new endpoints are created or as API specs change.

### Model
Every time an object is retrieved from the server, it will be represented as a JSON object.
Each JSON object will be uniform across the system by object type for uniform JSON parsing.

##### User
Clients cannot query information about a user directly.

##### MentorTicket

##### Fields
| Parameter Name| Description|
| ------------- |-------------|
| id | A unique identifier generated by the server |
| description | A brief description of the issue the user is experiencing|
| location | The physical location of the user within the venue|
| contact | The best way for a mentor to contact the user (phone number or email) |
| time_complete | The time the ticket was marked as closed. Will be null if the ticket is still open or expired. |
| time_created | The time the ticket was created |
| claimed | Has the ticket been claimed? |
| expired | Is the ticket expired |


Sample JSON

```json
{
    "claimed": false,
    "contact": "contact",
    "description": "description",
    "id": "58b2357f7a2f2e2e723e130e",
    "location": "location",
    "time_complete": null,
    "time_created": "2017-02-25T15:55:05.978298",
    "expired" : false
}
```

##### Event
##### Fields
| Parameter Name| Description|
| ------------- |-------------|
| id | A unique identifier generated by the server |
| short_description | A brief description of the event. The title.|
| long_description | A longer, more in depth description of the event for a detail view on a client.|
| location | The location in the venue the event is happening. See location object.|
| start_time | Time the event starts |
| start_time | Time the event ends |



Sample JSON

```json
{
  "end_time": "2017-02-24T16:14:00",
  "id": "58acf4077a2f2e921896da2e",
  "location": `location_object`,
  "long_description": "Sponsors unite!",
  "short_description": "Opening Ceremony",
  "start_time": "2017-02-16T16:14:00"
}
```

##### Location

##### Fields
| Parameter Name| Description|
| ------------- |-------------|
| id | A unique identifier generated by the server |
| name | The name of the location|
| map | A url with an image of the map for the location.|
| rank| A number in which to sort the location by. The rank will only appear if it is a primary location, one to show on the list of maps.|


```json
{
  "id": "58ad07c47a2f2e9dfdbac50b",
  "map": "https://api.menlohacks.com/location/image/58ad07c47a2f2e9dfdbac50b",
  "name": "test",
  "rank":1
}
```

##### Announcement

##### Fields
| Parameter Name| Description|
| ------------- |-------------|
| id | A unique identifier generated by the server |
| message | The announcement itself|
| message | The time the announcement was made|

```json
{
  "message": "Some message",
  "id": "58ae92f97a2f2ef7d88e59bc",
  "time": "2017-02-22T21:44:27",
}
```

### Response Format
All responses will be returned as JSON. Successful responses will be returned
with a 2xx code.

All successful responses will be formatted as shown in the example below.
```json
{
  "data": `JSON Object`,
  "success": true
}
```

All error messages the server is expected to return will be formatted as follows.
```json
{
  "error": "some error message" ,
  "success": false
}
```

### User Accounts

#### `POST user/create`
Creates a new user account. Note that this does not create a new account on the application site and thus should only be used for mentor accounts which do not need a full profile.

##### Parameters
| Parameter Name| Description| Required| Default |
| ------------- |-------------| -----  |  -----|
| name| The user's full name | YES | N/A |
| username| A unique username for the user. By convention, will be an email, but this will not be enforced server side. | YES | N/A|
| password | The user's password. | YES |N/A|

Successful requests will return a `201` with an authorization token.
An example successful request is shown below


```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ4ODA3MDQzMywiaWF0IjoxNDg4MDY2ODMzfQ.eyJ1c2VybmFtZSI6Imphc29uMyJ9.4j_SGsVkuV82PLkPccMzodukQw1PElksAn1l6DpT8sE"
  },
  "success": true
}
```

Errors will be returned for missing parameters or if an account already exists
with the specified username.

#### `POST user/login`
Login an already existing user. Returns a new authorization token.
##### Parameters
| Parameter Name| Description| Required| Default |
| ------------- |-------------| -----  |  -----|
| username| The username of the user. Typically their email. | YES | N/A|
| password | The user's password. | YES |N/A|

Successful logins will return a `200` with a response similar to below.
```json
{
  "data": {
    "name": "Jason Scharff",
    "token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ4ODA3MDk3OCwiaWF0IjoxNDg4MDY3Mzc4fQ.eyJ1c2VybmFtZSI6Imphc29uMyJ9.ix2vkW_W8POtrhM_vp5fi6caP9Fw08v2skYRmHQln4s"
  },
  "success": true
}
```
Errors may be thrown in the event of a missing parameter or an invalid
username and password combination.

### MenloHacks Live
The goal of the overall MenloHacks live platform is to provide MenloHacks
attendees a simple way to quickly see event information. Login is not required
for any MenloHacks Live related endpoints.

#### `GET times`
Returns the crucial times for the event. The primary purpose of this endpoint
is to construct a countdown for time remaining.

There are no parameters for this endpoint.
An example successful response is shown below.
```json
{
  "data": {
    "event_end_time": "2017-03-19T02:00:00",
    "event_start_time": "2017-03-18T00:15:00",
    "hacking_end_time": "2017-03-19T00:00:00",
    "hacking_start_time": "2017-03-18T02:00:00"
  },
  "success": true
}
```
No errors are specified by this endpoint.

#### `GET maps`
Returns a list of maps to help attendees navigate. Currently, there is only
a map for both levels of the gymnasium, but the system supports any number of maps.

There are no parameters for this endpoint.

An example successful response returns an array of maps. An example is shown below.

```json
{
  "data": [
    {
      "id": "58ad07c47a2f2e9dfdbac50b",
      "map": "https://api.menlohacks.com/location/image/58ad07c47a2f2e9dfdbac50b",
      "name": "Basement",
      "rank" : 1
    }
  ],
  "success": true
}
```

#### `GET announcements`
Returns a list of announcements that have been made in reverse chronological order.
Announcements can be made by event organizers by texting the MenloHacks phone number or
using the MenloHacks Vivere admin site. Because the number of announcements could exceed a reasonable
page limit, the announcement API is paginated.

##### Parameters
| Parameter Name| Description| Required| Default |
| ------------- |-------------| -----  |  -----|
| start| The next numbered announcement (reverse chronologically ordered) to fetch | NO |0|
| count | The number of announcements to fetch| NO |20|

No errors are specified for this endpoint.

An example successful response is shown below.
```json
{
  "data": [
    {
      "message": "test2",
      "id": "58ae92f97a2f2ef7d88e59bc",
      "time": "2017-02-22T21:44:27",
    },
    {
      "message": "test",
      "id": "58ae92d37a2f2ef7be114fab",
      "time": "2017-02-22T21:44:09",
    }
  ],
  "success": true
}
```

#### `GET events`
Returns a list of events on the schedule in chronological order by start time. Because the
number of events should be relatively small, all events are given as one response. Events can be added by organizers using
the MenloHacks Vivere admin site.

There are no parameters for this endpoint.

An example successful response is shown below.

```json
{
  "data": [
    {
      "end_time": "2017-02-24T16:14:00",
      "id": "58acf4077a2f2e921896da2e",
      "location": {
        "id": "58ad07c47a2f2e9dfdbac50b",
        "map": "http://0.0.0.0:5000/location/image/58ad07c47a2f2e9dfdbac50b",
        "name": "test"
      },
      "long_description": "Welcome to MenloHacks II",
      "short_description": "Opening Ceremony",
      "start_time": "2017-02-16T16:14:00"
    },
    {
      "end_time": "2017-04-16T14:32:00",
      "id": "58b222307a2f2e28ef102b65",
      "location": {
        "id": "58ad07c47a2f2e9dfdbac50b",
        "map": "http://0.0.0.0:5000/location/image/58ad07c47a2f2e9dfdbac50b",
        "name": "test"
      },
      "long_description": "A super long event.",
      "short_description": "Some long event",
      "start_time": "2017-04-08T14:32:00"
    }
  ],
  "success": true
}
```
No errors are specified.

### Mentorship
Version 1 of MenloHacks Vivere features a fairly straightforward mentorship system.
Users are able to create tickets and other users can claim them.
All tickets expire after 30 minutes if they are not claimed.

#### `POST mentorship/create`
Creates a ticket in the mentorship system. Authorization is required.
##### Parameters
| Parameter Name| Description| Required| Default |
| ------------- |-------------| -----  |  -----|
| description| A brief description of the issue the person needs help with | YES |N/A|
| location | The physical location the mentee is located at within the venue| YES |N/A|
| contact | The best way to reach the mentee (phone, email, etc)| YES |N/A|


Successful requests will return code `201`. An example successful response is below.
```json
{
  "data": {
    "claimed": false,
    "contact": "hello@menlohacks.com",
    "expired" : "false"
    "description": "Django admin site isn't loading CSS",
    "id": "58b225be7a2f2e2a3702419a",
    "location": "Main gym, near the front",
    "time_created": "2017-02-25T14:47:53.628224"
  },
  "success": true
}
```

Errors will be thrown with code `400` if a parameter is missing or no/an invalid
authentication token is provided.

#### `GET mentorship/queue`
Returns a list of tickets currently in the mentorship queue in chronological order.
Tickets older than 30 minutes are deemed expired and not included. Claimed or closed
tickets are not included. Login is not required.

##### Parameters
| Parameter Name| Description| Required| Default |
| ------------- |-------------| -----  |  -----|
| start| The next numbered ticket (chronologically ordered) to fetch | NO |0|
| count | The number of tickets to fetch| NO |20|

An example successful response is shown below.
```json
{
  "data": [
    {
      "claimed": false,
      "contact": "hello@menlohacks.com",
      "description": "Django admin site isn't loading CSS",
      "id": "58b2256b7a2f2e2922166a12",
      "expired" : false,
      "location": "Main gym, near the front",
      "time_created": "2017-02-25T14:33:35.474000"
    },
    {
      "claimed": false,
      "contact": "hello@menlohacks.com",
      "description": "Django admin site isn't loading CSS",
      "expired" : false,
      "id": "58b225947a2f2e2a154f472a",
      "location": "Main gym, near the front",
      "time_created": "2017-02-25T14:47:11.865000"
    }
  ],
  "success": true
}
```

No errors are specifically designated.

#### `GET mentorship/user/queue`
Gets all tickets created by the current logged in user. Requires login.

The API separates tickets into four buckets: closed, in-progress, expired, and open.
This is the only way for users to see tickets that are not currently open.

An example successful response is shown below.
```json
{
  "data": {
    "closed": [],
    "expired": [],
    "in_progress": [
      {
        "claimed": true,
        "contact": "hello@menlohacks.com",
        "description": "Help, please",
        "id": "58b22be07a2f2e2b2a26a40r",
        "location": "MS Gym",
        "expired" : false
        "time_created": "2017-02-25T15:09:52.996000"
      }
    ],
    "open": [
      {
        "claimed": false,
        "expired" : false,
        "contact": "hello@menlohacks.com",
        "description": "Help, please",
        "id": "58b22be07a2f2e2b2a26a40d",
        "location": "MS Gym",
        "time_created": "2017-02-25T15:09:51.996000"
      }
    ]
  },
  "success": true
}
```

An error will be thrown if the user is not logged in.

#### 'GET mentorship/user/claimed'
Returns a list of tickets claimed by the logged in user and currently open. Requires login.

There are no parameters for this endpoint.

Successful responses return a `200`. A sample response is provided below.

```json
{
  "data": [
    {
      "claimed": false,
      "contact": "contact",
      "description": "description",
      "expired": false,
      "id": "58b23d3d7a2f2e30b1394276",
      "location": "location",
      "time_complete": null,
      "time_created": "2017-02-25T16:26:19.839612"
    }
  ],
  "success": true
}
```





#### `POST mentorship/claim`
Claim a ticket for the current user.. Takes the ticket off of the queue. Must be logged in.

##### Parameters

| Parameter Name| Description| Required| Default |
| ------------- |-------------| -----  |  -----|
|id| The ID of the ticket to claim. | YES |N/A|

Successful queries will return a `200`. An example response is shown below.
```json
{
  "data": {
    "claimed": true,
    "contact": "hello@menlohacks.com",
    "description": "Help, please",
    "id": "58b22be07a2f2e2b2a26a40d",
    "location": "MS Gym",
    "time_created": "2017-02-25T15:09:51.996000",
    "expired" : false
  },
  "success": true
}
```

Errors will be thrown if there is no logged in user or a ticket does not exist with the specified ID.

#### `POST mentorship/reopen`
Re-open a previously claimed ticket. Also resets the time opened to give it an additional 30 minutes,
but preserves its spot in the queue. Both the mentor and mentee are able to re-open a ticket.

##### Parameters

| Parameter Name| Description| Required| Default |
| ------------- |-------------| -----  |  -----|
|id| The ID of the ticket to reopen. | YES |N/A|

A successful response will return a `200` An example response is shown below.

```json
{
  "data": {
    "claimed": false,
    "expired" : false,
    "contact": "hello@menlohacks.com",
    "description": "Help, please",
    "id": "58b22be07a2f2e2b2a26a40d",
    "location": "MS Gym",
    "time_created": "2017-02-25T15:09:51.996000"
  },
  "success": true
}
```

Errors will be thrown if no user is logged in, the user logged in is not the mentee or mentor,
or the ticket was already open.

##### Parameters

#### `POST mentorship/close`
Closes a ticket once the mentor is done with it or the mentee no longer needs help.

| Parameter Name| Description| Required| Default |
| ------------- |-------------| -----  |  -----|
|id| The ID of the ticket to close. | YES |N/A|

A successful response will return a `200` An example response is shown below.

```json
{
  "data": {
    "claimed": false,
    "contact": "hello@menlohacks.com",
    "description": "Help, please",
    "id": "58b22be07a2f2e2b2a26a40d",
    "location": "MS Gym",
    "expired" : false,
    "time_created": "2017-02-25T15:09:51.996000"
  },
  "success": true
}
```

Errors will be returned if no user is logged in or the person closing the ticket is not the mentee or mentor.

### Notifications

Notifications will be sent over Pusher. Notifications will be sent for updates
to the mentorship queue or for new announcements so that clients can react live.

Notifications regarding mentorship will be sent over the `com.vivere.mentor`channel and
notifications regarding new announcements will be sent over the `com.vivere.announcement` channel.
