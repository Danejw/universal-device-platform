# Personal Voice integration build plan

Status: **approved direction, implementation not started**. This document is the cross-repository work order for integrating the Universal Device Platform (UDP) reference watch with Personal Voice, first virtually and later via physical ESP32-S3 BLE.

Repositories:
- UDP: https://github.com/Danejw/universal-device-platform
- Personal Voice: https://github.com/Danejw/personal-voice

## End state

On the user's Android phone, an opt-in virtual watch can be enabled inside Personal Voice. It advertises a validated `udp/1` identity and only implemented capabilities. A simulated press triggers the **existing** Assistant flow, using the phone microphone and existing Gemini Live session and speaker output. A second press ends the session. The exact same normalized event handler will accept a physically connected watch after the BLE transport passes security and on-device tests.

No separate Android app, duplicate AI session, cloud service, new assistant tool, or hardware purchase is required for the first software milestone. Keep UDP reusable with other clients.

## Codebase findings (verified by reading both default branches, 2026-11-18)

- Personal Voice is a Tauri 2 / React TypeScript app with Kotlin Android platform code.
- `src/companion/CompanionView.tsx` invokes `assistant.setCompanionPressed(true/false)` and `assistantLibrary.produce()`. It uses hold-to-talk microphone gating.
- `src/assistant/AssistantController.ts` owns session and microphone lifetime. In Companion hold mode, audio is discarded while the press is not held.
- `src/app/App.tsx` already exposes the assistant toggle path through `overlayAssistantIntent`, `assistant.end()`, and `assistantLibrary.produce()`.
- `src/assistant/AssistantConversationStore.ts` claims/relinquishes an existing conversation lease when starting, so a device event must reuse this route.
- `src/platform/android/voicePlatformPlugin.ts` provides `callPlugin` and `listenPlugin` for the existing `VoicePlatformPlugin.kt` native bridge.
- Android manifest already includes `BLUETOOTH_SCAN` and `BLUETOOTH_CONNECT`; `NearbyDeviceDiscovery.kt` already performs user-triggered BLE scans and keeps raw addresses native/private.
- `src/devices/DevicesPanel.tsx` and `src/spatial/SpatialScanner.tsx` are existing device UI surfaces; `DeviceLinkManager` handles authenticated Android-to-Windows sessions and must not be repurposed as BLE.
- UDP currently has canonical `udp/1` messages, a localhost Python simulator, `android/VirtualWatchClient.kt`, `android/WatchBleClient.kt`, a short GATT v0 protocol, and ESP32-S3 reference firmware. The Python TCP simulator and Kotlin in-process virtual client are **different implementations** and do not connect automatically.
- Current physical firmware emits **press only**, as BLE byte `P`. It has no button-release event. Therefore V1 uses **tap to toggle** the standard Assistant, not Companion hold-to-talk. Hold-to-talk is a separate protocol extension when both edges are supported.

## Design decisions

1. **One normalized device input**: define a small TypeScript `WearableEvent` and `WearableSession` contract. Use `udp/1` capability names and normalized event names. The native BLE codec and in-process simulator both map to it.
2. **One assistant entry point**: a guarded application-level handler for `button.primary.pressed` calls the existing assistant start/end pathway, with sign-in, microphone-busy, assistant lease and current-status checks. Do not call `setCompanionPressed` for V1 taps.
3. **One simulated trigger**: implement the virtual watch in Personal Voice using the same TypeScript dispatch path as the future BLE adapter. A dedicated dev-only UI control emits the normalized event; it does not require localhost networking, Bluetooth, or a separate Python process. The Python simulator remains a reference for protocol tests.
4. **No fake capabilities**: active manifest is currently only `button.primary`. Camera, microphone, IMU, heart rate and battery reporting remain planned until drivers and tests exist.
5. **Visible provenance**: label source `simulated` or `physical` in debug state. Reject unrecognized protocol versions, undeclared capabilities, unknown commands, malformed events and duplicate/rapid notifications. No fake sensor values presented as measured data.
6. **Permissions**: native discovery remains user-triggered and its radio address remains native. Pairing and side-effect/media actions must have a stronger security gate than the current bench-only ESP32 reference.
7. **Scope**: Personal Voice retains its existing Gemini provider, conversation persistence, permission approvals, device pairing, Camera Context, audio handling and Windows DeviceLink. No new Gemini tools are needed for v1.

## Delivery phases and acceptance gates

### Phase 1: Contract and simulator parity (UDP repository)

Make `udp/1` fixtures (manifest, press, response, disconnect/error) and shared test vectors for Python and Kotlin/TypeScript consumers. Define stable fields for protocol version, device ID, capabilities, source, and event semantics; document what's transport metadata vs a wire field. Ensure simulated and BLE `P` both resolve to `button.primary.pressed`. Add unknown-version, wrong-capability, duplicate event, invalid schema and reconnection tests. Prefer a stable minimal API over introducing generators/frameworks.

**Gate:** Python tests, firmware configuration check and existing firmware CI pass; contract fixtures match both integrations. A successful host build is not physical BLE verification.

### Phase 2: Personal Voice virtual integration (Personal Voice repository)

Create `src/wearables/` (or another existing platform boundary if inspection shows a better fit) with:
- A small typed event parser/router and session state, independent of React and specific transports.
- A dev-only virtual-watch controller and UI entry in the existing Android device area. The control offers Connect, Tap button, Disconnect and shows active verified capabilities.
- A single handler wired in `src/app/App.tsx` or extracted from its existing overlay toggle callback. It consumes `button.primary.pressed` and invokes the same `assistantLibrary.produce()` / `assistant.end()` path already in use.
- Explicit UI status for sign-out, microphone busy, session connecting, active, error and disconnect. No autoplay or automatic first-time assistant start.

For the first test, a **tap** starts normal listening; another **tap** ends it. Companion's existing hold interaction remains unchanged. Avoid a second audio capture pipeline and a second ConversationStore lease.

**Gate:** Unit tests pass for toggle, denied sign-in, busy microphone, in-flight start, reconnect, duplicate events, after-unmount events, and teardown. User can interact with a virtual watch in an Android build without hardware.

### Phase 3: BLE watch adapter (Personal Voice repository)

Adapt and simplify the reference `android/WatchBleClient.kt` into Personal Voice's native package rather than copying a second app. Use existing `VoicePlatformPlugin.kt` commands/events and `voicePlatformPlugin.ts` bridge or a small child helper. Leverage current Nearby scanner's fresh opaque ID to initiate an explicit selected-device GATT connection, then validate service UUID, protocol manifest, capability set and CCCD notification subscription **before** marking it ready. Keep raw MAC addresses native. Handle Android permission denial, no Bluetooth, stale scan, missing characteristic, MTU failure, disconnect, reconnect, and teardown.

BLE bench firmware is currently unauthenticated. Limit test mode to non-sensitive events and a clearly labeled development setting until bonding and explicit application authorization are implemented and verified. Do not silently promote an arbitrary nearby radio to trusted device control.

**Gate:** Android Kotlin/Gradle build passes, native tests and TS interface contract tests pass. Actual RF connectivity remains pending a board and phone test.

### Phase 4: End-to-end verification and release readiness (both repositories)

- CI: UDP Python contract/config checks and ESP-IDF firmware build; Personal Voice `pnpm check`, `pnpm eval:tools` only if tool semantics change, and available Android build/test jobs. Review exact run IDs and failures.
- Automated integration: enable simulated watch, connect, tap, assert exactly one assistant start attempt and correct lease path; tap to end; reject duplicated/raced presses; reconnect no ghost notifications; simulated events never leak into production.
- Manual Android test: install a test build, sign in, grant phone microphone permission, enable development virtual watch, Connect, Tap, speak, receive an actual Gemini Live response through the phone, Tap to stop, Disconnect. Confirm no regression to Companion and existing device control.
- Record what was **observed** separately from mocked/unit-tested behavior. No claim that the live model or audio was verified unless it was performed on-device.
- Each phase should be independently reviewable with a commit/PR, test evidence, manual steps and rollback instructions. Do not merge red CI.

**Gate:** Live audio is confirmed by user on phone, and no extra device/software/service is required for the successful virtual-watch test.

### Phase 5: Physical bench validation (requires parts, later)

Purchase confirmed XIAO ESP32S3 Sense variant, USB-C data cable and normally-open button. Verify exact camera revision, pinout, shipping and battery requirements. Flash and test GPIO1 button, BLE UUID discovery, manifest read, encrypted/authorized session (after security work), event notification, and reconnect behavior. Only then enable microphone, camera, IMU, and optical sensor drivers one at a time, following `hardware/WIRING.md`, `hardware/BOM.md` and `docs/ROADMAP.md`. Batteries and wrist enclosure require separate electrical/thermal validation. No promise of guaranteed plug-and-play before bench tests.

## What the assistant can execute independently

- Implement and commit code to both GitHub repositories, with phase-scoped branches/PRs.
- Run and inspect connected GitHub Actions software and firmware compilation checks; correct code failures.
- Author and run mocked virtual-watch contracts, event-routing tests, permission/state tests, and build artifacts if supported by CI.
- Document exact user-facing Android test steps, failure evidence and release readiness.

## What requires the user or physical access

**For virtual-watch software demonstration:** No hardware purchase, soldering, ESP32 flashing, or GitHub setup. After an Android test build is available, the user must install or update the Personal Voice app on their own phone, sign in, allow microphone use, enable the development Virtual Watch, press Tap, speak a test request and check for audible response. App permissions and live audio behavior require actual user/device interaction. If CI can produce an installable APK, provide its exact workflow artifact link and installation guidance.

**For physical-watch validation later:** User needs to purchase/receive the exact listed parts and provide physical flashing/wiring/test feedback, or arrange a connected hardware test bench. The assistant cannot inspect or operate an unconnected physical watch through GitHub.

## Completion criteria

Phase 4 is complete only when (a) the virtual device uses the same normalized capability/event contract as the physical adapter, (b) Personal Voice starts and stops its existing AI assistant through a virtual watch event, (c) CI is green for changed software and Android, (d) the phone's real microphone and speaker response have been manually confirmed, (e) no physical data is implied by simulation, and (f) Personal Voice's existing Companion, dictation and DeviceLink behavior remains intact.

## Non-goals

No real camera/audio or biometrics streaming, battery integration, medical measurements, wrist enclosure, cross-platform desktop/watch support, agent-generated hardware pin reassignments, unattended AI actions, new assistant tool catalogs, new backend accounts, remote simulator socket exposure, or user-facing plug-in marketplace in this first integration.
