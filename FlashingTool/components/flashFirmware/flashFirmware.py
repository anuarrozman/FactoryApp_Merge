import subprocess
import tkinter as tk
import os


class FlashFirmware:
    
    def __init__(self, receive_text):
        self.receive_text = receive_text
    
    def find_bin_path(self, keyword):
        for root, dirs, files in os.walk("/"):
            for file in files:
                if file.endswith(".bin") and keyword in file:
                    return os.path.join(root, file)
        return None

    def flash_firmware(self, port_var, baud_var):
        selected_port = port_var.get()
        selected_baud = baud_var.get()
        
        # Define keywords for each bin file
        keywords = {
            "boot_loader": "boot_loader",
            "partition_table": "partition_table",
            "ota_data_initial": "ota_data_initial",
            "firmware": "adt_matter_project_A00000005_1_0_0-de1"
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
            self.log_message("Error: Unable to find one or more bin files")
            return

        # Run esptool.py command
        command = f"esptool.py -p {selected_port} -b {selected_baud} write_flash 0x0 {boot_loader_path} 0xc000 {partition_table_path} 0x1e000 {ota_data_initial_path} 0x200000 {fw_path}"

        try:
            # Execute the command and capture output
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            output = result.stdout
            
            # Print output line by line
            for line in output.splitlines():
                print(line)
                if "Hard resetting via RTS pin" in line:
                    self.receive_text.config(state=tk.NORMAL)
                    self.receive_text.insert(tk.END, "Firmware Flashing Complete\n")
                    self.receive_text.config(state=tk.DISABLED)
                    self.receive_text.see(tk.END)
                
        except subprocess.CalledProcessError as e:
            print(f"Error running esptool.py: {e}")
            self.receive_text.config(state=tk.NORMAL)
            self.receive_text.insert(tk.END, f"Error: {e}\n")
            self.receive_text.config(state=tk.DISABLED)
            self.receive_text.see(tk.END)