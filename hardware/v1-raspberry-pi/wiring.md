# v1 wiring guide: Raspberry Pi + SEN55

Version 1 is the bench and first field rig: a Raspberry Pi driving the SEN55 directly and logging to CSV (`firmware/v1-raspberry-pi/main.py`). It exists to prove the sensor, the reading logic, and the thresholds before the standalone battery powered version. First data from the kitchen in Quebrantadero is in `docs/`.

The wiring is minimal because the Pi and the SEN55 happen to suit each other: the Pi header provides the 5 V the sensor needs, the SEN55's I2C lines are happy at the Pi's 3.3 V logic level, and the Pi has 1.8 kilohm pull ups on SDA and SCL onboard. Five wires, no other components.

## Connections

The SEN55 connector is a JST ZHR-06. Pin numbers below follow the Sensirion datasheet, pin 1 nearest the edge mark.

| SEN55 pin | Function | Raspberry Pi header pin | Pi function |
| --- | --- | --- | --- |
| 1 | VDD (5 V) | 2 | 5 V |
| 2 | GND | 6 | GND |
| 3 | SDA | 3 | GPIO2, SDA1 |
| 4 | SCL | 5 | GPIO3, SCL1 |
| 5 | SEL | 6 (shared) | GND, selects I2C mode |
| 6 | GND | 6 (shared) | GND |

SEL must be tied to ground or the sensor will not talk I2C. The Adafruit SEN5x breakout also works in place of the bare cable; on the Pi its 5 V boost simply goes unused because real 5 V is available.

## Software setup

1. Enable I2C: `sudo raspi-config`, Interface Options, I2C, enable, reboot.
2. Confirm the sensor is visible: `i2cdetect -y 1` should show `69`.
3. Install the driver: `pip install sensirion-i2c-sen5x`
4. Run the logger: `python3 main.py`. It appends to the CSV path set at the top of the file and prints each reading.

To log unattended (for example overnight in the kitchen), run it under systemd or from `cron @reboot` so it restarts if the Pi loses power. Worth adding before the rainy season tests.

## Reading the data

Columns: timestamp, PM1.0, PM2.5, PM4.0, PM10 (all in micrograms per cubic metre), relative humidity (percent), temperature (degrees Celsius), VOC index, NOx index.

Two warmup effects show up at the start of every run and are visible in the first field data:

1. The first PM readings after `start_measurement()` report zero while the fan spins up and the optical cell settles. Discard roughly the first 30 seconds.
2. The VOC and NOx indices need a conditioning period; NOx reports NaN for some time after startup and both take minutes to become meaningful. This is normal SEN5x behaviour, not a fault.

Note the logger writes as fast as the sensor flags data ready, roughly once a second, not the 5 second interval described for the alarm logic in the README. For bench characterisation the faster rate is useful; the v2 firmware samples more slowly to save power.

## What v1 does not do

No alarm output: no LED, no buzzer, no thresholds acted on. It measures and records. The alarm behaviour, battery power, and the clay vessel all belong to v2 (`hardware/v2-esp32/`).
