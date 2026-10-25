"""
Software-only tests for interpreting sensor readings.
This can be run now, without the ESP32 or sensors:
    python test_sensor_logic.py

These are simple safety/logic checks, not FlyBrain tests.
"""

STOP_DISTANCE_CM = 12.0

def interpret_sensors(distance_cm, left_ir, right_ir):
    """
    left_ir/right_ir should already be normalized:
    True means obstacle detected; False means no obstacle.
    distance_cm should be a number in cm, or None if no valid reading.
    """
    if distance_cm is None or distance_cm < 0:
        return "S"  # fail safe if ultrasonic reading is invalid

    if distance_cm <= STOP_DISTANCE_CM:
        return "S"

    if left_ir and right_ir:
        return "S"  # both sides see obstacles; conservative default
    if left_ir:
        return "R"  # obstacle on left: turn right
    if right_ir:
        return "L"  # obstacle on right: turn left

    return "F"


def run_tests():
    cases = [
        ("clear path", 50, False, False, "F"),
        ("obstacle close ahead", 8, False, False, "S"),
        ("invalid distance", None, False, False, "S"),
        ("negative distance", -1, False, False, "S"),
        ("obstacle on left", 40, True, False, "R"),
        ("obstacle on right", 40, False, True, "L"),
        ("obstacles on both sides", 40, True, True, "S"),
        ("exact stop threshold", STOP_DISTANCE_CM, False, False, "S"),
    ]

    failed = 0
    for name, distance, left, right, expected in cases:
        actual = interpret_sensors(distance, left, right)
        result = "PASS" if actual == expected else "FAIL"
        print(f"{result}: {name}: expected {expected}, got {actual}")
        if actual != expected:
            failed += 1

    print(f"\n{len(cases) - failed}/{len(cases)} tests passed.")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run_tests()
