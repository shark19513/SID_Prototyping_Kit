import time
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
import threading
from pygame import mixer


receive_port    = 9008
ip_address      = "127.0.0.1"
slider_value    = 0
start_value     = -1
stop_value      = 2
is_playing      = False


def handle_slider(address, *args):
    global slider_value
    slider_value = args[0]

def start_server():
    dispatcher = Dispatcher()
    dispatcher.map("/slider", handle_slider)
    server = osc_server.ThreadingOSCUDPServer((ip_address, receive_port), dispatcher)
    print(f"Server listening on {ip_address}:{receive_port}")
    server.serve_forever()

def set_start_value():
    global start_value
    print(  "\nENTER        - Set start value",
            "\nN + ENTER    - Don't set start value")
    user_input = input().lower()

    if user_input == "n":
        start_value = -1 # Set to a value outside the range [0 - 1]
        print("No start value set")
    else:
        start_value = slider_value
        print(f"Start value set to {slider_value}")

def set_stop_value():
    global stop_value
    print(  "\nENTER        - Set stop value",
            "\nN + ENTER    - Don't set stop value")
    user_input = input().lower()

    if user_input == "n":
        stop_value = 2 # Set to a value outside the range [0 - 1]
        print("No stop value set")
    else:
        stop_value = slider_value
        print(f"Stop value set to {slider_value}")

# run OSC server in background thread
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()


mixer.init()
ambience_loop = mixer.Sound("audio/ambience_loop.mp3")


try:
    set_start_value()
    set_stop_value()
    #TODO: normalize?

    while True:
        #TODO: no sound plays when start value is larger than stop value
        if start_value < slider_value < stop_value:
            if not is_playing:
                ambience_loop.play(-1)
                is_playing = True
        else:
            if is_playing:
                ambience_loop.stop()
                is_playing = False

        ambience_loop.set_volume(slider_value)
        time.sleep(0.001)

except KeyboardInterrupt:
    ambience_loop.stop()
    print("\nProgram terminated.")