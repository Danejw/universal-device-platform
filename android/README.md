# Android and Personal Voice integration

The Android app remains independently owned by Personal Voice. This repository provides a native Kotlin **example adapter** to integrate via the Android BLE APIs; it does not write into the Personal Voice repository.

## Test on Android before hardware arrives

Add `VirtualWatchClient.kt` alongside `WatchBleClient.kt` in an Android project. Both use the same listener callbacks. Invoke `connect()`, `pressPrimaryButton()`, `ping()`, and `close()` from a development-only UI to exercise the Personal Voice input pipeline. Keep it behind a development flag so simulated events cannot be confused with real-device data. This adapter is also a Kotlin source example and has not been built as an independent Android application.

## Bring-up

1. Pairing/discovery is **not automatic until the Android app implements permissions and connection UX**. Require Bluetooth on and runtime `BLUETOOTH_SCAN`/`BLUETOOTH_CONNECT` permissions on Android 12+; handle legacy Android location permissions as needed.
2. Integrate `WatchBleClient.kt` in an Android app with minSdk 26, request Android 12+ runtime permissions in the host Activity, and add the matching permissions to its manifest.
3. Scan for the platform service UUID. Select the device deliberately, connect via GATT, and request MTU 185 before reading the manifest.
4. Read the BLE manifest. Subscribe to event CCCD. Normalize `P` into canonical `button.primary.pressed` and `!` into `device.pong`. Use the adapter's callback to forward the input to Personal Voice.
5. Exercise disconnect/reconnect, stale bonds, permission denial, background restrictions, and missing optional hardware.
6. For real phone tests, allow one device session at a time until the implementation is proven.

```xml
<uses-feature android:name="android.hardware.bluetooth_le" android:required="false" />
<uses-permission android:name="android.permission.BLUETOOTH_SCAN" />
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
<!-- If supporting Android 11 and below, review and add the appropriate legacy
     Bluetooth and location permissions and runtime permission flow. -->
```

This is an **integration source example**, not an independently compiled Android app or a production-ready pairing solution. The V0 ESP firmware is deliberately insecure and should only operate on a private lab bench with non-sensitive actions. Prioritize explicit pairing authorization and protection for future media and device control.
