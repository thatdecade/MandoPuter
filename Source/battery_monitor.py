
import displayio
import adafruit_imageload
import configure_me as config
import sleep

battery_monitoring = None
button_pins = None

low_batt_icon = 0

def init(user_button_pins):
    global battery_monitoring
    global button_pins
    
    button_pins = user_button_pins
    
    if config.BATTERY_MON:
        battery_monitoring = config.board_setup.configure_battery_monitor()

def get_batt_percent(batt_pin):
    batt_volts = (batt_pin.value * 3.3) / 65536 * 2
    batt_volts += 0.05
    if batt_volts > 3.80:
        return 86
    elif batt_volts > 3.65:
        return 50
    elif batt_volts > 3.40:
        return 25
    else:
        return 5

def monitor(stage, display, user_request):
    global low_batt_icon
  
    if not battery_monitoring:
        return
      
    lowbattImg, lowbattPal = adafruit_imageload.load("LowBatt.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
    lowbattX = int(display.width - lowbattImg.width)
    lowbattY = int(display.height - lowbattImg.height)
    batt_tile = displayio.TileGrid(lowbattImg, pixel_shader=lowbattPal, x=lowbattX, y=lowbattY)

    batt_percent = get_batt_percent(battery_monitoring)
    #print(f"Battery percentage: {batt_percent}%")
    
    if batt_percent < config.LOW_BATT_SHUTDOWN_LEVEL:
        print("Entering deep sleep due to low battery")
        display_images.display_name(display, bitmap_font.load_font("Alef-Bold-12.bdf"), "Battery Low.\nShutting Down...", 5, 0xFF0000)
        user_request.stop_polling() #release the buttons
        sleep.deepsleep(button_pins)
    
    elif batt_percent < config.LOW_BATT_LEVEL:
        print(f"Low battery detected, low_batt_icon: {low_batt_icon}")
        if low_batt_icon == 0:
            stage.append(batt_tile)
            low_batt_icon = 1
            print("Low battery icon displayed")
    else:
        #print(f"Low battery not detected, low_batt_icon: {low_batt_icon}")
        if low_batt_icon > 0:
            stage.remove(batt_tile)
            low_batt_icon = 0
            print("Low battery icon removed")

    #print(f"Sleep timer: {sleep.check_sleep(button_pins)}")
