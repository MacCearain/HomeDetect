# HomeDetect
Raspberry PI and XBee Tests with Python

This is one of my first micro-projects with the Pi.  It also uses a few Xbee radios.  Finally, it's one of my first attempts at writing code in Python...  

This is yet another example of Monitoring Sensors in a remote location.  Most of of the sensors are connected to Xbee radios.  Additionally there is an Xbee radio directly attached to one of the USB ports on the Pi.  The distributed xbees simply broadcast sensor data.  The xbee on the Pi simply reads the broadcast sensor data.  In a prestep, each xbee radio was defined in the HomeDetect script and the definition of the sensors that are attached were configured directly in the code along with the monitors that determine if there is an issue to report.  HomeDetect also has the registered list of people to notify based on the Person Object.  When a notification is required the Monitor makes use of the McMail object to actually send emails / texts.  

The concept is that the Pi is the only device that has an internet conneciton and can email / text when a Monitor goes beyond tolerance.  No data is stored in this project.  All notifications are sent or not sent based on the rule embeded in the Monitor based on a single data point.  In other words, the monitors do not currently support extra messaging for Monitors that have been out of tolerance for long periods of time or in repeated fashions.  HomeDetect is the starting / controlling program.  The other files simply support HomeDetect.  Person -- is an implementation of a Person as an object.  McMail.py - is a an implementation of sending email via Google Gmail.  Rooms -- is an implementation of the Sensors, Monitors, and base Room objects.  

I hope somebody finds the code useful...

MacCearain
