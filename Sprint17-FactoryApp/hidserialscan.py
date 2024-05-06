import os

def get_hidraw_devices():
    hidraw_devices = [device for device in os.listdir('/dev') if device.startswith('hidraw')]
    return hidraw_devices
