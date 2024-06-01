import digitalio
import board
import asyncio

class UserRequest:
    def __init__(self, button_pins):
        self.animation_select = ["Mando Characters", "Scroll Speed 2", "Scroll Speed 10", "Heart Monitor", "Planet"]
        self.selected_animation_index = 4 #TBD 3
        self.animation_counter = 10

        self.buttons = []
        self.button_states = []
        for pin in button_pins:
            button = digitalio.DigitalInOut(pin)
            button.direction = digitalio.Direction.INPUT
            button.pull = digitalio.Pull.UP
            self.buttons.append(button)
            self.button_states.append(button.value)

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
            if self.animation_counter < 0:
                self.animation_counter = 0
        return self.animation_counter

    def decrement_animation_counter_fast(self):
        if self.animation_counter > 0:
            self.animation_counter -= 2
            if self.animation_counter < 0:
                self.animation_counter = 0
        return self.animation_counter

    def should_show_selection_indicator(self):
        return self.animation_counter > 0

    def button_callback(self):
        for i, button in enumerate(self.buttons):
            current_state = button.value
            if current_state != self.button_states[i]:
                if not current_state:  # Button press detected
                    if i == 1:  # Next animation button
                        print("button_callback: Next animation button pressed")
                        self.update_animation_index(1)
                    elif i == 0:  # Previous animation button
                        print("button_callback: Previous animation button pressed")
                        self.update_animation_index(-1)
            self.button_states[i] = current_state

    async def check_buttons(self):
        while True:
            self.button_callback()
            await asyncio.sleep(0.1)
