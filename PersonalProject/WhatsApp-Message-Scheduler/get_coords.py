from pynput.mouse import Listener

from pyautogui import size


def on_click(x, y, button, pressed):
    WIDTH, HEIGHT = size()

    x_perc = (100/WIDTH) * x
    y_perc = (100/HEIGHT) * y

    if pressed:
        print(f"Mouse clicked at position: X={x}, Y={y} -- ({x_perc}%, {y_perc}%)")

# Start the listener
with Listener(on_click=on_click) as listener:
    listener.join()