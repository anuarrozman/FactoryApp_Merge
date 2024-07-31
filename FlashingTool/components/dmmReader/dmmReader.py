import tkinter as tk
from tkinter import messagebox, ttk
import hid
from components.dmmReader.ut61eplus import UT61EPLUS
import logging

logger = logging.getLogger(__name__)

class DeviceSelectionApp:
    def __init__(self, parent_frame, status_label1, status_label2):
        self.parent_frame = parent_frame
        self.devices = []
        self.create_widgets()
        self.refresh_devices()
        self.status_label1 = status_label1
        self.status_label2 = status_label2

    def create_widgets(self):
        self.device_label = tk.Label(self.parent_frame, text="Devices:", state=tk.DISABLED)
        self.device_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.device_buttons_frame = tk.Frame(self.parent_frame)
        self.device_buttons_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky=tk.W)

        self.refresh_button = tk.Button(self.parent_frame, text="Refresh Devices", command=self.refresh_devices, state=tk.DISABLED)
        self.refresh_button.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

    def refresh_devices(self):
        try:
            self.devices = hid.enumerate(UT61EPLUS.CP2110_VID, UT61EPLUS.CP2110_PID)
            self.update_device_buttons()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            logger.error(f"Error refreshing devices: {e}")

    def update_device_buttons(self):
        # Clear existing buttons
        for widget in self.device_buttons_frame.winfo_children():
            widget.destroy()

        # Create buttons for each device
        for i, device in enumerate(self.devices):
            button = tk.Button(self.device_buttons_frame, text=f"Device {i}", command=lambda idx=i: self.select_device(idx), state=tk.DISABLED if not self.devices else tk.NORMAL)
            button.grid(row=0, column=i, padx=5, pady=5, sticky=tk.W)

    def select_device(self, device_number):
        try:
            if device_number < len(self.devices):
                # print(f"Selected device: {self.devices[device_number]}")
                logger.info(f"Selected device: {self.devices[device_number]}")
                self.read_multimeter(device_number)
            else:
                # messagebox.showerror("Error", "Selected device number is out of range.")
                logger.error("Selected device number is out of range.")
        except Exception as e:
            # messagebox.showerror("Error", str(e))
            logger.error(f"Error selecting device: {e}")

    def read_multimeter(self, device_number):
        try:
            dev = UT61EPLUS(device_number)  # Pass the selected device number to UT61EPLUS
            dmm = dev
            dmm.writeMeasurementToFile('dmm_output.txt')
            dmm.sendCommand('lamp')

            measurement = dmm.takeMeasurement()
            if hasattr(measurement, 'display'):
                display_value = float(measurement.display)
                # messagebox.showinfo("Measurement", f"Measurement: {display_value}")
                logger.info(f"Measurement: {display_value}")
                self.check_voltage(display_value)
            else:
                # messagebox.showerror("Measurement Error", "Failed to extract display value from measurement.")
                logger.error("Failed to extract display value from measurement.")
        except Exception as e:
            # messagebox.showerror("Error", str(e))
            logger.error(f"Error reading multimeter: {e}")

    def check_voltage(self, voltage):
        if self.is_3_3_voltage(voltage):
            # messagebox.showinfo("Voltage Reading", f"Voltage reading from 3.3V multimeter: {voltage}")
            logger.info(f"Voltage reading from 3.3V multimeter: {voltage}")
        elif self.is_5_voltage(voltage):
            # messagebox.showinfo("Voltage Reading", f"Voltage reading from 5V multimeter: {voltage}")
            logger.info(f"Voltage reading from 5V multimeter: {voltage}")
        else:
            # messagebox.showinfo("Voltage Reading", f"Invalid voltage reading: {voltage}")
            logger.info(f"Invalid voltage reading: {voltage}")
            self.status_label1.config(text=f"Invalid voltage reading: {voltage}")

    def is_3_3_voltage(self, voltage):
        # Later change to 3V - 4V
        if 0.01 <= voltage <= 0.03:
            self.status_label1.config(text=f"Success {voltage}")
            return True
        else:
            return False

    def is_5_voltage(self, voltage):
        # Later change to 4.9V - 5.1V
        if 0.04 <= voltage <= 0.05:
            self.status_label2.config(text=f"Success: {voltage}")
            return True
        else:
            return False
