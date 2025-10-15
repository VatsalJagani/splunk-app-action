# My App 1


OVERVIEW
--------
This is just a dummy App for splunk-app-action tests.


* Author - Vatsal Jagani
* Creates Index - False
* Uses KV Store - False
* Compatible with:
   * Splunk Enterprise version: 9.2, 9.1, 9.0, 8.2
   * OS: Platform Independent
   * Browser: Google Chrome, Mozilla Firefox, Safari


## What's inside the App

* No of XML Dashboards: **1**
* Approx Total Viz(Charts/Tables/Map) in XML dashboards: **5**



TOPOLOGY AND SETTING UP SPLUNK ENVIRONMENT
------------------------------------------
This app can be set up in two ways: 
  1. Standalone Mode: 
     * Install the `My App 1`.
  2. Distributed Mode: 
     * Install the `My App 1` on the search head.
     * App do not require on the Indexer or on the forwarder.


DEPENDENCIES
------------------------------------------------------------
* The App does not have any external dependencies.


INSTALLATION
------------------------------------------------------------
The App needs to be installed only on the Search Head.  

* From the Splunk Web home screen, click the gear icon next to Apps.
* Click on `Browse more apps`.
* Search for `My App 1` and click Install. 
* Restart Splunk if you are prompted.


DATA COLLECTION & CONFIGURATION
------------------------------------------------------------
* Nothing here


UNINSTALL APP
-------------
To uninstall app, user can follow below steps:
* SSH to the Splunk instance.
* Go to folder apps($SPLUNK_HOME/etc/apps).
* Remove the `my_app_1` folder from `apps` directory.
* Restart Splunk.


RELEASE NOTES
-------------
* Some release notes here.



SAVED-SEARCHES
---------------
* Nothing yet


LOOKUPS
-------
* Nothing yet


OPEN SOURCE COMPONENTS AND LICENSES
------------------------------
* N/A


CONTRIBUTORS
------------
* Vatsal Jagani


SUPPORT
-------
* Nothing here
