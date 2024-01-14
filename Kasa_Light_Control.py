import asyncio
from kasa import SmartPlug, SmartBulb, Discover
from tkinter import Tk, Button
import threading
import os

# Function to discover Kasa devices on the network
async def discover_devices():
    devices = await Discover.discover()
    return [dev for dev in devices.values() if isinstance(dev, SmartBulb)]

# Function to toggle a device
async def toggle_device(device):
    await device.update()  # Update the device's state
    await device.turn_on() if not device.is_on else await device.turn_off()

# Function to control a specific light
def control_light(light):
    asyncio.run(toggle_device(light))
    reset_backlight_timer()

# Function to control all lights
def control_all_lights(lights, state):
    for light in lights:
        asyncio.run(light.turn_on() if state else light.turn_off())
    reset_backlight_timer()

# Function to turn on the backlight
def turn_on_backlight():
    os.system("echo 0 | sudo tee /sys/class/backlight/rpi_backlight/bl_power")

# Function to turn off the backlight
def turn_off_backlight():
    os.system("echo 1 | sudo tee /sys/class/backlight/rpi_backlight/bl_power")

# Backlight control timer
backlight_timer = None

# Function to reset the backlight timer
def reset_backlight_timer():
    global backlight_timer
    if backlight_timer is not None:
        backlight_timer.cancel()
    turn_on_backlight()
    backlight_timer = threading.Timer(30.0, turn_off_backlight)
    backlight_timer.start()

# Main function to create the UI and handle light controls
def main():
    # Discover Kasa smart bulbs
    lights = asyncio.run(discover_devices())

    # Check if we have four lights, otherwise exit
    if len(lights) != 4:
        print("Four Kasa lights not found. Please check your setup.")
        return

    # Creating the main window
    root = Tk()
    root.title("Kasa Light Control")

    # Creating buttons for each light
    for i, light in enumerate(lights):
        Button(root, text=f"Toggle Light {i+1}", command=lambda l=light: control_light(l)).pack()

    # Buttons to turn all lights on or off
    Button(root, text="Turn All On", command=lambda: control_all_lights(lights, True)).pack()
    Button(root, text="Turn All Off", command=lambda: control_all_lights(lights, False)).pack()

    # Initialize backlight control
    reset_backlight_timer()

    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()
