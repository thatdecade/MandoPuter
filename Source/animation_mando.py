import time
import asyncio
from adafruit_display_text import label
import displayio
import display_images
import random
from adafruit_display_shapes.line import Line
from adafruit_bitmap_font import bitmap_font
import configure_me as config
from user_requests import UserRequest
import battery_monitor

animation_keyword = "Characters"

async def animation(display, font, user_request, offset):

    stage  = displayio.Group()
    display.show(stage)

    mando_message = label.Label(font, text=config.messages[0], color=config.TEXT_COLOR)
    stage.append(mando_message)

    maxwidth = max(mando_message.bounding_box[2] for msg in config.messages)
    mando_message.x = int((display.width - maxwidth) / 2) - 1
    mando_message.y = int(display.height / 2) + offset

    # Setup selection indicator
    selection_indicator = label.Label(bitmap_font.load_font("Alef-Bold-12.bdf"), text=f"{user_request.get_animation_selected_name()}", color=0xFFFFFF)
    selection_indicator.x = 0
    selection_indicator.y = display.height - 10
    stage.append(selection_indicator)
    selection_indicator.hidden = False
        
    while animation_keyword in user_request.get_animation_selected_name():
      
        if config.BATTERY_MON:
            battery_monitor.monitor(stage, display, user_request)

        for index, msg in enumerate(config.messages):
            mando_message.text = msg
            
            # Non-Moving Text
            mando_message.x = int((display.width - maxwidth) / 2) - 1
            display.refresh()
            await asyncio.sleep(config.delays[index])

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

    # END LOOP

    while stage: #cleanup
        stage.pop()
