import tkinter as tk
from tkinter import ttk, scrolledtext
import serial.tools.list_ports
import os
from tkinter import messagebox
from cryptography.fernet import Fernet

from components.settingWindow.settingWindow import SettingApp
from components.toolsBar.toolsBar import ToolsBar
from components.flashFirmware.flashFirmware import FlashFirmware
from components.flashCert.flashCert import FlashCert
from components.serialCom.serialCom import SerialCom
from components.writeDevInfo.writeDeviceInfo import WriteDeviceInfo
from components.dmmReader.multimeter import Multimeter
from components.dmmReader.dmmReader import DeviceSelectionApp
from components.dmmReader.ut61eplus import UT61EPLUS
from components.adminLoginWindow.adminLoginWindow import AdminLoginApp
from components.manualTest.manualTest import ManualTestApp

class SerialCommunicationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Communication App")
        self.root.attributes('-zoomed', True)

        # Serial port configuration
        self.serial_port = None
        self.read_thread = None
        self.selected_port = ""

        # Create GUI elements
        self.initialize_gui()

        # Initialize components
        self.initialize_components()

        # Store reference to the Manual Test menu item
        self.manual_test_menu = None

    def initialize_gui(self):
        self.create_menubar()
        self.create_widgets()
        self.create_text_widgets()

        version = self.read_version_from_file("version.txt")  # Read version from file
        self.add_version_label(version)  # Add version number here

    def initialize_components(self):
        self.toolsBar = ToolsBar()
        self.flashFw = FlashFirmware(self.receive_text)
        self.flashCert = FlashCert(self.log_message)
        self.serialCom = SerialCom(self.receive_text)
        self.sendEntry = WriteDeviceInfo(self.send_command, self.log_message)
        self.dmmReader = DeviceSelectionApp(self.dmm_frame)
        self.multimeter = Multimeter()

    def refresh_dmm_devices(self):
        self.dmmReader.refresh_devices()

    def flash_tool_checking(self):
        self.toolsBar.flash_tool_checking()

    def download_list(self):
        self.toolsBar.download_list()

    def flash_firmware(self):
        self.flashFw.flash_firmware(self.port_var, self.baud_var)

    def flash_cert(self):
        self.flashCert.flash_cert(self.port_var)

    def open_serial_port(self):
        selected_port = self.port_var1.get()
        selected_baud = int(self.baud_var1.get())
        self.serialCom.open_serial_port(selected_port, selected_baud)

    def close_serial_port(self):
        self.serialCom.close_serial_port()

    def get_device_mac(self):
        command = "FF:3;MAC?\r\n"
        self.send_command(command)

    def send_command(self, command):
        if self.serialCom.serial_port and self.serialCom.serial_port.is_open:
            self.serialCom.serial_port.write(command.encode())
            self.log_message(f"Sent: {command.strip()}")
        else:
            self.log_message("Port is not open. Please open the port before sending commands.")

    def create_menubar(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Setting", command=self.config_setting)
        file_menu.add_command(label="Run As Admin", command=self.admin_login)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Check Flash Tool", command=self.flash_tool_checking)
        tools_menu.add_command(label="Download List", command=self.download_list)
        self.manual_test_menu = tools_menu.add_command(label="Manual Test", command=self.manual_test)
        tools_menu.entryconfig("Manual Test", state=tk.DISABLED)  
        self.tools_menu = tools_menu  
        menubar.add_cascade(label="Tools", menu=tools_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)
        
    def admin_login(self):
        login_window = tk.Toplevel(self.root)
        app = AdminLoginApp(login_window)
        login_window.wait_window(login_window)  # Wait for the login window to close
        if app.result:
            # Decrypt and verify the password
            decrypted_password = self.decrypt_password()
            print("Decrypted Password:", decrypted_password)  # Debugging message
            if decrypted_password == "admin":  # Replace "admin" with the actual password if needed
                messagebox.showinfo("Login Successful", "Admin login successful. Manual Test enabled.")
                # Change the Manual Test from menubar state to Normal
                self.tools_menu.entryconfig("Manual Test", state=tk.NORMAL)
            else:
                messagebox.showerror("Error", "Failed to decrypt password or invalid password!")

    def config_setting(self):
        SettingApp(tk.Toplevel(self.root))

    def manual_test(self):
        ManualTestApp(self.root, self.send_command).open_manual_test_window()

    def decrypt_password(self):
        key_file = "secret.key"
        password_file = "password.txt"
        try:
            with open(key_file, "rb") as kf:
                key = kf.read()
            with open(password_file, "rb") as pf:
                encrypted_password = pf.read()
            fernet = Fernet(key)
            decrypted_password = fernet.decrypt(encrypted_password).decode()
            return decrypted_password
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def create_widgets(self):
        self.serial_baud_frame = tk.Frame(self.root)
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
        self.port_dropdown1 = ttk.Combobox(self.serial_baud_frame, textvariable=self.port_var1)
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

        self.dmm_frame = tk.Frame(self.root)
        self.dmm_frame.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

    def create_text_widgets(self):
        text_frame = ttk.Frame(self.root)
        text_frame.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.receive_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, state=tk.DISABLED, height=24, width=48)
        self.receive_text.grid(row=2, column=0, columnspan=5, padx=5, pady=5, sticky=tk.W)

        self.clear_button = ttk.Button(text_frame, text="Clear", command=self.clear_received_data)
        self.clear_button.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

        self.send_entry = ttk.Entry(text_frame, width=48)
        self.send_entry.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky=tk.W)

        self.send_button = ttk.Button(text_frame, text="Send", command=lambda: self.sendEntry.send_entry_command(self.send_entry))
        self.send_button.grid(row=4, column=4, padx=5, pady=5, sticky=tk.W)

    def clear_received_data(self):
        self.receive_text.config(state=tk.NORMAL)
        self.receive_text.delete(1.0, tk.END)
        self.receive_text.config(state=tk.DISABLED)

    def log_message(self, message):
        self.receive_text.config(state=tk.NORMAL)
        self.receive_text.insert(tk.END, message + '\n')
        self.receive_text.config(state=tk.DISABLED)
        self.receive_text.see(tk.END)

    def read_version_from_file(self, file_name):
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        try:
            with open(file_path, "r") as file:
                version = file.readline().strip()
                return version
        except FileNotFoundError:
            return "Version not found"

    def add_version_label(self, version):
        version_label = tk.Label(self.root, text=f"Version: {version}")
        version_label.grid(row=99, column=99, sticky=tk.SE, padx=10, pady=10)  # Use a high number to ensure it's at the bottom right

        # Configure weight for the grid to ensure the label stays at the bottom right
        self.root.grid_rowconfigure(99, weight=1)
        self.root.grid_columnconfigure(99, weight=1)

    def on_exit(self):
        self.root.destroy()
        self.close_serial_port()

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialCommunicationApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_exit)
    root.mainloop()

