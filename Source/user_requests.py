import digitalio
import board
import asyncio

class UserRequest:
    def __init__(self, button_pins):
        self.animation_select = ["No Scroll", "Scroll Speed 2", "Scroll Speed 10"]
        self.selected_animation_index = 0
        self.animation_counter = 0

        self.buttons = []
        for pin in button_pins:
            button = digitalio.DigitalInOut(pin)
            button.direction = digitalio.Direction.INPUT
            button.pull = digitalio.Pull.UP
            self.buttons.append(button)

        print(f"UserRequest initialized with animations: {self.animation_select}")
    
    def stop_polling(self):
      for button in self.buttons:
          button.deinit()
    
    def get_animation_selected_name(self):
        return self.animation_select[self.selected_animation_index]
    
    def get_scroll_speed_for_animation(self):
        speed = 0
        if self.selected_animation_index == 0:
            speed = 0
        elif self.selected_animation_index == 1:
            speed = 2
        elif self.selected_animation_index == 2:
            speed = 10
        return speed

    def update_animation_index(self, change):
        self.selected_animation_index = (self.selected_animation_index + change) % len(self.animation_select)
        self.animation_counter = 10
        print(f"update_animation_index: change={change}, selected_animation_index={self.selected_animation_index}, animation_counter={self.animation_counter}")
        return self.animation_select[self.selected_animation_index]

    def decrement_animation_counter(self):
        if self.animation_counter > 0:
            self.animation_counter -= 1
        return self.animation_counter

    def should_show_speed_indicator(self):
        show = self.animation_counter > 0
        return show

    def button_callback(self):
        if not self.buttons[1].value:  # Next animation button
            print("button_callback: Next animation button pressed")
            self.update_animation_index(1)
        if not self.buttons[0].value:  # Previous animation button
            print("button_callback: Previous animation button pressed")
            self.update_animation_index(-1)

    async def check_buttons(self):
        while True:
            self.button_callback()
            await asyncio.sleep(0.1)
