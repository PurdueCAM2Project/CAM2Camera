Welcome to the user documentation for the CAM2API. If you were unable to find the help you needed, or if you encountered an issue with out API, please let us know by email at cam2api@ecn.purdue.edu (note: check this email address). 

The first thing you need to do when using the API is to [authenticate yourself](#authentication) , and receive a JSON Web Token, which you will then provide to the request you send to the API. After that, depending on your permission level, you will be able to interact with the API. If you are a regular (non-admin) user, you will be able to [query our database](#query), and retrieve cameras' metadata that match your query. In addition to that, in case you are an admin user, you will also be able to [add new cameras](#post) to the database, as well as [update the existing ones](#put), or [delete cameras](#delete) from our database. For detailed description of each of these steps, read the corresponding section below.

<a name="authentication"></a> 
## Authentication
The authentication of CAM2API implements the client credential flow and it makes it possible to authenticate your request to the CAM2API without providing the identification every time. The access token would be a JWT type token and only stay valid for one hour. If you would like to extend the valid time for the access token, you can either request from the refresh_token endpoint before the refreshing time limit of the current access token wears out(1 day) or simply request for a new access token with client_id & client_secret.
![](http://imgur.com/Q34yM2N)
1.  Your application requests authorization 

The request is sent to the /token/ endpoint of the authentication service:
   POST http://127.0.0.1:8000/token/
The request will include parameters in the request body:
Request Body Parameters          Value
client_id                        Required. Set it to the client_id you acquired after registering your app.
client_secret                    Required. Set it to the client_secret you acquired after registering your app.

Example:
```bash
curl -X POST http://127.0.0.1:8000/token.json -d client_id=<client_id> -d client_secret=<client_secret>
{
  "expires in": 3600
  "token": "eyJ0eXA...O6YKF44"
  "token_type": "JWT"
}
```
2. Use the access token to access CAM2API

The JWT token allow you to access to all endpoints of the CAM2API without authorizing client_id&client_secret every time

Example:
```bash
curl -X GET -H "Authorization: JWT eyJ0eXA...O6YKF44" http://127.0.0.1:8000/cameras.json
{
  "camera_id": 123,
  "city": "Shinjuku-ku",
  "country": "JP"
  "lat": 35.6895,
  "lng": 139.6917,
  "source": Google,
  "source_url": "www.google.com",
  "resolution_w": 1920,
  "resolution_h": 1080,
  ...
} 
```

3. Refresh the access token for CAM2API

The access token can only be refreshed within one day since it got issued. 

The request is sent to the /refresh_token/ endpoint of the authentication service.
  POST http://127.0.0.1:8000/refresh_token/
The request will include parameter in the request body:
Request Body Parameters                    Value
token                                      Required. Set it to access token before the refreshing time goes off.

Example:
```bash
curl -X POST http://127.0.0.1:8000/refresh_token.json -d token="eyJ0eXA...O6YKF44" 
{
  "token": eyJ0eXA...QiOjE0OT^C"
}
```