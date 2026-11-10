# Ekoheat 1500 controller guide

This is an alternative reading guide for the Ekoheat touch controller, based on the two supplied manuals and static analysis of original DTX9003 firmware 1.72 and 1.73. It covers initial setup, normal startup, the visible controls, and the documented menu items. The manuals describe different controller revisions: names, ranges, defaults, and screen layout can differ on the installed 1.73 controller. Read the value shown on the actual screen before changing it.

**Source key:** [2014 user manual](ekopower%20ekoheat%20installation%20manual%202%202014%20eng.pdf) is the 23-page manual; [series installation manual](ekoheat_series.pdf) is the 54-page manual. Page references below are PDF page numbers. The [firmware analysis](../analysis/README.md) provides evidence for code-level behavior; that behavior has not been measured on this boiler in every mode.

## The main screen

The [series manual diagram, PDF page 24](ekoheat_series.pdf#page=24) numbers the main-screen items. The older manual describes the same main buttons on [PDF page 4](ekopower%20ekoheat%20installation%20manual%202%202014%20eng.pdf#page=4).

| Display or button | What it does |
| --- | --- |
| **Boiler temperature setpoint** | Shows the requested boiler-water temperature. Touch its value, enter a new number on the keypad, and press **OK** to save. The series manual gives 65–80 °C; the 2014 manual lists 40–80 °C and advises against setting below 60 °C. Use the range shown by your controller. |
| **DHW / VVB setpoint** | Appears when a domestic hot-water tank and its control are enabled. Touch the value to change the requested tank temperature, then press **OK**. The series manual lists 15–65 °C; the older VVB menu lists 0–70 °C. The tank sensor and diverter valve must actually be installed for this function to work. |
| **Flame / lux** | Shows the light level sensed at the burner. This is feedback from the flame detector, not a temperature reading. In the analyzed firmware, a processed reading of at least 18 counts/lux is the ignition-detected threshold. |
| **Fan %** | Shows the current fan command or functioning percentage. It changes with ignition, modulation, and cleaning. This is a status display; fan tuning is in the technical menu. |
| **Burning % / modulation %** | Shows the current requested operating power as a percentage. It is not the same as measured thermal output. |
| **Auger symbol** | Indicates fuel-feed operation. Its presence does not measure the mass of pellets actually delivered. |
| **DHW symbol and temperature** | Shows the hot-water circuit when configured. |
| **Circulation-pump symbol** | Shows the controller's pump command. Pump operation also depends on configured thresholds and the connected hydraulic system. |
| **Start / Stop** | Starts boiler operation when stopped; the label changes to **Stop**. Pressing **Stop** requests the normal shutdown sequence; let it complete. The 2014 manual describes this on PDF page 4. |
| **Info** | Opens counters and identification data. It does not start an update. |
| **Menu** | Opens user/configuration, fitter/service, and other documented functions. |

The numeric editor shown on [series PDF page 25](ekoheat_series.pdf#page=25) has number keys, **X** to cancel, and **OK** to accept a value. **Back** returns one menu level; **Menu** returns to the menu; **Exit** or **Finish** returns toward the main screen. **Next** opens the next page. A **No / Yes** control is a toggle, and **Save and restart** applies some scheduled-mode changes. Button text may vary with language and firmware.

## First setup and normal startup

### Before the first Start

The [series manual, PDF page 23](ekoheat_series.pdf#page=23) requires a filled and bled water circuit, a correctly connected flue, installed feed auger, suitable pellets, and open flow/return valves. It specifies 1–1.5 bar during installation filling and warns against switching on without water. The [2014 manual, PDF page 3](ekopower%20ekoheat%20installation%20manual%202%202014%20eng.pdf#page=3) also calls for an earthed power connection. These installation checks are for qualified personnel.

When power is connected, the older manual says the EKOPOWER logo appears, followed after about five seconds by the graphical screen. Open **Info** and verify the selected boiler model is **Ekoheat 1500**. Set date and time if scheduling is used. Check the ash-plate movement and calibrate the external feed auger before the initial Start. A firmware update may reset settings and select Ekoheat 900, so repeat the model and calibration checks after an update. See [2014 PDF pages 3 and 16](ekopower%20ekoheat%20installation%20manual%202%202014%20eng.pdf#page=3) and [series PDF pages 23 and 29–30](ekoheat_series.pdf#page=23).

### Feed-auger calibration buttons

The illustrated procedure is on [series PDF pages 29–30](ekoheat_series.pdf#page=29), with a shorter description on [2014 PDF page 3](ekopower%20ekoheat%20installation%20manual%202%202014%20eng.pdf#page=3). It measures the pellets actually delivered by the external auger; the entered mass is used for fuel dosing and combustion calculations.

1. With the boiler stopped, a qualified person disconnects the flexible feed tube at the outlet and places a suitable collection container. In the menu, open **Feed auger calibration** / **Calibration auger**.
2. **Manual start** / **Manual operation → Start** runs the external auger to fill it. The manuals show running it for at least 15 minutes, then using **Stop**. Empty collected pellets back into the hopper as directed.
3. **Doses → Start** runs a 200-dose test. The displayed dose counter counts down to zero. **Reset** resets that test counter; it is not the Info-counter Reset.
4. Weigh the 200-dose collection. Touch **Weight after 200 doses** / **Amount by 200 dosings**, enter the measured grams with the keypad, and press **OK**. The illustrated 1450 g is an example/default, not a substitute for the measured amount.
5. The series manual says to perform the measurement twice. Reconnect the feed tube and return to the normal screen before starting the boiler.

The manuals call for recalibration at initial installation and after relevant fuel or feed changes. The older manual also calls for a repeat after 200 kg or 14 days, when the hopper empties, or when pellet size/brand changes. A wrong calibration changes the fuel delivered during ignition and operation.

### What happens after Start

The main **Start** button requests operation; the controller then manages fuel feed, ignition, flame detection, stabilization, and running power. The following details come from [original-firmware startup analysis](../analysis/startup-failure.md) and the [1.72/1.73 comparison](../analysis/v1.73/comparison.md#important-rules-that-remain), not from a timed hardware trace:

1. The controller calculates an initial pellet charge from the model/configuration and auger calibration, runs the feed, and starts the ignition path. Do not infer delivered pellet mass from the auger icon alone.
2. It waits for the processed flame reading to reach **18 or higher**. The factory ignition-wait field in the compared original profiles is 600 seconds, but the configured value can matter. If the wait expires without sufficient flame, the code counts a failed attempt and may retry.
3. The original code permits **three total ignition attempts**. The second charge calculation uses a quarter of the initial base; the third attempt bypasses that normal charging setup. After the final failed wait, error code 4 maps to **Startup failed!**
4. After flame detection, the ignition request turns off and a nominal **240-second stabilization** wait occurs. The program then ramps toward running conditions. During that ramp, a processed flame reading below 18 for more than 29 nominal timer seconds can also lead to **Startup failed!** Blocking waits can delay when the message appears.
5. Once running, the controller modulates fan and fuel feed against temperature demand and configuration. Cleaning, DHW priority, pump control, and time-programmer or on/off mode can alter visible status. The exact duration of each stage depends on settings and conditions.

**Stop** requests shutdown; allow the boiler to finish its normal sequence before cleaning, opening, or updating. A physical mains disconnect is not a substitute for a normal stop. The [series manual, PDF page 38](ekoheat_series.pdf#page=38) describes the Stop button and full power-off separately.

## Info screen

The [series manual, PDF page 26](ekoheat_series.pdf#page=26) and [2014 manual, PDF page 4](ekopower%20ekoheat%20installation%20manual%202%202014%20eng.pdf#page=4) list:

| Item | Meaning |
| --- | --- |
| **Operating hours** | Accumulated boiler operating time. |
| **Number of ignitions** | Ignition counter. The series manual shows a **Reset** control for the counters; the older manual associates resetting the ignition count with replacing the igniter. Record values before resetting. |
| **Software version** | Version text shown by the application. A clock-only derivative keeps its source version text, so this line alone cannot distinguish original from clock-only firmware. |
| **Controller ID / Control card ID** | Identifier of the electronic control, not a chip part number or proof of firmware identity. |
| **Boiler model** | Controller's selected model. It must match the physical Ekoheat 1500 boiler. |

## User settings / Configuration

The 2014 controller calls this **Menu → User settings**; the series manual calls it **Menu → Configuration**. The available entries and ranges differ by manual. These controls are described in [2014 PDF pages 4–6 and 9](ekopower%20ekoheat%20installation%20manual%202%202014%20eng.pdf#page=4) and [series PDF pages 27–31](ekoheat_series.pdf#page=27).

| Item or button | What happens |
| --- | --- |
| **Boiler temperature** | Changes the water-temperature target. The controller regulates toward it; the actual water temperature can differ while starting or responding to load. |
| **Cleaning settings / Cleaning → Adjust** | Sets automatic fume-cleaning interval, fan-cleaning duration, and fuel quantity between burner/ash-plate cleaning cycles. The series manual lists 45 minutes and 10 seconds as default fume-cleaning values, and 1.9 kg as the Ekoheat 1500 burner-cleaning interval. The older manual lists a narrower fan-cleaning time range. These parameters affect physical cleaning devices. |
| **Time programmer / Summer operation** | Enables scheduled run periods, up to five per day. Enter start and end hour/minute values, toggle **No → Yes**, then use **Save and restart**. The series manual says at least 1 hour 30 minutes per period; the older manual says at least 1 hour. **Reset** clears periods in the series-manual layout. A schedule icon/sun may appear on the main screen. |
| **Feed auger calibration** | Opens the manual-feed and 200-dose weighing workflow described above. |
| **Burner lubrication** | Series-manual entry that positions the burner cleaning device for lubrication maintenance. It moves hardware and is not a general operating control. |
| **Language** | Selects the display language; the older manual presents flags. |
| **Date and time / Watch and date** | Sets the real-time clock. The time programmer depends on this being correct. |
| **Pump stop** | Older-manual setting for the circulating-pump temperature threshold: 5–85 °C, default 45 °C. The older manual advises against zero and gives a separate summer-operation recommendation. The later series manual has **Minimum pump temperature** in Service instead, with a different range/default. |
| **VVB Priority** | Older-manual name for DHW priority. **Yes / No** enables it when the required tank sensor and motor valve are installed. **VVB Temp** sets the tank target; **VVB Drop** sets how far the tank can cool before reheating is requested. The series manual places similar controls under Service → DHW circuit. |
| **Correct content of hopper** | Older-manual entry for recording the approximate pellets added. The displayed remaining kilograms are a calculated estimate; the older manual explicitly says this number does not control the boiler. Original 1.73 separately adds a low-fuel warning path; its exact relationship to this displayed estimate has not been verified. |
| **Clean now** | Older-manual manual ash-plate movement, usually one or five cycles. The later series manual places **Manual ash cleaning** in Service. It actuates a physical mechanism. |
| **Finish / Exit** | Leaves the current menu or returns to the main screen. |

## Fitter settings / Service

The 2014 layout calls this **Menu → Fitter settings**; the later layout uses **Menu → Service**, with a default code of 1234 in [series PDF page 26](ekoheat_series.pdf#page=26). The manuals reserve technical changes and output tests for qualified personnel because they can alter combustion, pump behavior, and safety. The following is an explanation of what the buttons mean, not a set of new target values.

| Item | Function and effect |
| --- | --- |
| **Fuel** | Calibrated kilograms consumed per hour at 100% power. The manuals give 3.1 kg/h for Ekoheat 1500. This is a configuration value, not a live scale reading. |
| **Ignition fuel / Fuel for ignition** | Pellet mass charged for ignition. The series manual lists 140 g as a 1500 default; the 2014 manual gives a broader 150–200 g standard band. Incorrect adjustment can impair ignition. |
| **Travel of bottom plate / Burner cleaning device movement** | Sets movement time for the ash/burner cleaning plate. The older manual gives 0–100 seconds and standard 40; the series manual describes 38–42 seconds. The endstop and plate position still matter; time alone does not prove correct travel. |
| **Fan functioning / Efficiency for flue suction** | Fan percentages by modulation level and a **General** adjustment affecting the curve. These settings influence combustion air. The two manuals describe them differently; copy actual values before any change. |
| **Minimum / Maximum power** | Lower and upper modulation limits, expressed as percentages of nominal boiler power. |
| **Optional equipment** | Older-manual **No / Yes** toggles for installed accessories, with a second page reached using **Next**. Enable only equipment physically connected and configured. |
| **DHW circuit** | Later-manual enable toggle for the three-way valve and a temperature differential that decides when tank reheating is needed. |
| **Minimum pump temperature** | Later-manual threshold below which the heating-circuit pump stops; the series manual lists 0–60 °C and 30 °C default. Original 1.73 also has additional low-temperature pump-request logic in the analyzed firmware, so this one setting does not describe every pump condition. |
| **On/Off Operation** | Older-manual alternative to summer time scheduling. When **Yes**, the manual says the boiler stops at the configured **Set point** (60–80 °C, standard 70 °C) and restarts below 45 °C. **Max efficiency** caps output (20–100%, standard 60%). The manual says this mode cannot run alongside Summer operation. |
| **Manual ash cleaning** | Starts a selected 1–5 cleaning cycles in the later layout. This moves hardware. |
| **Model selection / Self-Testing boiler size** | Selects 900, 1500, 2500, or 4000. It is not a cosmetic label; model-specific fuel/fan settings differ. Confirm 1500 after a reset or software update. |
| **Auto-test / Test boiler** | Shows input/sensor readings and provides sequential manual relay/output activation. The series manual says it is available only with the boiler off and time programmer disabled. **Input test** is observational; **Relay test** can energize motors and other equipment. |
| **Restore / Reset default configuration** | Restores factory settings, which can clear custom values and require model selection and auger calibration again. This is separate from resetting a dose test or Info counters. |
| **New software / loading / Download** | Starts USB firmware loading after confirmation. It is not an ordinary setting save. See the [USB update guide](updating-firmware.md). |

The 2014 manual shows **Self-Testing → Next → Next → Next** for sensor pages and manual component controls; **Finish** stops the selected manual component and returns. The series manual calls these **Input test** and **Relay test** on [PDF page 36](ekoheat_series.pdf#page=36). No safe relay-test sequence can be inferred solely from the menu name.

## Shutdowns, alarms, and resets

The [series manual, PDF page 38](ekoheat_series.pdf#page=38) describes **E05: Burner error** and **E06: Flame defect** as controller cut-outs; **OK** acknowledges the displayed fault after the cause has been checked. It also describes a separate high-temperature safety thermostat: at 110 °C, power to the electronic control is cut, and its physical reset is used only after cooling below 90 °C. A screen **OK** cannot replace a physical safety reset.

Original-firmware analysis identifies **Startup failed!** when all ignition waits are exhausted or when flame is lost during the startup ramp. The 1.73 image additionally contains a low-fuel warning and changed pump and digital-input behavior; see the [version comparison](../analysis/v1.73/comparison.md). The electrical purpose of the analyzed digital input is still unknown, so this guide does not label it as a thermostat connection.

The [2014 manual, PDF pages 14–15](ekopower%20ekoheat%20installation%20manual%202%202014%20eng.pdf#page=14) also lists hot-shaft/burner-disconnected, ignition, ash-plate, and sensor-configuration alerts. They point to different physical causes; an acknowledgement button only clears the display after the underlying fault has been checked. Repeated faults, smoke, or a tripped safety cut-out call for a qualified technician rather than repeated restarts. The older manual describes a separate red thermal-reset button with a lower reset-temperature condition than the later series manual, so identify the actual safety device and matching controller manual before using a physical reset.

## Firmware updates and the idle clock

The [2014 manual, PDF page 16](ekopower%20ekoheat%20installation%20manual%202%202014%20eng.pdf#page=16) says to copy the firmware file first and its matching license second to an empty USB drive, select **Menu → Fitter settings → Next → New software → Download**, wait through a black screen and EKOPOWER logo countdown, then remove the USB. The later manual places **New software** under Service and reserves it for authorised personnel. Settings may reset and the selected model may become Ekoheat 900; check the model, calibration, and settings before normal operation.

The original firmware automatically changes to a clock screen after inactivity. The retained clock-only derivatives alter one idle-expiry instruction and retain the original version text. The [update story](firmware-story.md) records mixed hardware observations, including a later report that the clock seemed absent while Info still showed 1.73. That observation does not identify the exact image in flash or establish persistence. Check the same screen after more than the previously observed four-minute idle interval and after a normal restart with the USB removed.

## Where the manuals disagree

The manuals are not identical releases. Examples: boiler setpoint range 40–80 °C versus 65–80 °C, DHW range 0–70 °C versus 15–65 °C, minimum scheduled period 1 hour versus 1 hour 30 minutes, fan-cleaning time 10–30 versus 0–60 seconds, and pump threshold location/range/default. The [2014 manual](ekopower%20ekoheat%20installation%20manual%202%202014%20eng.pdf) and [series manual](ekoheat_series.pdf) both cover the product family but may describe different controller revisions. When a value differs, the installed controller and its matching service documentation take precedence over this combined guide.
