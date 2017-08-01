<a name="query"></a>
## Queries
When querying the CAM2 database through our API, you can use three different methods:
* retrieve [all cameras](#all) from the database
* retrieve all cameras in the certain [radius](#radius) from a given geographical location
* retrieve certain [number of cameras](#count) closest to a given geographical location
In addition to these three different types of queries, you can apply certain filters to your query results, as described [here](#filters). Note: all examples below are performed using [curl](https://curl.haxx.se/), but any other software with similar capabilities can be used.
<a name="all"></a>
### Retrieve all cameras 
In order to get all cameras from the CAM2 database, you send a GET request to the API at the URI <cam2_domain>/cameras.json. The response to this request is a JSON representation of the cameras. 
For example:    
```bash
curl --request "GET" <cam2api_domain>/cameras.json
```
<a name="radius"></a>
### Query by radius 
In case you want to retrieve all cameras that are in certain radius from a given geographical location, you need to send the query specifying latitude and longitude of that location, as well as radius in which you want these cameras to be. The response to this request is a list of cameras in a JSON representation. Note: For latitude we use negative number south of equator and positive north of equator, for longitude negative values west of Prime Meridian and positive values east of Prime Meridian. Unit for the radius is kilometers.
Example:
```bash
curl --request "GET" <cam2api_domain>/query/lat=20.12,lon=13.621,radius=12.json
```
In this example, the result would be a JSON representation of all cameras that are in the 12 kilometers radius from the point 20.12 degrees North, 13.621 East. Note: latitude and longitude can have up to 4 decimal places, while radius has to be an integer.
<a name="count"></a>
### Query by number
If you want to get certain number of cameras that are closest to a given geographical location, you need to send the query specifying latitude and longitude of that location, as well as the number of cameras that you want to receive. The response to this request is a list of cameras in a JSON representation. Note: For latitude we use negative number south of equator and positive north of equator, for longitude negative values west of Prime Meridian and positive values east of Prime Meridian.
Example:  
```bash
curl --request "GET" <cam2api_domain>/query/lat=-11,lon=0.4562,count=54.json
```
In this example, the result would be a JSON representation of 54 cameras that are closest to the point 11 degrees South, 0.4562 East. Note: latitude and longitude can have up to 4 decimal places, while count has to be an integer.
### Filters <a name="filters"></a>
In addition to the queries described above, you can specify your request even further by adding some query parameters (filters). **These filters are applied to all cameras in the database, after which your particular query is processed.** You can specify as many query parameters as you want, and they will be connected by logical AND. The list of available filters:
* _city_ - city where cameras are located
* _state_ - state where cameras are located (only applicable to the US)
* _country_ - country where cameras are located
* _camera\_type_ - type of the cameras (Non_IP or IP)
* _lat_ - latitude of the cameras
* _lat\_min_ - minimum latitude of all cameras (everything north of the latitude)
* _lat\_max_ - maximum latitude of all cameras (everything south of the latitude)
* _lng_ - longitude of the cameras
* _lng\_min_ - minimum longitude of all cameras (everything east of the longitude)
* _lng\_max_ - maximum longitude of all cameras (everything west of the longitude)
* _framerate_ - framerate of the cameras
* _framerate\_min_ - minimum framerate of the cameras
* _framerate\_max_ - maximum framerate of the cameras
* _source_ - provider of the cameras
* _resolution\_w_ - resolution width of the cameras
* _resolution\_w\_min_ - minimum resolution width of the cameras
* _resolution\_w\_max_ - maximum resolution width of the cameras
* _resolution\_h_ - resolution height of the cameras
* _resolution\_h\_min_ - minimum resolution height of the cameras
* _resolution\_h\_max_ - maximum resolution height of the cameras
* _id_ - camera id
* _video_ - is camera a video stream (True or False)
* _outdoors_ - is camera outdoors (True or False)
* _traffic_ - is camera recording traffic (True or False)
* _inactive_ - is camera inactive (True or False)
* _added\_before_ - specifying the latest date that the cameras were added at (MM/DD/YYYY)
* _added\_after_ - specifying the earliest date that the cameras were added at (MM/DD/YYYY)
* _updated\_before_ - specifying the latest date that the cameras were updated at (MM/DD/YYYY)
* _updated\_after_ - specifying the earliest date that the cameras were updated at (MM/DD/YYYY)

Examples:

Instead of just getting all cameras from the database, we may want to get all cameras from India that have framerate between 0.3 and 20 frames per second. In that case, we would send the following request:
```bash
curl --request "GET" <cam2api_domain>/cameras.json?country=Kenya&framerate_min=0.3&framerate_max=20
```
If we want to get 54 cameras closest to the latitude -11 degrees and longitude 0.4562 degrees that have been added to the database after July 4th of 2017, we would send the following request:
```bash
curl --request "GET" <cam2api_domain>/query/lat=-11,lon=0.4562,count=54.json?added_after=07/04/2017
```