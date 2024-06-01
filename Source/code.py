import gc
import time
import displayio
import battery_monitor
import display_images
from adafruit_display_text import label
import adafruit_imageload
import sleep
import digitalio
import board
import asyncio
from adafruit_bitmap_font import bitmap_font
from user_requests import UserRequest
import configure_me as config
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.line import Line
import random
import animation_scrolling
import animation_mando
import animation_health
import animation_planet

# -----------------------------------------------------------------------------

def debug_print(text):
    if config.DEBUG_SERIAL:
        print(text)

debug_print(f"Starting MandoPuter in {config.DISPLAY} mode.")

# Setup
display_bus, lcd_light = config.board_setup.init()

debug_print("Display bus initialized")

# Initialize display
display, mando_font, offset = display_images.init(config.DISPLAY, display_bus, lcd_light)
debug_print("Display initialized")

led = config.board_setup.configure_led(config.ENABLE_LEDS)
debug_print("LED configured")

# Turn on the Backlight
display.brightness = config.DISP_BRIGHT / 100
debug_print("Backlight turned on")

# Show the owner's name at startup
if config.SHOW_NAME:
    display_images.display_name(display, mando_font, config.OWNER_NAME, config.NAME_HOLD, config.NAME_COLOR)
    debug_print(f"Displayed owner name: {config.OWNER_NAME}")

# Show the banner graphic(s)
if config.SHOW_IMG:
    debug_print(f"Display image: {config.IMG1}")
    display_images.display_image(display, config.IMG1, config.IMG1_HOLD)
    if config.SHOW_IMG > 1:
        debug_print(f"Display image: {config.IMG2}")
        display_images.display_image(display, config.IMG2, config.IMG2_HOLD)

button_pins = None
buttons = None
if hasattr(config.board_setup, 'configure_buttons'):
    button_pins = config.board_setup.configure_buttons()
    
    # Initialize sleep module
    sleep.init(button_pins, config.SLEEP_TIMEOUT_SECONDS)
    debug_print("Sleep timer started")

    battery_monitor.init(button_pins)
    debug_print("Battery monitor configured")

    # Setup buttons for user interaction
    user_request = UserRequest(button_pins)

else:
    debug_print("No button configuration found in board_setup.")

async def main():
    gc.collect()
    debug_print("Starting main loop")

    while True:
        animation_name = user_request.get_animation_selected_name()
        if "Scroll" in animation_name:
            debug_print("Starting the scrolling mando character animation.")
            await animation_scrolling.animation(display, mando_font, user_request, offset)
            
        elif "Characters" in animation_name:
            debug_print("Starting the static mando character animation.")
            await animation_mando.animation(display, mando_font, user_request, offset)
            
        elif "Heart" in animation_name:
            debug_print("Starting the health animation.")
            await animation_health.animation(display, user_request)
            
        elif "Planet" in animation_name:
            debug_print("Starting the planet animation.")
            await animation_planet.animation(display, user_request)
            
        else:
            debug_print("Unknown animation selected.")

async def run():
    await asyncio.gather(main(), user_request.check_buttons())

asyncio.run(run())
