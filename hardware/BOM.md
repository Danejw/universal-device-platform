# Reference parts and procurement

**Reference design:** USB-powered prototype, not a sealed wearable. Values are manufacturer listed USD item prices checked November 18, 2026, excluding tax and Hawaii shipping; they are **not confirmed delivered quotes**. See machine-readable [parts.json](parts.json).

| Component | Source/SKU | Prototype use | Listed price |
|---|---|---|---:|
| [Seeed XIAO ESP32S3 Sense](https://www.seeedstudio.com/XIAO-ESP32S3-Sense-p-5639.html) | Seeed 113991115 | Required controller + included camera + digital mic | $18.90 |
| Generic normally-open button | Electrical parts supplier, footprint TBD | Required D0 input | TBD |
| USB-C data cable | Generic | Required programming + power | TBD |
| [Adafruit LSM6DS3TR-C](https://www.adafruit.com/product/4503) | Adafruit 4503 | Optional 6-axis motion | $9.95 |
| [SparkFun optical sensor](https://www.sparkfun.com/sparkfun-pulse-oximeter-and-heart-rate-sensor-max30101-max32664-qwiic.html) | SparkFun SEN-15219 | Optional experimental heart-rate | $48.95 |
| 4-pin Qwiic cable + jumper adapter | Generic | Optional I2C sensor wiring | TBD |

Core documented board price: **$18.90**, plus button/cable/taxes/shipping. All listed optional electronics: **$77.80**, plus unpriced parts/taxes/shipping. Optical sensor not needed to prove the architecture.

The included camera model varies with shipping batch: OV2640, OV3660, or currently OV5640 fixed-focus. Validate actual delivered model and driver ID first. XIAO Sense's camera/mic daughterboard is included; do not order a second camera or mic for this V0.

### Purchasing gates

1. Confirm the exact SKU and whether the seller ships to Hawaii, including tax/delivery.
2. Confirm delivered camera module; record photo/revision and run the factory camera test.
3. Test the button and BLE firmware on USB **before** adding a LiPo battery.
4. A wearable battery is **not yet selected**. Capacity, protection circuit, lead polarity, charger current, heat and enclosure tolerances require an electrical review.
5. Validate skin-contact materials, sensor position, waterproofing, thermal behavior, and optical accuracy separately. No medical-use claims.

### Primary manufacturer references

- [Seeed board wiki and revisions](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)
- [Seeed pin multiplexing](https://wiki.seeedstudio.com/xiao_esp32s3_pin_multiplexing/)
- [Adafruit IMU guide](https://learn.adafruit.com/adafruit-lsm6ds3tr-c-6-dof-accel-gyro-imu)
- [SparkFun optical sensor hookup guide](https://learn.sparkfun.com/tutorials/sparkfun-pulse-oximeter-and-heart-rate-monitor-hookup-guide)
