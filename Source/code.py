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

# -----------------------------------------------------------------------------

def debug_print(text):
    if config.DEBUG_SERIAL:
        print(text)

debug_print(f"Starting MandoPuter in {config.DISPLAY} mode.")

# Setup
display_bus, lcd_light = config.board_setup.init()

debug_print("Display bus initialized")

# Initialize display
display, font, offset = display_images.init(config.DISPLAY, display_bus, lcd_light)
debug_print("Display initialized")

led = config.board_setup.configure_led(config.ENABLE_LEDS)
debug_print("LED configured")

if config.BATTERY_MON:
    battery_monitoring = config.board_setup.configure_battery_monitor()
    debug_print("Battery monitor configured")

# Turn on the Backlight
display.brightness = config.DISP_BRIGHT / 100
debug_print("Backlight turned on")

# Show the owner's name at startup
if config.SHOW_NAME:
    display_images.display_name(display, font, config.OWNER_NAME, config.NAME_HOLD, config.NAME_COLOR)
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

    # Setup buttons for user interaction
    user_request = UserRequest(button_pins)

else:
    debug_print("No button configuration found in board_setup.")

async def battery_monitoring_routine(stage, display, battery_monitoring, user_request):
    lowbattImg, lowbattPal = adafruit_imageload.load("LowBatt.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
    lowbattX = int(display.width - lowbattImg.width)
    lowbattY = int(display.height - lowbattImg.height)
    batt_tile = displayio.TileGrid(lowbattImg, pixel_shader=lowbattPal, x=lowbattX, y=lowbattY)

    low_batt_icon = 0

    while True:
        batt_percent = battery_monitor.get_batt_percent(battery_monitoring)
        debug_print(f"Battery percentage: {batt_percent}%")
        
        if batt_percent < config.LOW_BATT_SHUTDOWN_LEVEL:
            debug_print("Entering deep sleep due to low battery")
            display_images.display_name(display, bitmap_font.load_font("Alef-Bold-12.bdf"), "Battery Low.\nShutting Down...", 5, 0xFF0000)
            user_request.stop_polling()
            sleep.deepsleep(button_pins)
        
        elif batt_percent < config.LOW_BATT_LEVEL:
            if low_batt_icon == 0:
                stage.append(batt_tile)
                low_batt_icon = 1
                debug_print("Low battery icon displayed")
        else:
            if low_batt_icon > 0:
                stage.pop()
                low_batt_icon = 0
                debug_print("Low battery icon removed")

        debug_print(f"Sleep timer: {sleep.check_sleep(button_pins)}")
        await asyncio.sleep(1)

async def main():
    gc.collect()
    debug_print("Starting main loop")

    stage = displayio.Group()
    display.show(stage)
    mando_message = label.Label(font, text=config.messages[0], color=config.TEXT_COLOR)
    stage.append(mando_message)

    maxwidth = max(mando_message.bounding_box[2] for msg in config.messages)
    mando_message.x = int((display.width - maxwidth) / 2) - 1
    mando_message.y = int(display.height / 2) + offset

    # Setup speed indicator
    speed_indicator = label.Label(bitmap_font.load_font("Alef-Bold-12.bdf"), text=f"{user_request.get_animation_selected_name()}", color=0xFFFFFF)
    speed_indicator.x = 0
    speed_indicator.y = display.height - 10
    stage.append(speed_indicator)
    speed_indicator.hidden = True

    if config.BATTERY_MON:
        asyncio.create_task(battery_monitoring_routine(stage, display, battery_monitoring, user_request))

    while True:
        for index, msg in enumerate(config.messages):
            mando_message.text = msg
            if user_request.get_scroll_speed_for_animation() > 0:
                mando_message.x = display.width  # Reset the text position to the start for each message
                while mando_message.x + mando_message.bounding_box[2] > 0:
                    if user_request.get_scroll_speed_for_animation() > 0:
                        mando_message.x -= user_request.get_scroll_speed_for_animation()  # Move text to the left
                        display.refresh()
                        await asyncio.sleep(0.01)
                    else:
                        # If scroll speed is 0, break the inner while loop
                        break
                    
                    # Check for user requested changes
                    if user_request.should_show_speed_indicator():
                        speed_indicator.text = f"{user_request.get_animation_selected_name()}"
                        speed_indicator.hidden = False
                        user_request.decrement_animation_counter()
                    else:
                        speed_indicator.hidden = True
            else:
                # Non-Moving Text
                mando_message.x = int((display.width - maxwidth) / 2) - 1
                display.refresh()
                await asyncio.sleep(config.delays[index])
                
                # Check for user requested changes
                if user_request.should_show_speed_indicator():
                    speed_indicator.text = f"{user_request.get_animation_selected_name()}"
                    speed_indicator.hidden = False
                    user_request.decrement_animation_counter()
                else:
                    speed_indicator.hidden = True

            display.refresh()

async def run():
    await asyncio.gather(main(), user_request.check_buttons())

asyncio.run(run())
