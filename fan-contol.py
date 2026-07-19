#! /usr/bin/python3

# Raspberry Pi PWM fan control V1.3 by Kevin Loughin, KB9RLW, July 2026
# Note: Ensure "dtoverlay=pwm" is enabled in your /boot/firmware/config.txt
# Also, install the periphery library with sudo apt install python3-periphery

# Initialize stuff
from periphery import PWM
from time import sleep

# Open PWM Chip 0, Channel 0 (This maps to physical GPIO 18)
pwm = PWM(0, 0)

# Set the total wave period for 100Hz (10,000,000 nanoseconds)
PERIOD = 20000000
pwm.period_ns = PERIOD
pwm.enable()

pwmvalue = 0

# Main loop
try:
    while True:
        # Read cpu temp, convert to 1 dec point.
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            raw_temp = int(f.read().strip())

            cpu_temp = round(raw_temp / 1000.0, 1)

        # 1. Below 46.9 -> Turn fan off (0 ns active time)
        if cpu_temp < 47.9:
            pwmvalue = 0
            pwm.duty_cycle_ns = 0

        # 2. In the target window -> Scale 20% to 100%
        elif 47.9 <= cpu_temp <= 51.1:
            # Check if fan was off to kickstart it
            if pwmvalue == 0:
                pwm.duty_cycle_ns = PERIOD  # 100% power
                sleep(0.2)

            # Calculate percent (20-100)
            percent = int(20 + (cpu_temp - 48) * 80 / 3)
            percent = max(20, min(100, percent)) # Clamp safety

            # Convert percentage to nanoseconds active time
            pwmvalue = int(PERIOD * (percent / 100.0))
            pwm.duty_cycle_ns = pwmvalue

        # 3. Above 51.1 -> Turn fan to max high
        else:
            pwmvalue = PERIOD
            pwm.duty_cycle_ns = pwmvalue


        # Wait 15 secs and check again.
        sleep(15)

finally:
    # Clean up hardware state safely
    pwm.duty_cycle_ns = 0
    pwm.close()

