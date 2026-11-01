# Startup-failure triggers in the analyzed original firmware

Error code 4 (RAM `0x224C`) maps to `Startup failed!`. The error handler at `0x80010548` dispatches code 4 to `0x800106B6`, which uses the language string table at RAM `0xAC8`. Its English pointer resolves to `0x8000C8F0`, file offset `0x4909`.

## Trigger 1: ignition attempts exhausted

In task `0x80023754`, state 1/substate 2:

```c
if (light_reading > 17)
    change_subsystem_state(2);
if (ignition_attempt_elapsed >= configured_ignition_wait) {
    ignition_attempt_count++;
    if (ignition_attempt_count < 3)
        change_subsystem_state(1);
    else
        error_code = 4;
}
```

The counter is RAM `0x22B9`, reset to zero at initial ignition entry. The wait setting is the 16-bit value at RAM `0x4FFC`, loaded from configuration record offset `0x56`. Elapsed time is RAM `0x21F0`, incremented by the nominal one-second TimerTask at `0x8000B3F4`, and reset after fuel charging. Thus the initial attempt is followed by up to two repeats before this error. Repeated charging uses a quarter of the initial charge calculation (integer shift before the rest of the calculation).

The threshold applies to the processed light/lux value at RAM `0x504C`, not a raw ADC count. Processing is in `0x80025394`. The two `if` checks above are separate; detection at exactly the timeout boundary does not necessarily prevent the timeout branch from running during the same task pass.

## Trigger 2: light lost during startup ramp

Ignition routine `0x8000EAF8` waits for a processed light value greater than 17, then disables the ignition request and waits 240 nominal seconds. It subsequently ramps output toward its temperature/power exit conditions. During that ramp:

```c
if (light_reading < 18) {
    if (low_light_seconds > 14) {
        // Fan adjustment and 100 × 100 ms abort-aware wait.
    }
    if (low_light_seconds > 29) {
        previous_state = boiler_state;
        boiler_state = 5;
        error_code = 4;
        return false;
    }
} else {
    low_light_seconds = 0;
}
```

The low-light timer is RAM `0x2228`, incremented by TimerTask. It is reset on entry to the ramp and whenever the ramp loop sees light >=18. Once the timer exceeds 14, the routine can block for approximately ten seconds per pass before checking the >29 condition. Therefore the threshold is 30 nominal timer seconds, but reporting can occur later; this is not an exact 30-second wall-clock deadline.

The four-minute stabilization loop itself does not contain this low-light failure check. Other asynchronous errors can still abort it through `0x80010D18`.

## Evidence

- `ghidra/decompiled/80023754.txt`: ignition attempts, wait timeout, retry counter.
- `ghidra/decompiled/8000eaf8.txt`: light threshold, stabilization wait, ramp failure.
- `ghidra/decompiled/8000b3f4.txt`: one-second timer updates.
- `ghidra/decompiled/80011168.txt`: configuration mapping.
- `ghidra/decompiled/80025394.txt`: processed light value.
- `ghidra/decompiled/80010548.txt`: fault handler (some vararg message arguments are lost in decompilation; string mapping checked against machine code and pointer data).

These are static-analysis findings for SHA-256 `b5ab1b7380f2486c29cf6708954cdb5bbaa2d7798fd0103f845fa254da51a5e8`. The corresponding v1.73 ignition/retry behavior was subsequently compared; see the [version comparison](v1.73/comparison.md#important-rules-that-remain).
