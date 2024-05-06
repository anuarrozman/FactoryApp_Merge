import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
import serial
import subprocess
from tkinter import scrolledtext
from threading import Thread
from tkinter import filedialog
from configparser import ConfigParser
import os
import time
from tkinter import messagebox


class SerialCommunicationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Communication App")
        self.root.minsize(600, 300)  # Set minimum window size

        # Serial port configuration
        self.serial_port = serial.Serial()
        self.read_thread = None  # Thread for reading data

        self.selected_port = ""

        # Create GUI elements
        self.create_widgets()
        self.create_text_widgets()
        self.create_menubar()
    
    def exec_dmm(self):
        script = "dmm.py"
        output_file = "dmm_output.txt"

        try:
            subprocess.run(["python3", script])

            with open(output_file, "r") as file:
                output = file.read()
                self.receive_text.delete(1.0, tk.END)
                self.receive_text.config(state=tk.NORMAL)
                self.receive_text.insert(tk.END, output + '\n')
                self.receive_text.config(state=tk.DISABLED)
                self.receive_text.see(tk.END)

        except subprocess.CalledProcessError as e:
            print(f"Error running dmm.py: {e}")
            self.receive_text.config(state=tk.NORMAL)
            self.receive_text.insert(tk.END, f"Error: {e}\n")
            self.receive_text.config(state=tk.DISABLED)
            self.receive_text.see(tk.END)

    def flash_tool_checking(self, receive_text):
        command = f"esptool.py --help"
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            output = result.stdout
            print(output)
            receive_text.config(state=tk.NORMAL)
            receive_text.insert(tk.END, output + '\n')
            receive_text.config(state=tk.DISABLED)
            receive_text.see(tk.END)
        except subprocess.CalledProcessError as e:
            print(f"Error running esptool.py: {e}")
            receive_text.config(state=tk.NORMAL)
            receive_text.insert(tk.END, f"Error: {e}\n")
            receive_text.config(state=tk.DISABLED)
            receive_text.see(tk.END)

    def flash_firmware(self,receive_text):
        selected_port = self.port_var.get()
        selected_baud = self.baud_var.get()
        boot_loader_path = "firmware/boot_loader.bin"
        partition_table_path = "firmware/partition_table.bin"
        ota_data_initial_path = "firmware/ota_data_initial.bin"
        fw_path = "firmware/firmware.bin"

        # Check if all paths are valid
        if not all(os.path.exists(path) for path in [boot_loader_path, partition_table_path, ota_data_initial_path, fw_path]):
            print("Error: Invalid file paths")
            self.receive_text.insert(tk.END, "Error: Invalid file paths")
            self.receive_text.see(tk.END)
            return

        # Run esptool.py command
        command = f"esptool.py -p {selected_port} -b {selected_baud} write_flash 0x0 {boot_loader_path} 0xc000 {partition_table_path} 0x1e000 {ota_data_initial_path} 0x200000 {fw_path}"
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            output = result.stdout
            print(output)
            self.receive_text.config(state=tk.NORMAL)
            self.receive_text.insert(tk.END, output + '\n')
            self.receive_text.config(state=tk.DISABLED)
            self.receive_text.see(tk.END)
        except subprocess.CalledProcessError as e:
            print(f"Error running esptool.py: {e}")
            self.receive_text.config(state=tk.NORMAL)
            self.receive_text.insert(tk.END, output + '\n')
            self.receive_text.config(state=tk.DISABLED)
            self.receive_text.see(tk.END)

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
        tools_menu.add_command(label="Check Flash Tool", command=lambda: self.flash_tool_checking(self.receive_text))
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=help_menu)

        root.config(menu=menubar)

    def create_widgets(self):
        self.serial_baud_frame = tk.Frame(root)
        self.serial_baud_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.port_label = tk.Label(self.serial_baud_frame, text="Flash Port:")
        self.port_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(self.serial_baud_frame, textvariable=self.port_var)
        self.port_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.port_dropdown['values'] = [port.device for port in serial.tools.list_ports.comports()]

        self.baud_label = tk.Label(self.serial_baud_frame, text="Baud Rate:")
        self.baud_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        self.baud_var = tk.StringVar()
        self.baud_dropdown = ttk.Combobox(self.serial_baud_frame, textvariable=self.baud_var)
        self.baud_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.baud_dropdown['values'] = ["9600", "115200", "460800"]
        self.baud_dropdown.set("460800")

        self.flash_button = ttk.Button(self.serial_baud_frame, text="Flash Firmware", command=lambda:self.flash_firmware(self.receive_text))
        self.flash_button.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)

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

    def create_text_widgets(self):
        text_frame = ttk.Frame(self.root)
        text_frame.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.receive_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, state=tk.DISABLED, height=24, width=48)
        self.receive_text.grid(row=2, column=0, columnspan=5, padx=5, pady=5, sticky=tk.W)

        self.clear_button = ttk.Button(text_frame, text="Clear", command=self.clear_received_data)
        self.clear_button.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

    def clear_received_data(self):
        self.receive_text.configure(state=tk.NORMAL)
        self.receive_text.delete(1.0, tk.END)
        self.receive_text.configure(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialCommunicationApp(root)
    root.mainloop()

