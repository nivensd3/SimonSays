# original code, added for loop in initialize gpio to detect rising voltage as start
import RPi.GPIO as GPIO
#import GPIOmock as GPIO
import threading
import time
import random
import os
from subprocess import call

# green, red, yellow, blue
LIGHTS = [33, 40, 36, 29]
BUTTONS = [11, 37, 15, 7]

# values you can change that affect game play
speed = 0.25
use_sounds = False

# flags used to signal game status
is_displaying_pattern = False
is_won_current_level = False
is_game_over = False

# game state
current_level = 1
current_step_of_level = 0
pattern = []



def initialize_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LIGHTS, GPIO.OUT, initial=GPIO.LOW) # set up LEDs as output pins
    GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # set up buttons as input pins with pull down resistors
    for i in range(4):
        GPIO.add_event_detect(BUTTONS[i], GPIO.RISING, verify_player_selection, 400 if use_sounds else 150)

def flash_led_for_button(button_channel):
    try:
        button_index = BUTTONS.index(button_channel)
        if 0 <= button_index < len(LIGHTS):
            led_pin = LIGHTS[button_index]
            GPIO.output(led_pin, GPIO.HIGH)  # Turn on the corresponding LED
            time.sleep(0.05)  # Keep the LED on for a short duration
            GPIO.output(led_pin, GPIO.LOW)  # Turn off the LED
        
        else:
            print("Button channel index out of range.")
    except ValueError:
        print("Button channel not found in BUTTONS list.")
    led = LIGHTS[BUTTONS.index(button_channel)]
    GPIO.output(led, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(led, GPIO.LOW)

def verify_player_selection(channel):
    global current_step_of_level, current_level, is_won_current_level, is_game_over
    if not is_displaying_pattern and not is_won_current_level and not is_game_over:
        flash_led_for_button(channel)
        if channel == BUTTONS[pattern[current_step_of_level]]:
            current_step_of_level += 1
            if current_step_of_level >= current_level:
                current_level += 1
                is_won_current_level = True
        else:
            is_game_over = True





def add_new_color_to_pattern():
    global is_won_current_level, current_step_of_level
    is_won_current_level = False
    current_step_of_level = 0
    next_color = random.randint(0, 3)
    pattern.append(next_color)
    print(f'Pattern: {pattern}') #0- green, 1-red, 2-yellow, 3-blue


def display_pattern_to_player():
    global is_displaying_pattern
    is_displaying_pattern = True
    GPIO.output(LIGHTS, GPIO.LOW)
    for i in range(current_level):
        GPIO.output(LIGHTS[pattern[i]], GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(LIGHTS[pattern[i]], GPIO.LOW)
        time.sleep(speed)
    is_displaying_pattern = False


def wait_for_player_to_repeat_pattern():
    while not is_won_current_level and not is_game_over:
        time.sleep(0.5)


def reset_board_for_new_game():
    global is_displaying_pattern, is_won_current_level, is_game_over
    global current_level, current_step_of_level, pattern
    is_displaying_pattern = False
    is_won_current_level = False
    is_game_over = False
    current_level = 1
    current_step_of_level = 0
    pattern = []
    GPIO.output(LIGHTS, GPIO.LOW)


def start_game():
    while True:
        add_new_color_to_pattern()
        display_pattern_to_player()
        wait_for_player_to_repeat_pattern()
        if is_game_over:
            print("Game Over! Your max score was {} colors!\n".format(current_level-1))
            play_again = input("Enter 'Y' to play again, or just press [ENTER] to exit.\n")
            if play_again == "Y" or play_again == "y":
                reset_board_for_new_game()
                print("Begin new round!\n")
            else:
                print("Thanks for playing!\n")
                break
        time.sleep(2)


def start_game_monitor():
    t = threading.Thread(target=start_game)
    t.daemon = True
    t.start()
    t.join()


def main():
    try:
        # call(["sonic_pi", "set_sched_ahead_time! 0"])
        # call(["sonic_pi", "use_debug false"])
        # call(["sonic_pi", "use_synth :pulse"])
        # call(["sonic_pi", "use_bpm 100"])
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Begin new round!\n")
        initialize_gpio()
        time.sleep(2) # 2 second start delay
        start_game_monitor()
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
