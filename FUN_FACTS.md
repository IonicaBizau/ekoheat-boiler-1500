# Reset touchscreen calibration

The firmware appears to request recalibration on the next startup after **three ash-plate endstop activations within five seconds**. I found this in the firmware; I have not tested it on the boiler.

There is also a software recalibration action, but I have not found its menu location yet.

## The boiler recognizes ignition at 18 lux

During startup, the firmware treats a processed light reading of **18 lux or higher** as ignition detected. If it fails to reach that threshold before the ignition timeout across three attempts, it reports **“Startup failed!”**

After the four-minute stabilization period, light below 18 lux can also trigger that error during the startup ramp when the low-light timer reaches 30 seconds; blocking waits can delay reporting. A reading of 18 or higher resets that timer.

[Binary analysis and evidence](analysis/startup-failure.md)
