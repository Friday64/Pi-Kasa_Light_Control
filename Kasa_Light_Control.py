import asyncio
from kasa import SmartPlug, SmartBulb, Discover
from tkinter import Tk, Button, colorchooser
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

# Function to change the color of a light
def change_light_color(light):
    # Open color picker dialog
    color_code, _ = colorchooser.askcolor(title="Choose a color")
    if color_code is None:
        return  # User cancelled

    # Convert RGB to HSV (Hue, Saturation, Value)
    # This is a placeholder conversion, the actual conversion may vary based on the bulb's specifications
    r, g, b = (int(c) for c in color_code)
    hue, saturation, value = rgb_to_hsv(r, g, b)

    # Apply color to the light
    asyncio.run(light.set_hsv(hue, saturation, value))
    reset_backlight_timer()

# Function to convert RGB to HSV (this function needs proper implementation)
def rgb_to_hsv(r, g, b):
    # Placeholder function, needs proper implementation
    return 0, 0, 0

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

# Function to safely shutdown the Raspberry Pi
def shutdown_pi():
    os.system("sudo shutdown now")

# Main function to create the UI and handle light controls
def main():
    # Discover Kasa smart bulbs
    lights = asyncio.run(discover_devices())

    # Check if we have at least one light, otherwise exit
    if not lights:
        print("No Kasa lights found. Please check your setup.")
        return

    # Creating the main window
    root = Tk()
    root.title("Kasa Light Control")

    # Creating buttons for each light
    for i, light in enumerate(lights):
        Button(root, text=f"Toggle Light {i+1}", command=lambda l=light: control_light(l)).pack()
        Button(root, text=f"Change Color {i+1}", command=lambda l=light: change_light_color(l)).pack()

    # Buttons to turn all lights on or off
    Button(root, text="Turn All On", command=lambda: control_all_lights(lights, True)).pack()
    Button(root, text="Turn All Off", command=lambda: control_all_lights(lights, False)).pack()

    # Shutdown button
    Button(root, text="Shutdown", command=shutdown_pi).pack()

    # Initialize backlight control
    reset_backlight_timer()

    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()

# Note: This code won't run correctly in the PCI due to missing hardware and GUI capabilities, but it's written to work on a Raspberry Pi setup.
# Also, the rgb_to_hsv function needs proper implementation based on the specific requirements of the Kasa bulb.

