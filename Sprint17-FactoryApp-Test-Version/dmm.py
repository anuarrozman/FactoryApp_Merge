import tkinter as tk
from tkinter import messagebox
import hid
from ut61eplus import UT61EPLUS
class DeviceSelectionApp:
    def __init__(self):
        self.selected_device_number = None  # Store the selected device number
        self.dev = None

    def select_device(self, device_number):
        try:
            self.selected_device_number = device_number  # Store the selected device number
            devices = hid.enumerate(UT61EPLUS.CP2110_VID, UT61EPLUS.CP2110_PID)
            self.read_multimeter()
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

    def run(self):
        self.root.mainloop()
