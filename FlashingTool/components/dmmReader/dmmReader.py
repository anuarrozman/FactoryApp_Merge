import tkinter as tk
from tkinter import messagebox, ttk
import hid
from components.dmmReader.ut61eplus import UT61EPLUS

class DeviceSelectionApp:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.selected_device_number = None  # Store the selected device number
        self.dev = None

        self.create_widgets()

    def create_widgets(self):
        self.device_label = tk.Label(self.parent_frame, text="Select Device:")
        self.device_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.device_combo = ttk.Combobox(self.parent_frame, state="readonly")
        self.device_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.refresh_button = tk.Button(self.parent_frame, text="Refresh Devices", command=self.refresh_devices)
        self.refresh_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        self.select_button = tk.Button(self.parent_frame, text="Select Device", command=self.on_select_device)
        self.select_button.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        self.refresh_devices()

    def refresh_devices(self):
        try:
            devices = hid.enumerate(UT61EPLUS.CP2110_VID, UT61EPLUS.CP2110_PID)
            self.device_combo['values'] = [f"{i}: {device['product_string']}" for i, device in enumerate(devices)]
            if devices:
                self.device_combo.current(0)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_select_device(self):
        selected_index = self.device_combo.current()
        if selected_index == -1:
            messagebox.showwarning("No Selection", "Please select a device from the dropdown list.")
        else:
            self.select_device(selected_index)

    def select_device(self, device_number):
        try:
            self.selected_device_number = device_number  # Store the selected device number
            devices = hid.enumerate(UT61EPLUS.CP2110_VID, UT61EPLUS.CP2110_PID)
            if device_number < len(devices):
                print(f"Selected device: {devices[device_number]}")
                self.read_multimeter()
            else:
                messagebox.showerror("Error", "Selected device number is out of range.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def read_multimeter(self):
        try:
            self.dev = UT61EPLUS(self.selected_device_number)  # Pass the selected device number to UT61EPLUS
            dmm = self.dev
            dmm.writeMeasurementToFile('dmm_output.txt')
            dmm.sendCommand('lamp')

            measurement = dmm.takeMeasurement()
            if hasattr(measurement, 'display'):
                display_value = measurement.display
                display_value = float(display_value)
                messagebox.showinfo("Measurement", f"Measurement: {display_value}")
                self.check_voltage(display_value)
            else:
                messagebox.showerror("Measurement Error", "Failed to extract display value from measurement.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def check_voltage(self, voltage):
        if self.is_3_3_voltage(voltage):
            messagebox.showinfo("Voltage Reading", f"Voltage reading from 3.3V multimeter: {voltage}")
        elif self.is_5_voltage(voltage):
            messagebox.showinfo("Voltage Reading", f"Voltage reading from 5V multimeter: {voltage}")
        else:
            messagebox.showinfo("Voltage Reading", f"Invalid voltage reading: {voltage}")

    def is_3_3_voltage(self, voltage):
        return 3.0 <= voltage <= 3.6

    def is_5_voltage(self, voltage):
        return 4.8 <= voltage <= 5.2