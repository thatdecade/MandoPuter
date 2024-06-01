import time
import asyncio
from adafruit_display_text import label
import displayio
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.arc import Arc
from adafruit_bitmap_font import bitmap_font
import configure_me as config
from user_requests import UserRequest
import battery_monitor
import math

ANIMATION_KEYWORD = "Planet"

NUMBER_OF_LONGITUDE_LINES = 5
SIZE_OF_LONGITUDES = 1


async def animation(display, user_request):

    stage = displayio.Group()
    display.show(stage)

    # Setup selection indicator
    selection_indicator = label.Label(bitmap_font.load_font("Alef-Bold-12.bdf"), text=f"{user_request.get_animation_selected_name()}", color=0xFFFFFF)
    selection_indicator.x = 0
    selection_indicator.y = display.height - 10
    stage.append(selection_indicator)
    selection_indicator.hidden = False
    
    ###########################################
    # Draw the static background of the planet
    ###########################################
    planet_radius = min(display.width, display.height) // 4
    planet_x = planet_radius + 10
    planet_y = planet_radius + 10

    # Draw the circle for the planet
    stage.append(Circle(planet_x, planet_y, planet_radius, outline=0xFFFFFF))

    # Draw the Latitudes (East to West)
    for i in range(1, 6):
        y = planet_y - planet_radius + i * (2 * planet_radius // 6)
        x_offset = int((planet_radius ** 2 - (y - planet_y) ** 2) ** 0.5)
        stage.append(Line(planet_x - x_offset, y, planet_x + x_offset, y, color=0xFFFFFF))

    # Precalc the Longitudes (North to South)
    spacing_of_longitudes_degrees = int(90/((NUMBER_OF_LONGITUDE_LINES+1)//2)) #Must be a multiple that will exactly add up to 90
    longitudes_angles = [round(-90 + spacing_of_longitudes_degrees * i, 1) for i in range(1, int((180 // spacing_of_longitudes_degrees)))]

    ###########################################
    # Draw the animated portion of the planet
    ###########################################
    while ANIMATION_KEYWORD in user_request.get_animation_selected_name():
        
        # Draw the Longitudes (North to South)
        for i in range(-spacing_of_longitudes_degrees, spacing_of_longitudes_degrees, SIZE_OF_LONGITUDES+1):
            
            while len(stage) > 7:  # Keep the static portion intact
                stage.pop()

            # This here is some very clever code that animates an array of arcs to create the illusion of a rotating sphere.
            for angle in longitudes_angles:
                angle = angle + i #slowly move the arcs
                if angle == 0:
                    continue
                offset_x = abs(planet_radius * math.tan(math.radians(angle))) * angle/abs(angle)
                arc_radius = planet_radius / math.cos(math.radians(abs(angle))) * angle/abs(angle)
                arc_angle = (180 - abs(angle) * 2) * angle/abs(angle)
                #print(f"x: {int(planet_x - offset_x)}, radius: {arc_radius}, angle={arc_angle}")
                arc = Arc( x=int(planet_x - offset_x), y=int(planet_y), radius=arc_radius, angle=arc_angle, direction=0, segments=50, outline=0xFFFFFF, arc_width=SIZE_OF_LONGITUDES )
                stage.append(arc)

            await asyncio.sleep(0.005)

            if ANIMATION_KEYWORD not in user_request.get_animation_selected_name():
                break
            
            display.refresh()

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
