# configure_me.py

# -----------------------------------------------------------------------------
# Board Configuration
# -----------------------------------------------------------------------------

# Board setup imports (uncomment the one corresponding to your board)
import board_lilygo as board_setup            # LilyGo RP2040 w/ 1.14" LCD    https://amzn.to/4aBkma1
# import board_esp32_s3 as board_setup          # Adafruit ESP32-S3 Feather     https://www.adafruit.com/product/5477
# import board_feather_m4 as board_setup        # Adafruit Feather M4 Express   https://www.adafruit.com/product/3857
# import board_itsybitsy_m4 as board_setup      # Adafruit ItsyBitsy M4 Express https://www.adafruit.com/product/3800
# import board_itsybitsy_rp2040 as board_setup  # Adafruit ItsyBitsy RP2040     https://www.adafruit.com/product/4888
# import board_pipico_rp2040 as board_setup     # Raspberry Pi Pico RP2040      https://www.adafruit.com/product/4864

# -----------------------------------------------------------------------------
# Display Configuration
# -----------------------------------------------------------------------------

# Display type
DISPLAY = "1.14"  # Pre-Beskar   # Adafruit 1.14" LCD display  https://www.adafruit.com/product/4383
# DISPLAY = "1.30" #"Beskar"     # Adafruit 1.3" LCD display   https://www.adafruit.com/product/4313
# DISPLAY = "1.44"               # Adafruit 1.44" LCD display  https://www.adafruit.com/product/2088
# DISPLAY = "0.96"               # Adafruit 0.96" LCD display  https://www.adafruit.com/product/3533

# Setting screen resolution based on display type, do not change these
if DISPLAY == "1.30":
    RESOLUTION = 240
elif DISPLAY == "1.14":
    RESOLUTION = 135
elif DISPLAY == "1.44":
    RESOLUTION = 128
elif DISPLAY == "0.96":
    RESOLUTION = 80

# -----------------------------------------------------------------------------
# Preference Configuration
# -----------------------------------------------------------------------------

# Backlight brightness (0% to 100%)
DISP_BRIGHT = 80

# Owner name settings
SHOW_NAME = 0  # Set to 1 to display the name, or 0 to not display a name
OWNER_NAME = "Your Name Here"  # Name of the owner to be shown
NAME_COLOR = 0x00FF00  # Green on black (choose colors here - https://www.color-hex.com/)
NAME_HOLD = 3.0  # How many seconds to display the name

# Battery monitoring settings
BATTERY_SZ = 500  # Size of battery in mAh (only for the ESP32-S3 board)
BATTERY_MON = 1  # Set to 1 to enable the battery monitor, 0 to disable it
LOW_BATT_LEVEL = 15  # Show the low battery icon when the battery goes below this percentage
LOW_BATT_SHUTDOWN_LEVEL = 10  # Shutdown when battery goes below this percentage

# Other settings for debugging
ENABLE_LEDS = 1  # Set to 1 to turn on LEDs for debugging, set to 0 to save battery
DEBUG_SERIAL = 1  # If your board has a debug port, you can read the system messages.

SLEEP_TIMEOUT_SECONDS = 3600  # 3600 seconds = 1 hour

# -----------------------------------------------------------------------------
# Banner graphics settings
# -----------------------------------------------------------------------------

# Banner graphics settings
SHOW_IMG = 0  # How many images to show. 0 = no images, 1 = 1 image, 2 = 2 images

# File name of the first 8-bit BMP graphic to be shown after each text sequence
IMG1 = f"TheMandalorian{RESOLUTION}.bmp"
IMG1_HOLD = 5.00  # How long the first image is displayed in seconds

# File name of the second 8-bit BMP graphic to be shown after the first image
IMG2 = f"BabyYoda{RESOLUTION}.bmp"
IMG2_HOLD = 5.00  # How long the second image is displayed in seconds

# -----------------------------------------------------------------------------
# Mandalorian character sequence
# -----------------------------------------------------------------------------

# Mandalorian character sequence
messages = ["MLM", "JBM", "SAS", "JAS", "JBM", "MLM", "SAS", "AJS", "SAS"]
# Time that each character group is shown 0.50 is 500 milliseconds, or 1/2 of a second
delays = [0.75, 0.75, 0.65, 0.75, 0.50, 0.84, 1.00, 0.35, 0.84]
TEXT_COLOR = 0xFF0000  # Red on black (choose colors here - https://www.color-hex.com/)
