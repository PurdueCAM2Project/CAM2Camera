<a name="post"></a>
## Adding new cameras
In case you have admin permissions, you will be able to add new cameras to the database. In that case, here is the list of attributes that each camera needs in order to be added to the database:

**Required**:
* _camera\_id_ - id of the camera (has to be unique)
* _lat_ - latitude where camera is located
* _lng_ - longitude where camera is located
* _ip_ or _url_ - one of the two, depending if you are adding IP or Non_IP camera (has to be unique)

**Highly suggested** (These can sometimes be determined from the latitutude-longitude combination, but in some cases this is not possible, so the data provided by the user is used instead):
* _city_ - city where the camera is located

**Optional**:
* _port_ - only relevant if it is an IP camera, if nothing specified default is 80
* _source_ - provider of the camera
* _source\_url_ - url of the camera provider
* _description_ - description of the camera (max 100 characters)
* _framerate_ - framerate of the camera (frames per second)
* _resolution\_w_ - resolution width of the image provided by the camera
* _resolution\_h_ - resolution height of the image provided by the camera
* _is\_video_ - camera is a video stream (True or False)
* _outdoors_ - camera is outdoors (True or False)
* _traffic_ - camera recording traffic (True or False)
* _inactive_ - camera is not active (True or False)

When POST request is sent to the server at the URI <cam2api_domain>/cameras, server will either respond with the camera's JSON showing the camera as added to the database, or it will return appropriate error code and the message describing the error that was encountered while adding camera to the database.

Example of a bash script adding a camera:
```bash
#!/bin/bash
DATA='{"camera_id": 13452,
       "city": "Nairobi",
        "ip": "10.0.0.11",
        "lat": -1.2804,
        "lng": 36.8163,
        "source": "google",
        "source_url": "www.google.com",
        "resolution_w": 1920,
        "resolution_h": 1080}'
curl --header "Content-Type: application/json" --data "$DATA" <cam2api_domain>/cameras/
```