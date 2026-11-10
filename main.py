import time
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
import threading
from pygame import mixer


receive_port    = 9008
ip_address      = "127.0.0.1"

#NOTE: These variables could perhaps go into a dictionary for each sound
osc_data            = 0
start_value         = -1
stop_value          = 2
is_playing          = False
volume_link         = False
normalize_volume    = False


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
def set_start_value():
    global start_value
    print(  "\nENTER        - Set start value",
            "\nN + ENTER    - Don't set start value")
    user_input = input().lower()

    if user_input == "n":
        start_value = -1 # Set to a value outside the range [0 - 1]
        print("No start value set")
    else:
        start_value = osc_data
        print(f"Start value set to {osc_data}")


def set_stop_value():
    global stop_value
    print(  "\nENTER        - Set stop value",
            "\nN + ENTER    - Don't set stop value")
    user_input = input().lower()

    if user_input == "n":
        stop_value = 2 # Set to a value outside the range [0-1]
        print("No stop value set")
    else:
        stop_value = osc_data
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


# Run OSC server in background thread
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()


mixer.init()
ambience_loop = mixer.Sound("audio/ambience_loop.flac")
ambience_loop.set_volume(1)


try:
    set_start_value() # Ask user for start value
    set_stop_value() # Ask user for stop value
    set_volume_link() # Ask user if they want to link the volume to the osc data input
    #TODO: Ask user if they want to loop

    while True:
        #TODO: no sound plays when start value is larger than stop value
        if start_value < osc_data < stop_value:
            if not is_playing:
                ambience_loop.play(-1)
                is_playing = True
        else:
            if is_playing:
                ambience_loop.stop()
                is_playing = False

        if volume_link:
            if normalize_volume:
                ambience_loop.set_volume((osc_data - start_value) / (stop_value - start_value)) # Normalize to [0-1]
            else:
                ambience_loop.set_volume(osc_data)

        time.sleep(0.001)

except KeyboardInterrupt:
    ambience_loop.stop()
    print("\nProgram terminated.")