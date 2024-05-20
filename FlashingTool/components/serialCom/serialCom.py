import serial
import serial.tools.list_ports
from threading import Thread
import tkinter as tk

from components.updateDB.updateDB import UpdateDB
class SerialCom:
    def __init__(self, receive_text):
        self.receive_text = receive_text  
        self.update_db = UpdateDB()
    
    def open_serial_port(self, selected_port, selected_baud):
        try:
            self.serial_port = serial.Serial(selected_port, baudrate=selected_baud, timeout=1)
            print(f"Opened port {selected_port} at {selected_baud} baud")
            
            # Store the selected port in the class variable
            self.selected_port = selected_port

            # Start a thread to continuously read data from the serial port
            self.read_thread = Thread(target=self.read_serial_data)
            self.read_thread.start()
        except serial.SerialException as e:
            print(f"Error: {e}")

    def close_serial_port(self):
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                self.log_message("Closed port")
            else:
                self.log_message("Port is not open.")
        except serial.SerialException as e:
            self.log_message(f"Error closing serial port: {e}")
            
    def read_serial_data(self):
        while self.serial_port.is_open:
            try:
                raw_data = self.serial_port.readline()
                decoded_data = raw_data.decode("utf-8", errors='replace').strip()

                if decoded_data:
                    self.receive_text.config(state=tk.NORMAL)
                    self.receive_text.insert(tk.END, decoded_data + '\n')
                    self.receive_text.config(state=tk.DISABLED)
                    self.receive_text.see(tk.END)
                    
                    if "." in decoded_data:
                        print("Factory Mode")
                        self.send_data_auto()
                    
                    if "3:MAC? = " in decoded_data:
                        # Extract MAC address from the received data
                        mac_address = decoded_data.split("=")[1].strip()
                        # Store MAC address in the variable
                        self.mac_address_variable = mac_address
                        print("MAC Address:", mac_address)
                        
                        self.update_db.update_database(self.mac_address_variable)
                        self.mac_address_variable = ""

            except UnicodeDecodeError as decode_error:
                print(f"Error decoding data: {decode_error}")
                self.receive_text.config(state=tk.NORMAL)
                self.receive_text.insert(tk.END, f"Error decoding data: {decode_error}\n")
                self.receive_text.config(state=tk.DISABLED)
                self.receive_text.see(tk.END)
            except Exception as e:
                pass

    def send_data_auto(self):
        auto_data = "polyaire&ADT\r\n"
        if self.serial_port.is_open:
            self.serial_port.write(auto_data.encode())
            print(f"Auto-sent: {auto_data}")
        else:
            print("Serial port not open.")

    def log_message(self, message):
        print(message)  # Replace this with your preferred logging mechanism
