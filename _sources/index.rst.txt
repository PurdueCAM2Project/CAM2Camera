.. CAM2API documentation master file, created by
   sphinx-quickstart on Tue Jul 18 00:21:13 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to CAM2API's documentation!
===================================
If you were unable to find the help you needed, or if you encountered an issue with out API, please let us know by email at cam2api@ecn.purdue.edu (note: check this email address). 

The first thing you need to do when using the API is to authenticate yourself, and receive a JSON Web Token, which you will then provide to the request you send to the API. After that, depending on your permission level, you will be able to interact with the API. If you are a regular (non-admin) user, you will be able to query our database, and retrieve cameras' metadata that match your query. In addition to that, in case you are an admin user, you will also be able to add new cameras to the database, as well as update the existing ones, or delete cameras from our database. For detailed description of each of these steps, read the corresponding section below.


.. toctree::
   :glob:
   :caption: User Documentation

   sources/Authentication.md
   sources/query.md

.. toctree::
   :glob:
   :caption: Developer Documentation
   
   sources/Post.md
   sources/Put.md
   sources/Delete.md
   



