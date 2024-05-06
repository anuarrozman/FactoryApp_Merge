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

        # Create GUI elements
        self.create_widgets()
        self.create_text_widgets()
        self.create_menubar()

    def exec_testapp(self):
        script = "Sprint17-FactoryApp/prodtool.py"

        try:
            subprocess.run(["python3", script])

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

    def find_bin_path(self, keyword):
        for root, dirs, files in os.walk("/"):  
            for file in files:
                if file.endswith(".bin") and keyword in file:  
                    return os.path.join(root, file) 
        return None  

    def flash_firmware(self, receive_text):
        selected_port = self.port_var.get()
        selected_baud = self.baud_var.get()
        
        # Define keywords for each bin file
        keywords = {
            "boot_loader": "boot_loader",
            "partition_table": "partition_table",
            "ota_data_initial": "ota_data_initial",
            "firmware": "adt_matter_project_A00000001_1_0_0"
        }

        # Find paths for each bin file using keywords
        bin_paths = {key: self.find_bin_path(keyword) for key, keyword in keywords.items()}
        
        boot_loader_path = bin_paths["boot_loader"]
        partition_table_path = bin_paths["partition_table"]
        ota_data_initial_path = bin_paths["ota_data_initial"]
        fw_path = bin_paths["firmware"]


        # Check if all paths are valid
        if not all(bin_paths.values()):
            print("Error: Unable to find one or more bin files")
            receive_text.config(state=tk.NORMAL)
            receive_text.insert(tk.END, "Error: Unable to find one or more bin files\n")
            receive_text.config(state=tk.DISABLED)
            receive_text.see(tk.END)
            return

        # Run esptool.py command
        command = f"esptool.py -p {selected_port} -b {selected_baud} write_flash 0x0 {boot_loader_path} 0xc000 {partition_table_path} 0x1e000 {ota_data_initial_path} 0x200000 {fw_path}"

        
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
        
        self.cert_flash_button = ttk.Button(self.serial_baud_frame, text="Flash Cert", command=self.flash_cert)
        self.cert_flash_button.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
    # Function to update status in the database
    def update_status(self, certid):
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="anuarrozman2303",
            password="Matter2303!",
            database="device_mac_sn"
        )

        cursor = connection.cursor()

        # Update status to true for the selected certid
        query = "UPDATE matter_certid SET status = TRUE WHERE certid = %s"
        cursor.execute(query, (certid,))
        connection.commit()

        cursor.close()
        connection.close()        

    # Function to retrieve a certid where status is not true
    def get_certid(self):
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="anuarrozman2303",
            password="Matter2303!",
            database="device_mac_sn"
        )

        cursor = connection.cursor()

        # Retrieve a certid where status is NULL or FALSE
        query = "SELECT certid FROM matter_certid WHERE status IS NULL OR status = FALSE LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return result[0]  # Return the certid
        else:
            return None  # Return None if no certid found

    def flash_cert(self):
        certid = self.get_certid()
        selected_port = self.port_var.get()  # Retrieve the selected port from the Combobox
        if certid:
            bin_path = self.get_bin_path(certid)
            if bin_path:
                if selected_port:  # Use the selected port obtained from the Combobox
                    print(f"Flashing cert {certid} on port {selected_port}...")
                    self.certify(bin_path, selected_port)  # Pass the selected port to the certify function
                    print(f"Cert {certid} flashed successfully.")
                    self.update_status(certid)  # Update status only if .bin file is found
                    self.receive_text.config(state=tk.NORMAL)
                    self.receive_text.insert(tk.END, f"Flashing cert {certid} on port {selected_port}...\n")
                    self.receive_text.insert(tk.END, f"Cert {certid} flashed successfully.\n")
                    self.receive_text.config(state=tk.DISABLED)
                    self.receive_text.see(tk.END)
                else:
                    print("No port selected. Please select a port before flashing.")
                    self.receive_text.config(state=tk.NORMAL)
                    self.receive_text.insert(tk.END, "No port selected. Please select a port before flashing.\n")
                    self.receive_text.config(state=tk.DISABLED)
                    self.receive_text.see(tk.END)
            else:
                print("No .bin file found for this certid.")
                self.receive_text.config(state=tk.NORMAL)
                self.receive_text.insert(tk.END, "No .bin file found for this certid.\n")
                self.receive_text.config(state=tk.DISABLED)
                self.receive_text.see(tk.END)
        else:
            print("No available certid with status not true.")
            self.receive_text.config(state=tk.NORMAL)
            self.receive_text.insert(tk.END, "No available certid with status not true.\n")
            self.receive_text.config(state=tk.DISABLED)
            self.receive_text.see(tk.END)

    # Function to get the path of the .bin file for the selected certid
    def get_bin_path(self, certid):
        for root, dirs, files in os.walk("/"):  # Walk through all files and directories in the current directory and its subdirectories
            for file in files:
                if file.endswith(".bin") and certid in file:  # Check if the file is a .bin file and contains the certid in its name
                    return os.path.join(root, file)  # Return the path of the .bin file
        return None  # Return None if no .bin file with the certid is found

    # Function to flash the .bin file onto the device
    def certify(self, bin_path, selected_port):
        subprocess.run(["esptool.py", "-p", selected_port, "write_flash", "0x10000", bin_path])


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
