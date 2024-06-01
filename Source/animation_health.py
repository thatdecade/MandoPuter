import asyncio
from adafruit_display_shapes.line import Line
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import displayio
import random
import configure_me as config
from user_requests import UserRequest
import battery_monitor

animation_keyword = "Heart"

async def animation(display, user_request):
  
    stage = displayio.Group()
    display.show(stage)
    print("stage created")

    # Dimensions of the box
    box_width = display.width // 2
    box_height = display.height // 2

    # Draw the outer lines of the box
    stage.append(Line(0, 0, box_width, 0, color=0xFFFFFF))  # Top
    stage.append(Line(0, 0, 0, box_height, color=0xFFFFFF))  # Left
    stage.append(Line(box_width, 0, box_width, box_height, color=0xFFFFFF))  # Right
    stage.append(Line(0, box_height, box_width, box_height, color=0xFFFFFF))  # Bottom

    # Heart monitor animation loop with a single pixel inside the box
    random_point = (box_width // 2) + random.randint(-50, 50)
    y_position = box_height // 2
    
    # Setup selection indicator
    selection_indicator = label.Label(bitmap_font.load_font("Alef-Bold-12.bdf"), text=f"{user_request.get_animation_selected_name()}", color=0xFFFFFF)
    selection_indicator.x = 0
    selection_indicator.y = display.height - 10
    stage.append(selection_indicator)
    selection_indicator.hidden = False

    while animation_keyword in user_request.get_animation_selected_name():

        if config.BATTERY_MON:
            battery_monitor.monitor(stage, display, user_request)

        for x in range(box_width - 1):
            # Draw the moving red line
            if x < random_point:
                if x > 20:  # Before random point
                    x1 = x
                    x2 = x - 20  # full length tail
                else:  # Off screen left
                    x1 = x
                    x2 = 0  # clamp
            elif x + 20 > box_width:  # Off screen right
                x1 = box_width  # clamp
                x2 = x
            else:
                if x > random_point + 20:  # After random point
                    x1 = x - 20  # full length tail
                    x2 = x
                else:  # "Off screen" random point
                    x1 = random_point  # clamp
                    x2 = x

            stage.append(Line(x2, y_position, x1, y_position, color=0xFF0000))
            display.refresh()
            await asyncio.sleep(0.001)

            # Draw peak line segments at random_point
            if x == random_point:
                stage.pop()
                stage.append(Line(x, y_position, x + 5, y_position - 20, color=0xFF0000))
                stage.append(Line(x + 5, y_position - 20, x + 10, y_position, color=0xFF0000))

                # Animate the shortening red line
                for x2 in range(20):
                    stage.append(Line(x - 20 + x2, y_position, x, y_position, color=0xFF0000))
                    display.refresh()
                    stage.pop()
                    await asyncio.sleep(0.001)

                x += 10  # Skip ahead to continue the flat line

            while len(stage) > 5:  # Keep the box intact
                stage.pop()

            if animation_keyword not in user_request.get_animation_selected_name():
                break
        
        # Check for user requested changes
        if user_request.should_show_selection_indicator():
            selection_indicator.text = f"{user_request.get_animation_selected_name()}"
            selection_indicator.hidden = False
            user_request.decrement_animation_counter_fast()
        else:
            selection_indicator.hidden = True
    
        display.refresh()

        await asyncio.sleep(config.delays[0])
        
    # END LOOP

    #while stage: #cleanup
    #    stage.pop()
