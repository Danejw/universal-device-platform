package com.universaldeviceplatform.android

/**
 * In-process stand-in for the ESP32 watch. Uses the same listener vocabulary
 * as WatchBleClient so a host app can exercise UI and agent actions without
 * granting Bluetooth permissions or purchasing hardware.
 *
 * Deliberately exposes only the button capability that firmware V0 implements.
 * This is a test double; it does not test BLE, sensor timing, power, or hardware.
 */
class VirtualWatchClient(private val listener: WatchBleClient.Listener) {
    private var connected = false

    fun connect() {
        if (connected) return
        connected = true
        listener.onConnected("watch-v0", listOf("button.primary"))
    }

    fun pressPrimaryButton() {
        if (connected) listener.onEvent("button.primary.pressed")
        else listener.onError("Virtual watch is disconnected")
    }

    fun ping() {
        if (connected) listener.onEvent("device.pong")
        else listener.onError("Virtual watch is disconnected")
    }

    fun close() {
        if (!connected) return
        connected = false
        listener.onDisconnected()
    }
}
