import time
import board
import busio
import displayio
import digitalio
from analogio import AnalogIn

SPI_SPEED = 48000000

# Pin definitions
TX_PIN = board.GP8
RX_PIN = board.GP9

class ESP_AT:
    def __init__(self, tx_pin, rx_pin, baudrate=115200):
        self.uart = busio.UART(tx_pin, rx_pin, baudrate=baudrate, receiver_buffer_size=1024)
        self.reset()
        self.send_command('ATE0')  # Turn off echo

    def send_command(self, cmd):
        at_cmd = 'AT+' + cmd + '\r\n'
        self.uart.write(at_cmd.encode())
        response = self.read_response()
        if "ERROR" in response:
            print(response)
        return response

    def read_response(self):
        response = b''
        timeout = time.monotonic() + 2
        while time.monotonic() < timeout:
            if self.uart.in_waiting > 0:
                response += self.uart.read(self.uart.in_waiting)
        return response.decode()

    def reset(self):
        self.send_command('RST')
        time.sleep(1)

    def wifi_off(self):
        self.send_command('CWQAP')  # Disconnect from any access point
        self.send_command('CWMODE=0')  # Set WiFi mode to off

def init():
    displayio.release_displays()
    spi = busio.SPI(clock=board.GP2, MOSI=board.GP3)
    while not spi.try_lock():
        pass
    spi.configure(baudrate=SPI_SPEED)
    spi.unlock()

    tft_cs    = board.GP5
    tft_dc    = board.GP1
    lcd_rst   = board.GP0
    lcd_light = board.GP4

    display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, baudrate=SPI_SPEED, reset=lcd_rst, polarity=0, phase=0)

    #esp = ESP_AT(TX_PIN, RX_PIN)
    #esp.wifi_off()

    return display_bus, lcd_light

def configure_led(enable_leds):
    led = digitalio.DigitalInOut(board.GP25)
    led.direction = digitalio.Direction.OUTPUT
    if enable_leds > 0:
       led.value = True
    else:
       led.value = False
    return led

def configure_battery_monitor():
    vbat_voltage_pin = AnalogIn(board.GP26)
    return vbat_voltage_pin

def configure_buttons():
    buttons = [board.GP6, board.GP7]
    return buttons
