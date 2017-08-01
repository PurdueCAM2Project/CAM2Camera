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