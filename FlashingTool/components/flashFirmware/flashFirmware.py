import subprocess
import os
import logging
import signal
import io

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FlashFirmware:
    
    def __init__(self, status_label, status_label_1, status_label_2):
        self.status_label = status_label
        self.status_label_1 = status_label_1
        self.status_label_2 = status_label_2
        self.log_capture_string = io.StringIO()
        self.ch = logging.StreamHandler(self.log_capture_string)
        self.ch.setLevel(logging.INFO)
        self.ch.setFormatter(logging.Formatter('%(message)s'))
        # Clean up previous handlers if any to avoid duplicate logs
        if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
            logger.addHandler(self.ch)
    
    def find_bin_path(self, keyword, search_directory):
        for root, dirs, files in os.walk(search_directory):
            for file in files:
                if file.endswith(".bin") and keyword in file:
                    return os.path.join(root, file)
        return None
    
    def export_esp_idf_path(self):
        # Define the path to the esp-idf directory
        esp_idf_path = "/home/anuarrozman/esp/esp-idf"

        # Define the command to source the export.sh script
        command = f"source {esp_idf_path}/export.sh"

        # Execute the command
        try:
            result = subprocess.run(command, shell=True, executable='/bin/bash', check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in result.stdout.splitlines():
                logger.info(line.strip())
                if "idf.py build" in line:
                    logger.info("ESP-IDF environment variables set.")
        except subprocess.CalledProcessError as e:
            logger.error(f"An error occurred: {e}")

    def flash_s3_firmware(self, port_var, baud_var):
        selected_port = port_var
        selected_baud = baud_var

        # Define keywords for each bin file
        keywords = {
            "boot_loader": "bootloader",
            "partition_table": "partition-table",
            "ota_data_initial": "ota_data_initial",
            # "firmware": "adt_matter_project_"
            "firmware": "v1_0_0-20240716-de5"
        }

        # Define the directory to search in
        search_directory = "/usr/src/app/ATSoftwareDevelopmentTool/FlashingTool/firmware/s3"

        # Find paths for each bin file using keywords
        bin_paths = {key: self.find_bin_path(keyword, search_directory) for key, keyword in keywords.items()}

        boot_loader_path = bin_paths["boot_loader"]
        partition_table_path = bin_paths["partition_table"]
        ota_data_initial_path = bin_paths["ota_data_initial"]
        fw_path = bin_paths["firmware"]

        # Check if all paths are valid
        if not all(bin_paths.values()):
            logger.error("Error: Unable to find one or more bin files")
            return

        # Run esptool.py command
        # command = f"esptool.py -p {selected_port} -b {selected_baud} write_flash 0x0 {boot_loader_path} 0xc000 {partition_table_path} 0x1e000 {ota_data_initial_path} 0x200000 {fw_path}"
        # command = f"openocd -f openocd/esp_usb_jtag.cfg -f openocd/esp32s3-builtin.cfg --command 'program {fw_path} 0x200000' --command 'program {ota_data_initial_path} 0x1e000' --command 'program {partition_table_path} 0xc000' --command 'program {boot_loader_path} 0x0'"

        # try:
        #     # Open subprocess with stdout redirected to PIPE
        #     process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        #     # Read stdout line by line and log in real-time
        #     for line in iter(process.stdout.readline, ''):
        #         logger.info(line.strip())
        #         # if "Hard resetting via RTS pin" in line:
        #         #     logger.info("Firmware Flashing Complete")
        #         if "Listening on port 4444 for telnet connections" in line:
        #             # execute terminate openocd here
        #             process.send_signal(subprocess.signal.SIGINT)
        #             break
                
        #             logger.info("Firmware Flashing Complete")

        #     process.stdout.close()
        #     process.wait()  # Wait for the process to finish

        # except subprocess.CalledProcessError as e:
        #     logger.error(f"Error running esptool.py: {e}")
        # except Exception as e:
        #     logger.error(f"An unexpected error occurred: {e}")
        

        command = f"openocd -f openocd/esp_usb_jtag.cfg -f openocd/esp32s3-builtin.cfg --command 'program_esp {ota_data_initial_path} 0x1e000' --command 'program_esp {partition_table_path} 0xc000' --command 'program_esp {boot_loader_path} 0x0' --command 'program_esp {fw_path} 0x200000 verify exit' "
        # command = f"openocd -s /home/anuarrozman/esp/openocd-esp32/share/openocd/scripts -f openocd/esp_usb_jtag.cfg -f openocd/esp32s3-builtin.cfg --command 'program {ota_data_initial_path} 0x1e000' --command 'program {partition_table_path} 0xc000' --command 'program {boot_loader_path} 0x0' --command 'program {fw_path} 0x200000' "


        try:
            # Open subprocess with stdout redirected to PIPE
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            # Read stdout line by line and log in real-time
            for line in iter(process.stdout.readline, ''):
                logger.info(line.strip())
                if "** Verify OK **" in line:
                    # process.send_signal(signal.SIGINT)
                    process.terminate()
                    logger.info("Firmware Flashing Complete")
                    break

            # Ensure the process has terminated
            process.stdout.close()
            process.wait()
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running openocd: {e}")

        
        # After the process completes, update the flashing status
        self.get_flashing_s3_status()
        
    def flash_h2_firmware(self, port_var, baud_var):
        selected_port = port_var
        selected_baud = baud_var

        # Define keywords for each bin file
        keywords = {
            "boot_loader": "bootloader",
            "partition_table": "partition-table",
            "firmware": "ATIR_H2.bin"
        }

        # Define the directory to search in
        search_directory = "/usr/src/app/ATSoftwareDevelopmentTool/FlashingTool/firmware/h2"

        # Find paths for each bin file using keywords
        bin_paths = {key: self.find_bin_path(keyword, search_directory) for key, keyword in keywords.items()}

        boot_loader_path = bin_paths["boot_loader"]
        partition_table_path = bin_paths["partition_table"]
        fw_path = bin_paths["firmware"]

        # Check if all paths are valid
        if not all(bin_paths.values()):
            logger.error("Error: Unable to find one or more bin files")
            return

        # Run esptool.py command
        command = f"esptool.py -p {selected_port} -b {selected_baud} write_flash 0x0 {boot_loader_path} 0x8000 {partition_table_path} 0x10000 {fw_path}"

        try:
            # Open subprocess with stdout redirected to PIPE
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            # Read stdout line by line and log in real-time
            for line in iter(process.stdout.readline, ''):
                logger.info(line.strip())
                if "Hard resetting via RTS pin" in line:
                    logger.info("Firmware Flashing Complete")

            process.stdout.close()
            process.wait()  # Wait for the process to finish

        except subprocess.CalledProcessError as e:
            logger.error(f"Error running esptool.py: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        
        # After the process completes, update the flashing status
        self.get_flashing_h2_status()

    def get_flashing_s3_status(self):
        self.ch.flush()
        log_contents = self.log_capture_string.getvalue()
        if "Firmware Flashing Complete" in log_contents:
            self.update_status_label("Completed", "green", ("Helvetica", 12, "bold"))
        else:
            self.update_status_label("Failed", "red", ("Helvetica", 12, "bold"))
            
    def get_flashing_h2_status(self):
        self.ch.flush()
        log_contents = self.log_capture_string.getvalue()
        if "Firmware Flashing Complete" in log_contents:
            self.update_status_label1("Completed", "green", ("Helvetica", 12, "bold"))
        else:
            self.update_status_label1("Failed", "red", ("Helvetica", 12, "bold"))
            
    def get_device_mac_address(self, port_var):
        selected_port = port_var
        command = f"esptool.py -p {selected_port} read_mac"
        
        try:
            # Open subprocess with stdout redirected to PIPE
            logger.info("Reading MAC Address...")
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            # Read stdout line by line and log in real-time
            for line in iter(process.stdout.readline, ''):
                logger.info(line.strip())
                if "MAC:" in line:
                    mac_address = line.split("MAC:")[1].strip()
                    self.update_status_label2(f"{mac_address}", "black", ("Helvetica", 12, "bold"))
                    logger.info(f"MAC Address: {mac_address}")
                    break
            
            # Ensure the process has terminated
            process.stdout.close()
            process.wait()
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running esptool.py: {e}")

    def update_status_label(self, message, fg, font):
        self.status_label.config(text=message, fg=fg, font=font)  # Update the status label with the message
        
    def update_status_label1(self, message, fg, font):
        self.status_label_1.config(text=message, fg=fg, font=font)
        
    def update_status_label2(self, message, fg, font):
        self.status_label_2.config(text=message, fg=fg, font=font)

