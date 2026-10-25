
"""
flybrain_robot.py

Experimental mapping:
  Ultrasonic distance -> overall stimulus strength
  Left/right IR       -> asymmetric LC10a stimulation
  DNa02 L/R activity  -> candidate steering signal

This is a prototype. The neural-to-steering mapping must be
validated; a conservative rule-based fallback is included.
"""

import time
import serial
import numpy as np
from flybrain import FlyBrain

SERIAL_PORT = "COM3"       # Change this for your computer
BAUD_RATE = 115200

STOP_DISTANCE_CM = 12.0
RELEVANT_DISTANCE_CM = 45.0
FAR_DISTANCE_CM = 60.0
STEPS_PER_DECISION = 5     # 5 x 20 ms = about 100 ms
STEERING_THRESHOLD = 2     # Require a noticeable activity difference

# Load the simulated fly brain
print("Loading FlyBrain...")
brain = FlyBrain(device="auto")

# Experimental sensory input populations
lc10a_left = brain.cells(["LC10a"], side="L")
lc10a_right = brain.cells(["LC10a"], side="R")

# Candidate output populations to monitor
dNa02_left = brain.cells(["DNa02"], side="L")
dNa02_right = brain.cells(["DNa02"], side="R")

print("LC10a cells:", len(lc10a_left), len(lc10a_right))
print("DNa02 cells:", len(dNa02_left), len(dNa02_right))


def clip01(value):
    return max(0.0, min(1.0, float(value)))


def distance_to_strength(distance_cm):
    """Closer obstacle -> stronger normalized stimulus."""
    if distance_cm < 0:
        return 0.0

    return clip01(
        (FAR_DISTANCE_CM - distance_cm)
        / (FAR_DISTANCE_CM - STOP_DISTANCE_CM)
    )


def run_neural_window(distance_cm, left_ir, right_ir):
    """
    Stimulate LC10a populations for several simulation steps.
    Return total DNa02 spikes observed in that window.
    """
    distance_strength = distance_to_strength(distance_cm)

    # Ultrasonic distance creates a symmetric urgency signal.
    # IR detection adds a stronger side-specific input.
    left_strength = 0.25 * distance_strength
    right_strength = 0.25 * distance_strength

    if left_ir:
        left_strength = max(left_strength, 0.8)

    if right_ir:
        right_strength = max(right_strength, 0.8)

    left_spikes = 0
    right_spikes = 0

    for _ in range(STEPS_PER_DECISION):
        # The exact sensory mapping is an experiment, not a
        # biologically validated conversion of IR/ultrasonic data.
        inject = [
            (lc10a_left, left_strength),
            (lc10a_right, right_strength),
        ]

        fired = brain.step(inject=inject)

        left_spikes += int(np.isin(fired, dNa02_left).sum())
        right_spikes += int(np.isin(fired, dNa02_right).sum())

    return left_spikes, right_spikes


def choose_command(distance_cm, left_ir, right_ir,
                   left_spikes, right_spikes):
    """
    Choose a command. Local safety rules take priority over
    the neural output.
    """
    if distance_cm < 0 or distance_cm <= STOP_DISTANCE_CM:
        return "S"

    obstacle_near = distance_cm < RELEVANT_DISTANCE_CM
    obstacle_detected = bool(left_ir or right_ir)

    if not obstacle_near and not obstacle_detected:
        return "F"

    difference = left_spikes - right_spikes

    # Initial hypothesis: greater left DNa02 activity -> turn left;
    # greater right activity -> turn right.
    # Bench-test this and reverse the mapping if the observed
    # behavior is opposite or inconsistent.
    if difference >= STEERING_THRESHOLD:
        return "L"

    if difference <= -STEERING_THRESHOLD:
        return "R"

    # Conventional fallback if neural output is inconclusive.
    if left_ir and not right_ir:
        return "R"  # obstacle on left -> turn away
    if right_ir and not left_ir:
        return "L"  # obstacle on right -> turn away
    if left_ir and right_ir:
        return "S"

    # Ultrasonic sensor alone doesn't reveal which side is clear.
    return "S"


def main():
    print("Opening ESP32 serial connection...")
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        time.sleep(2)  # ESP32 may reset when serial opens
        ser.reset_input_buffer()

        print("Running. Press Ctrl+C to stop.")

        try:
            while True:
                line = ser.readline().decode(
                    "utf-8", errors="ignore"
                ).strip()

                if not line:
                    continue

                parts = line.split(",")

                # Expected: S,distance_cm,left_ir,right_ir
                if len(parts) != 4 or parts[0] != "S":
                    continue

                try:
                    distance_cm = float(parts[1])
                    left_ir = int(parts[2]) == 1
                    right_ir = int(parts[3]) == 1
                except ValueError:
                    continue

                # Stop for invalid ultrasonic readings.
                if distance_cm < 0:
                    ser.write(b"S\n")
                    print("Invalid distance -> STOP")
                    continue

                left_spikes, right_spikes = run_neural_window(
                    distance_cm, left_ir, right_ir
                )

                command = choose_command(
                    distance_cm,
                    left_ir,
                    right_ir,
                    left_spikes,
                    right_spikes,
                )

                ser.write((command + "\n").encode("ascii"))

                print(
                    f"distance={distance_cm:5.1f} cm | "
                    f"IR L/R={int(left_ir)}/{int(right_ir)} | "
                    f"DNa02 L/R={left_spikes}/{right_spikes} | "
                    f"command={command}"
                )

        except KeyboardInterrupt:
            ser.write(b"S\n")
            print("\nStopping robot.")

        finally:
            ser.write(b"S\n")


if __name__ == "__main__":
    main()
