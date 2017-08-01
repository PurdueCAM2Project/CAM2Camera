<a name="delete"></a>
## Deleting cameras
If you are a CAM2 admin, you will have the permissions to delete cameras from our database using the API. In order to do this, you have to know the camera_id of the camera that you want to delete. Once you have that information, you need to send DELETE request to the API to the URL <cam2api_domain>/<camera_id>.json, and the selected camera will be deleted.

Example:
```bash
curl --request "DELETE" <cam2api_domain>/1234.json
```
In this example, camera with the camera_id 1234 would be deleted from the database