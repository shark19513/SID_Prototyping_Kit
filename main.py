import time
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
import threading
from pygame import mixer


receive_port    = 9008
ip_address      = "127.0.0.1"

#NOTE: These variables could perhaps go into a dictionary for each sound
osc_data            = 0
min_value           = -1
max_value            = 2
is_playing          = False
volume_link         = False
normalize_volume    = False
loop                = False


def handle_osc_data(address, *args):
    global osc_data
    osc_data = args[0]

def start_server():
    dispatcher = Dispatcher()
    dispatcher.map("/osc_data", handle_osc_data)
    server = osc_server.ThreadingOSCUDPServer((ip_address, receive_port), dispatcher)
    print(f"Server listening on {ip_address}:{receive_port}")
    server.serve_forever()


#TODO: Add ValueErrors
def set_min_value():
    global min_value
    print(  "\nENTER        - Set minimum play range value",
            "\nN + ENTER    - Don't set minimum play range value")
    user_input = input().lower()

    if user_input == "n":
        min_value = -1 # Set to a value outside the range [0 - 1]
        print("No start value set")
    else:
        min_value = osc_data
        print(f"Start value set to {osc_data}")


def set_max_value():
    global max_value
    print(  "\nENTER        - Set maximum play range value",
            "\nN + ENTER    - Don't set maximum play range value")
    user_input = input().lower()

    if user_input == "n":
        max_value = 2 # Set to a value outside the range [0-1]
        print("No stop value set")
    else:
        max_value = osc_data
        print(f"Stop value set to {osc_data}")


def set_volume_link():
    global volume_link
    global normalize_volume
    print( "\nLink OSC data input to volume? (Y/N) + ENTER")
    user_input = input().lower()

    if user_input == "y":
        volume_link = True
        print("OSC data input linked to volume")

        print("\nNormalize? (Y/N) + ENTER")
        user_input = input().lower()

        if user_input == "y":
            normalize_volume = True
            print("Normalization on")
        elif user_input == "n":
            normalize_volume = False
            print("Normalization off")

    elif user_input == "n":
        volume_link = False
        print("OSC data input not linked to volume")


def set_loop():
        global loop
        print("\nLoop? (Y/N) + ENTER")
        user_input = input().lower()

        if user_input == "y":
            loop = True
            print("Loop on")
        elif user_input == "n":
            loop = False
            print("Loop off")


# Run OSC server in background thread
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()


mixer.init()
sound = mixer.Sound("audio/vine_boom.mp3")
channel = None
sound.set_volume(1)


try:
    set_min_value()     # Ask user for minimum value of play range
    set_max_value()     # Ask user for maximum value of pay range
    set_volume_link()   # Ask user if they want to link the volume to the osc data input
    set_loop()          # Ask user if they want to loop

    while True:
        #TODO: no sound plays when min value is larger than max value

        in_range = min_value < osc_data < max_value

        # If inside range and not already playing, play as either loop or oneshot
        if in_range:
            if channel is None or not channel.get_busy():
                channel = sound.play(-1 if loop else 0)
        # If outside range, only stop the sound if it's looping
        elif loop:
                if channel is not None and channel.get_busy():
                    channel.stop()
                channel = None
        # If the sound is not looping it finishes on its own

        if volume_link and channel is not None and channel.get_busy():
            if normalize_volume:
                channel.set_volume((osc_data - min_value) / (max_value - min_value)) # Normalize to [0-1]

        time.sleep(0.001)

except KeyboardInterrupt:
    sound.stop()
    print("\nProgram terminated.")