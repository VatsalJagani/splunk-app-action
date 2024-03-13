# Correct App Inspect Test App


OVERVIEW
--------
Test app for splunk-app-action.

* Author - Vatsal Jagani
* Creates Index - False
* Compatible with:
   * Splunk Enterprise version: 9.0.x, 8.2.x
   * OS: Platform Independent
   * Browser: Does not have UI.


## What's inside the App

* No of Custom Inputs: **1**



TOPOLOGY AND SETTING UP SPLUNK ENVIRONMENT
------------------------------------------
There are two ways to setup this app:
  1. Standalone Mode: 
     * Install the `App Inspect Pass`.
  2. Distributed Mode:
     * The Add-on is required on the Search Head for field extraction. Input configuration is not required on the Search Head.
     * Install the `App Inspect Pass` on the universal forwarders on Windows and configure it. (You can do it from the Deployment Server.)
     * Install the Add-on on a heavy forwarder if forwarders are sending data to Heavy Forwarder, otherwise install it on Indexers for data parsing. Input configuration is not required for both indexers and heavy forwarders.


DEPENDENCIES
------------------------------------------------------------
* There are no external dependencies for this Add-on.


INSTALLATION
------------------------------------------------------------
* From the Splunk Home page, click the gear icon next to Apps.
* Click `Browse more apps`.
* Search for `App Inspect Pass`.
* Click `Install`.
* If prompted, restart Splunk.


DATA COLLECTION & CONFIGURATION
------------------------------------------------------------



UNINSTALL ADD-ON
-------------
1. SSH to the Splunk instance.
2. Navigate to apps ($SPLUNK_HOME/etc/apps).
3. Remove the `app_inspect_pass` folder from the `apps` directory.
4. Restart Splunk.


RELEASE NOTES
-------------
None


OPEN SOURCE COMPONENTS AND LICENSES
------------------------------
* N/A


CONTRIBUTORS
------------
* Vatsal Jagani



SUPPORT
-------
* None
