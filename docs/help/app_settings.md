# Application Settings
------

### Temperature Display
Select if temperature will be stored and displayed in Fahrenheit or Celsius

Go to *Settings* -> *Application Settings* -> *Temperature Display*
```
Choose Fahrenheit or Celsius.
SAVE choice
```

*Note:* You must restart the worker, or reboot the Pi to get this change to take effect.

### Polling Interval
How often will the system poll devices for measurment information.

Go to *Settings* -> *Application Settings* -> *Polling Interval*
```
Default is every 10 minutes.
Set polling interval minutes (2-60 minutes).
SAVE choice
```

*Note:* A shorter polling interval will provide faster updates for power-outlet controls, but may also shorten the battery life of some bluetooth devices.
*Note:* You must restart the worker, or reboot the Pi to get this change to take effect.

### Leaf Temperature Offset
The leaf temperature offset value (in celsius) used for VPD calculations.

Go to *Settings* -> *Application Settings* -> *Leaf Temperature Offset*
```
Default is -2 celsius
SAVE choice
```

*Note:* You should have a very thorough understanding of VPD calculations before modifying this value.
*Note:* You must restart the worker, or reboot the Pi to get this change to take effect.

### Measurement Retention
The number of days measurement data will be kept in the database.

Go to *Settings* -> *Application Settings* -> *Measurement Retention*
```
Default is 7 days
SAVE choice
```

*Note:* Retaining too much data will increase the database size, and may slow down queries and overall speed of the application.
*Note:* You must restart the worker, or reboot the Pi to get this change to take effect.

### Graph Hours
The number of hours shown when viewing measurement graphs.

Go to *Settings* -> *Application Settings* -> *Graph Hours*
```
Default is 24 hours
SAVE choice
```

*Note:* You must restart the worker, or reboot the Pi to get this change to take effect.

