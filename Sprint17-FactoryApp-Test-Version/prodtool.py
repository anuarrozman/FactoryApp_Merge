import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
import serial
import subprocess
from tkinter import scrolledtext
from threading import Thread
from hidserialscan import get_hidraw_devices
from tkinter import filedialog
from configparser import ConfigParser
import os
import time
from tkinter import messagebox
import glob
from dmm import DeviceSelectionApp
import mysql.connector

class SerialCommunicationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Communication App")
        self.root.minsize(600, 300)  # Set minimum window size

        # Serial port configuration
        self.serial_port = serial.Serial()
        self.read_thread = None  # Thread for reading data

        self.selected_port = ""
        
        self.mac_address_variable = ""

        self.create_widgets()
        self.create_popupwindow_widgets()
        self.create_text_widgets()
        self.create_menubar()
        self.device_selection_app = DeviceSelectionApp()
        self.root.protocol("WM_DELETE_WINDOW", self.closing_window)
    
    def close_window(self):
        # self.close_serial_port()
        self.root.destroy()
            
    def on_select_dmm_port(self, event):
        selected_device = self.dmm_var.get()
        print(f"Selected DMM device: {selected_device}")

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("INI files", "*.ini")])
        if file_path:
            # Read the contents of the .ini file
            config = ConfigParser()
            config.read(file_path)
            # Write the contents to auto_test.ini
            with open('auto_test.ini', 'w') as f:
                config.write(f)
            self.file_path_label.config(text="Selected File: " + file_path)
            self.receive_text.delete(1.0, tk.END)

    def create_menubar(self):
        menubar = tk.Menu(root)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Cut")
        edit_menu.add_command(label="Copy")
        edit_menu.add_command(label="Paste")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="View")
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Tools")
        # Associate the flash_tool_checking function with the menu item
        tools_menu.add_command(label="Upload Automated Test Script", command=self.upload_file)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=help_menu)

        root.config(menu=menubar)

    def create_widgets(self):
        self.serial_baud_frame = tk.Frame(root)
        self.serial_baud_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.port_label1 = tk.Label(self.serial_baud_frame, text="Factory Port:")
        self.port_label1.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.port_var1 = tk.StringVar()
        self.port_dropdown1 = ttk.Combobox(self.serial_baud_frame, textvariable=self.port_var1)
        self.port_dropdown1.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.port_dropdown1['values'] = [port.device for port in serial.tools.list_ports.comports()]

        self.baud_label1 = tk.Label(self.serial_baud_frame, text="Baud Rate:")
        self.baud_label1.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        self.baud_var1 = tk.StringVar()
        self.baud_dropdown1 = ttk.Combobox(self.serial_baud_frame, textvariable=self.baud_var1)
        self.baud_dropdown1.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.baud_dropdown1['values'] = ["9600", "115200", "460800"]
        self.baud_dropdown1.set("115200")

        self.open_port_button = ttk.Button(self.serial_baud_frame, text="Open Port", command=self.open_serial_port)
        self.open_port_button.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)

        self.close_port_button = ttk.Button(self.serial_baud_frame, text="Close Port", command=self.close_serial_port())
        self.close_port_button.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        self.dmm_label = tk.Label(self.serial_baud_frame, text="DMM Port:")
        self.dmm_label.grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)
        
        self.dmm_button_1 = tk.Button(self.serial_baud_frame, text="MultiMeter1", command=lambda: self.device_selection_app.select_device(1))
        self.dmm_button_1.grid(row=0, column=7, padx=5, pady=5, sticky=tk.W)    
        
        self.dmm_button_2 = tk.Button(self.serial_baud_frame, text="MultiMeter2", command=lambda: self.device_selection_app.select_device(2))
        self.dmm_button_2.grid(row=0, column=8, padx=5, pady=5, sticky=tk.W)

        self.file_path_label = tk.Label(self.root, text="Selected file: None")
        self.file_path_label.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)

    def send_command(self, command):
        if self.serial_port.is_open:
            self.serial_port.write(command.encode())
            print(f"Sent command: {command}")
        else:
            print("Serial port not open.")

    def send_data_auto(self):
        auto_data = "polyaire&ADT\r\n"
        if self.serial_port.is_open:
            self.serial_port.write(auto_data.encode())
            print(f"Auto-sent: {auto_data}")
        else:
            print("Serial port not open.")

    def open_serial_port(self):
        selected_port = self.port_var1.get()
        selected_baud = int(self.baud_var1.get())
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
            if self.serial_port.is_open:
                self.serial_port.close()
                print("Closed port")
            else:
                print("Port is not open.")
        except serial.SerialException as e:
            print(f"Error: {e}")
    
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
                        
                        self.update_database(self.mac_address_variable)
                        self.mac_address_variable = ""

            except UnicodeDecodeError as decode_error:
                print(f"Error decoding data: {decode_error}")
                self.receive_text.config(state=tk.NORMAL)
                self.receive_text.insert(tk.END, f"Error decoding data: {decode_error}\n")
                self.receive_text.config(state=tk.DISABLED)
                self.receive_text.see(tk.END)
            except Exception as e:
                print(f"Error reading data: {e}")
                self.receive_text.config(state=tk.NORMAL)
                self.receive_text.insert(tk.END, f"Error reading data: {e}\n")
                self.receive_text.config(state=tk.DISABLED)
                self.receive_text.see(tk.END)
    
    def update_database(self, mac_address):
        try:
            connection = mysql.connector.connect(
        host="localhost",
        user="anuarrozman2303",
        password="Matter2303!",
        database="device_mac_sn"
            )
            
            cursor = connection.cursor()

            # Check if the MAC address already exists in the database
            cursor.execute("SELECT * FROM mac_address WHERE dev_mac = %s", (mac_address,))
            result = cursor.fetchone()

            if result:
                print("MAC address already exists in the database.")
            else:
                # Insert the MAC address into the database
                cursor.execute("INSERT INTO mac_address (dev_mac) VALUES (%s)", (mac_address,))
                connection.commit()
                print("MAC address inserted into the database.")

        except mysql.connector.Error as error:
            print("Failed to update database:", error)

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection closed.")

    def create_popupwindow_widgets(self):
        popup_button_frame = ttk.Frame(self.root)
        popup_button_frame.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        popup_label = ttk.Label(popup_button_frame, text="Funct Test", font=("Arial", 10))
        popup_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        # Auto / Manual        
        popup_button = [
            {"text": "Auto", "command": None, "column": 1},
            {"text": "Manual", "command": lambda: self.open_manual_test_window(), "column": 2}
        ]

        for info in popup_button:
            button = ttk.Button(popup_button_frame, text=info["text"], command=info["command"])
            button.grid(row=0, column=info["column"], padx=10, pady=10, sticky=tk.W)
    
    def open_manual_test_window(self):
        manual_test_window = tk.Toplevel(self.root)
        manual_test_window.title("Manual Test")
        manual_test_window.minsize(400, 300)

        manual_test_frame = ttk.Frame(manual_test_window)
        manual_test_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        
        # Search for manual_test.ini starting from the root directory
        config_path = self.find_manual_test_ini("/")
        if config_path:
            self.create_buttons_from_config(self.load_config(config_path), manual_test_frame)
        else:
            print("manual_test.ini not found.")

    def find_manual_test_ini(self, start_dir):
        for dirpath, dirnames, filenames in os.walk(start_dir):
            if "manual_test.ini" in filenames:
                return os.path.join(dirpath, "manual_test.ini")
        return None
    
    def load_config(self, filename):
        config = ConfigParser()
        config.read(filename)
        return config

    def create_buttons_from_config(self, config, parent):
        sections = config.sections()
        buttons = {}
        for section in sections:
            section_frame = tk.LabelFrame(parent, text=section)
            section_frame.pack(padx=10, pady=5, fill="both", expand=True)

            for key, value in config.items(section):
                # Append \r\n to the value to ensure correct line endings
                value_with_line_endings = value + "\r\n"
                button = tk.Button(section_frame, text=key, command=lambda v=value_with_line_endings: self.send_command(v))
                button.pack(side=tk.LEFT, padx=5, pady=5)
                buttons[key] = button
        return buttons

    def create_text_widgets(self):
        text_frame = ttk.Frame(self.root)
        text_frame.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.receive_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, state=tk.DISABLED, height=24, width=70)
        self.receive_text.grid(row=2, column=0, columnspan=5, padx=5, pady=5, sticky=tk.W)

        self.clear_button = ttk.Button(text_frame, text="Clear", command=self.clear_received_data)
        self.clear_button.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

    def clear_received_data(self):
        self.receive_text.configure(state=tk.NORMAL)
        self.receive_text.delete(1.0, tk.END)
        self.receive_text.configure(state=tk.DISABLED)

    def closing_window(self):
        for port_info in serial.tools.list_ports.comports():
            # Check if the object has a close() method
            if hasattr(port_info, 'close') and callable(port_info.close):
                port_info.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialCommunicationApp(root)
    hidraw_devices = get_hidraw_devices() 
    root.protocol("WM_DELETE_WINDOW", app.closing_window)
    root.mainloop()
