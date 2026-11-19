# Watch V0 bench wiring

USB-C provides power to the XIAO board. **Do not connect a battery yet.** Disconnect power while moving wires.

| Signal | XIAO pin | Connected to | Status |
|---|---|---|---|
| Button signal | D0 / GPIO1 | One side of normally-open switch | V0 |
| Button return | GND | Other side of switch | V0 |
| I2C data | D4 / GPIO5 | IMU and/or optical module SDA | Optional |
| I2C clock | D5 / GPIO6 | IMU and/or optical module SCL | Optional |
| I2C power | 3V3 | Module VIN/Qwiic VCC | Optional, 3.3V |
| I2C ground | GND | Module ground | Optional |

The button uses internal GPIO pull-up and reads LOW when pressed, so **do not connect it to 5V**. The 3.3V and ground lines must be shared with optional sensor modules. The XIAO board has **no native Qwiic connector**; use a Qwiic-to-header cable or soldered wires, and verify wire order.

The Sense expansion board owns camera GPIO10–18, 38–40, 47–48 and PDM microphone GPIO41/42. SD occupies GPIO7/8/9/21 when enabled. Do not allocate those to general-purpose add-ons. Specific camera revision and board configuration still need bench validation.

Adafruit IMU default I2C address **0x6A** (optional **0x6B**), SparkFun SEN-15219 address **0x55**. There is no I2C address conflict between the two. Correct I2C addresses and wiring do **not** guarantee software compatibility: enable each validated driver in firmware before publishing its capability.

See [Seeed pin map](https://wiki.seeedstudio.com/xiao_esp32s3_pin_multiplexing/), [Adafruit guide](https://learn.adafruit.com/adafruit-lsm6ds3tr-c-6-dof-accel-gyro-imu/pinouts), and [SparkFun guide](https://learn.sparkfun.com/tutorials/sparkfun-pulse-oximeter-and-heart-rate-monitor-hookup-guide).