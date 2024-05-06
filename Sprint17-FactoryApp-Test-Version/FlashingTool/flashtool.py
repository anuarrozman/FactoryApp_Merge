import tkinter as tk
from tkinter import ttk, scrolledtext
import serial.tools.list_ports
import serial
import subprocess
import os
import requests
import mysql.connector
from threading import Thread

class SerialCommunicationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Communication App")
        self.root.minsize(600, 300)  # Set minimum window size

        # Serial port configuration
        self.serial_port = None
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
            self.log_message(f"Error running dmm.py: {e}")

    def flash_tool_checking(self):
        command = "esptool.py --help"
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            output = result.stdout
            self.log_message(output)
        except subprocess.CalledProcessError as e:
            self.log_message(f"Error running esptool.py: {e}")

    def download_list(self):
        url = "http://localhost:3000/devices"  # Correct endpoint
        try:
            response = requests.get(url)
            data = response.json()
            self.insert_data(data)
            self.display_data(data)
        except Exception as e:
            self.log_message("Error downloading data: " + str(e))

    def insert_data(self, data):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="anuarrozman2303",
                password="Matter2303!",
                database="device_mac_sn"
            )
            cursor = conn.cursor()
            for device in data:
                matter_cert_id = device.get("matter_cert_id", "N/A")
                serial_number = device.get("serial_no", "N/A")  # Correct key to access serial number
                mac_address = device.get("mac_address", "N/A")
                cursor.execute("INSERT INTO device_info (matter_cert_id, serial_number, mac_address) VALUES (%s, %s, %s)", (matter_cert_id, serial_number, mac_address))
            conn.commit()
            self.log_message("Data inserted successfully!")
        except mysql.connector.Error as e:
            self.log_message(f"Error inserting data into database: {e}")
        finally:
            cursor.close()
            conn.close()

    def find_bin_path(self, keyword):
        for root, dirs, files in os.walk("/"):
            for file in files:
                if file.endswith(".bin") and keyword in file:
                    return os.path.join(root, file)
        return None

    def flash_firmware(self):
        selected_port = self.port_var.get()
        selected_baud = self.baud_var.get()
        
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
        query = "SELECT matter_cert_id FROM device_info WHERE status IS NULL OR status = FALSE LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return result[0]  # Return the certid
        else:
            return None  # Return None if no certid found

    # Function to get the path of the .bin file for the selected certid
    def get_bin_path(self, certid):
        for root, dirs, files in os.walk("/"):  # Walk through all files and directories in the current directory and its subdirectories
            for file in files:
                if file.endswith(".bin") and certid in file:  # Check if the file is a .bin file and contains the certid in its name
                    return os.path.join(root, file)  # Return the path of the .bin file
        return None  # Return None if no .bin file with the certid is found

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
                    self.log_message(f"Flashing cert {certid} on port {selected_port}...")
                    self.log_message(f"Cert {certid} flashed successfully.")
                else:
                    self.log_message("No port selected. Please select a port before flashing.")
            else:
                self.log_message("No .bin file found for this certid.")
        else:
            self.log_message("No available certid with status not true.")

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
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                self.log_message("Closed port")
            else:
                self.log_message("Port is not open.")
        except serial.SerialException as e:
            self.log_message(f"Error closing serial port: {e}")

    def update_status(self, certid):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="anuarrozman2303",
                password="Matter2303!",
                database="device_mac_sn"
            )
            cursor = connection.cursor()
            query = "UPDATE device_info SET status = TRUE WHERE matter_cert_id = %s"
            cursor.execute(query, (certid,))
            connection.commit()
        except mysql.connector.Error as e:
            self.log_message(f"Error updating status in database: {e}")
        finally:
            cursor.close()
            connection.close()
            
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
            cursor.execute("SELECT * FROM device_info WHERE mac_address = %s", (mac_address,))
            result = cursor.fetchone()

            if result:
                print("MAC address already exists in the database.")
            else:
                # Insert the MAC address into the database
                cursor.execute("INSERT INTO device_info (mac_address) VALUES (%s)", (mac_address,))
                connection.commit()
                print("MAC address inserted into the database.")

        except mysql.connector.Error as error:
            print("Failed to update database:", error)

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection closed.")
            
    def display_data(self, data):
        self.clear_received_data()  # Clear the text frame
        for device in data:
            matter_cert_id = device.get("matter_cert_id", "N/A")
            serial_number = device.get("serial_number", "N/A")  # Correct field name
            self.log_message(f"Matter Cert ID: {matter_cert_id}, Serial: {serial_number}")
        self.log_message("Data downloaded successfully!")
        
    def get_device_mac(self):
        command = "FF:3;MAC?\r\n"
        self.send_command(command)
        
    def send_command(self, command):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(command.encode())
        else:
            self.log_message("Port is not open. Please open the port before sending commands.")
            
    def send_data_auto(self):
        auto_data = "polyaire&ADT\r\n"
        if self.serial_port.is_open:
            self.serial_port.write(auto_data.encode())
            print(f"Auto-sent: {auto_data}")
        else:
            print("Serial port not open.")
            
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

    def create_menubar(self):
        menubar = tk.Menu(root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Check Flash Tool", command=self.flash_tool_checking)
        tools_menu.add_command(label="Download List", command=self.download_list)
        menubar.add_cascade(label="Tools", menu=tools_menu)

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

        self.flash_button = ttk.Button(self.serial_baud_frame, text="Flash FW", command=self.flash_firmware)
        self.flash_button.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        
        self.cert_flash_button = ttk.Button(self.serial_baud_frame, text="Flash Cert", command=self.flash_cert)
        self.cert_flash_button.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        self.port_label1 = tk.Label(self.serial_baud_frame, text="Factory Port:")
        self.port_label1.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.port_var1 = tk.StringVar()
        self.port_dropdown1 = ttk.Combobox(self.serial_baud_frame, textvariable=self.port_var1) ##, state="disabled")
        self.port_dropdown1.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.port_dropdown1['values'] = [port.device for port in serial.tools.list_ports.comports()]
        
        self.baud_label1 = tk.Label(self.serial_baud_frame, text="Baud Rate:")
        self.baud_label1.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.baud_var1 = tk.StringVar()
        self.baud_dropdown1 = ttk.Combobox(self.serial_baud_frame, textvariable=self.baud_var1)
        self.baud_dropdown1.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        self.baud_dropdown1['values'] = ["9600", "115200", "460800"]
        self.baud_dropdown1.set("115200")
        
        self.open_port_button = ttk.Button(self.serial_baud_frame, text="Open Port", command=self.open_serial_port)
        self.open_port_button.grid(row=1, column=4, padx=5, pady=5, sticky=tk.W)
        
        self.close_port_button = ttk.Button(self.serial_baud_frame, text="Close Port", command=self.close_serial_port)
        self.close_port_button.grid(row=1, column=5, padx=5, pady=5, sticky=tk.W)
        
        self.read_device_mac_button = ttk.Button(self.serial_baud_frame, text="Read Device MAC", command=self.get_device_mac)
        self.read_device_mac_button.grid(row=2, column=6, padx=5, pady=5, sticky=tk.W)

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

    def log_message(self, message):
        self.receive_text.config(state=tk.NORMAL)
        self.receive_text.insert(tk.END, message + '\n')
        self.receive_text.config(state=tk.DISABLED)
        self.receive_text.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = SerialCommunicationApp(root)
    root.mainloop()
