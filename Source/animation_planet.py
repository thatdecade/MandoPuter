import time
import asyncio
from adafruit_display_text import label
import displayio
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.arc import Arc
from adafruit_bitmap_font import bitmap_font
import adafruit_imageload
import configure_me as config
from user_requests import UserRequest
import battery_monitor
import math
import random

ANIMATION_KEYWORD = "Planet"

NUMBER_OF_LONGITUDE_LINES = 5
SIZE_OF_LONGITUDES = 1

PLANET_DATA = {
    "ARVALA-7": "ARVALA-7\n\nRemote\nDesert\nPlanet",
    "PLANET"  : "PLANET",
    "TREES"   : "TREES",
    "TARGET"  : "TARGET\n\nBounty\n10,000\nCredits",
    "GROGU"   : "GROGU"
}

async def animation(display, user_request):

    stage = displayio.Group()
    display.show(stage)

    planet_radius = min(display.width, display.height) // 3
    
    # Setup selection indicator
    selection_indicator = label.Label(bitmap_font.load_font("Alef-Bold-12.bdf"), text=f"{user_request.get_animation_selected_name()}", color=0xFFFFFF)
    selection_indicator.x = 0
    selection_indicator.y = display.height - 10
    stage.append(selection_indicator)
    selection_indicator.hidden = False
    
    # Setup text animations
    planet_info_label = label.Label(bitmap_font.load_font("mandalor24.bdf"), text=f"", color=0xFF0000)
    planet_info_label.x = display.width//2 + 10
    planet_info_label.y = 25
    planet_details_label = label.Label(bitmap_font.load_font("Aurebesh_english14.bdf"), text=f"", color=0xFFFFFF)
    planet_details_label.x = planet_info_label.x
    planet_details_label.y = planet_info_label.y + 25
    
    ###########################################
    # Draw the static background of the planet
    ###########################################
    planet_x = planet_radius + 10
    planet_y = planet_radius + 10

    # Draw the circle for the planet
    stage.append(Circle(planet_x, planet_y, planet_radius, outline=0xFFFFFF))

    loop_index = 0
    while ANIMATION_KEYWORD in user_request.get_animation_selected_name():
        while len(stage) > 2:  # Keep the circle portion intact
            stage.pop()
                     
        # Draw the Latitudes (East to West)
        red_lat = random.randint(1, 5)
        planet_info_label.text = list(PLANET_DATA.keys())[red_lat-1]
        planet_details_label.text = PLANET_DATA[planet_info_label.text]

        # Load and display the Baby Yoda image if the planet details text is "GROGU"
        yoda_tilegrid = None
        if planet_details_label.text == "GROGU":
            yoda_bitmap, yoda_palette = adafruit_imageload.load("BabyYoda60.bmp",
                                                                bitmap=displayio.Bitmap,
                                                                palette=displayio.Palette)
            yoda_tilegrid = displayio.TileGrid(yoda_bitmap, pixel_shader=yoda_palette,
                                               x=planet_x + planet_radius + 10, y=planet_y+10)
        
        red_y = 0
        for i in range(1, 6):
            y = planet_y - planet_radius + i * (2 * planet_radius // 6)
            x_offset = int((planet_radius ** 2 - (y - planet_y) ** 2) ** 0.5)
            color = 0xFFFFFF
            if i == red_lat:
              color = 0xFF0000  #color a random latitude red
              red_y = y
              red_x = planet_x + x_offset
            stage.append(Line(planet_x - x_offset, y, planet_x + x_offset, y, color=color))
            
        planet_info_label_line1 = Line(red_x, red_y, planet_info_label.x - 10, planet_info_label.y, color=0xFF0000)
        planet_info_label_line2 = Line(planet_info_label.x - 10, planet_info_label.y, planet_info_label.x - 5, planet_info_label.y, color=0xFF0000)

        # Precalc the Longitudes (North to South)
        spacing_of_longitudes_degrees = int(90/((NUMBER_OF_LONGITUDE_LINES+1)//2)) #Must be a multiple that will exactly add up to 90
        longitudes_angles = [round(-90 + spacing_of_longitudes_degrees * i, 1) for i in range(1, int((180 // spacing_of_longitudes_degrees)))]
        #print(longitudes_angles)
        ###########################################
        # Draw the animated portion of the planet
        ###########################################
        # Draw the Longitudes (North to South)
        for i in range(0, spacing_of_longitudes_degrees, SIZE_OF_LONGITUDES+1):
            while len(stage) > 7:  # Keep the static portion intact
                stage.pop()
                        
            stage.append(planet_info_label)
            stage.append(planet_info_label_line1)
            stage.append(planet_info_label_line2)
            stage.append(planet_details_label)
            if yoda_tilegrid:
                stage.append(yoda_tilegrid)
            
            # This here is some very clever code that animates an array of arcs to create the illusion of a rotating sphere.
            for angle in longitudes_angles:
                color = 0xFFFFFF
                if angle == longitudes_angles[loop_index]:
                  color = 0xFF0000  #color the first arc red
                  
                angle = angle + i #slowly move the arcs
            
                offset_x = abs(planet_radius * math.tan(math.radians(angle)))
                arc_radius = planet_radius / math.cos(math.radians(abs(angle)))
                arc_angle = (180 - abs(angle) * 2)
                if angle != 0:
                    offset_x   *= angle/abs(angle)
                    arc_radius *= angle/abs(angle)
                    arc_angle  *= angle/abs(angle)
                #print(f"x: {int(planet_x - offset_x)}, radius: {arc_radius}, angle={arc_angle}")
                arc = Arc( x=int(planet_x - offset_x), y=int(planet_y), radius=arc_radius, angle=arc_angle, direction=0, segments=50, outline=color, arc_width=SIZE_OF_LONGITUDES )
                stage.append(arc)

            await asyncio.sleep(0.005)

            if ANIMATION_KEYWORD not in user_request.get_animation_selected_name():
                break
            
            display.refresh()

        loop_index += 1
        if loop_index > len(longitudes_angles) - 1:
            loop_index = 0
        
        if config.BATTERY_MON:
            battery_monitor.monitor(stage, display, user_request)

        # Check for user requested changes
        if user_request.should_show_selection_indicator():
            selection_indicator.text = f"{user_request.get_animation_selected_name()}"
            selection_indicator.hidden = False
            user_request.decrement_animation_counter_fast()
        else:
            selection_indicator.hidden = True
        
        if ANIMATION_KEYWORD not in user_request.get_animation_selected_name():
            break
        
        await asyncio.sleep(0.05)

    # END LOOP

    while stage:  # Cleanup
        stage.pop()
