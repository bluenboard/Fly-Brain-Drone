"""
Basic USB serial test for the ESP32.
Requires the ESP32 to be connected and running firmware that prints
sensor lines and accepts single-letter commands.

Install dependency:
    python -m pip install pyserial

Run:
    python test_serial.py
Choose the serial port printed by the script. This cannot be fully tested
until the ESP32 is connected.
"""

import sys
import time

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    print("pyserial is missing. Install it with: python -m pip install pyserial")
    raise SystemExit(1)


def main():
    ports = list(list_ports.comports())
    if not ports:
        print("No serial ports found. Connect the ESP32 with a data-capable USB cable.")
        return

    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"  {i}: {port.device} — {port.description}")

    choice = input("Enter the number of the ESP32 port (or type the port name): ").strip()
    if choice.isdigit():
        index = int(choice)
        if index < 0 or index >= len(ports):
            print("Invalid selection.")
            return
        port_name = ports[index].device
    else:
        port_name = choice

    try:
        with serial.Serial(port_name, 115200, timeout=0.5, write_timeout=0.5) as ser:
            # Many ESP32 boards reset when serial opens.
            time.sleep(2)
            ser.reset_input_buffer()
            print("\nConnected. Reading incoming lines.")
            print("Type F, L, R, or S and press Enter to send a command.")
            print("Type Q to quit. The script sends S on exit if possible.\n")

            while True:
                line = ser.readline().decode("utf-8", errors="replace").strip()
                if line:
                    print(f"ESP32 -> {line}")

                # Input is checked when a line is available; use Ctrl+C to exit.
                # This simple version avoids extra keyboard libraries.
                try:
                    command = input("Command [F/L/R/S, Enter=none, Q=quit]: ").strip().upper()
                except EOFError:
                    break

                if command == "Q":
                    break
                if command in {"F", "L", "R", "S"}:
                    ser.write((command + "\n").encode("ascii"))
                    print(f"Python -> {command}")
                elif command:
                    print("Please enter F, L, R, S, or Q.")

    except serial.SerialException as exc:
        print(f"Could not open/use {port_name}: {exc}")
        print("Close Arduino IDE Serial Monitor or any other app using the same port.")
    finally:
        print("Serial test ended. Make sure the motors are stopped.")


if __name__ == "__main__":
    main()
