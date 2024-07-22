# flash_cert.py

import os
import subprocess
import configparser
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

used_cert_ids = set()  # Track used cert-ids
class FlashCert:
    def __init__(self, status_label):
        self.status_label = status_label
        self.seleceted_order_number = None
        
    def get_cert_ids_for_order(self, orders, selected_order_no):
        cert_ids = [order['cert-id'] for order in orders if order['order-no'] == selected_order_no]
        return cert_ids

    def flash_certificate(self, cert_id, selected_port):
        if cert_id in used_cert_ids:
            logger.debug(f"Cert ID {cert_id} has already been used.")
            return False

        cert_dir = '/usr/src/app/ATSoftwareDevelopmentTool/FlashingTool/certs'
        cert_file_path = os.path.join(cert_dir, f"{cert_id}.cert")

        # Check if the file exists
        if not os.path.isfile(cert_file_path):
            logger.error(f"Certificate file {cert_file_path} does not exist.")
            return False
        
        if cert_file_path:
            if selected_port:
                logger.info(f"Flashing certificate with cert-id: {cert_file_path} on port {selected_port}")
                self.certify(cert_file_path, selected_port)
                self.update_status(cert_file_path)
                # self.create_folder()
                # self.save_cert_id_to_ini(os.path.join(os.path.dirname(__file__), self.get_serial_number()), cert_file_path)
                self.log_message(f"Cert {cert_file_path} flashed successfully.")
                self.update_status_label("Completed", "green", ("Helvetica", 12, "bold"))
            else:
                logger.error("No port selected. Please select a port before flashing.")
                self.update_status_label("Failed", "red", ("Helvetica", 12, "bold"))
        else:
            logger.error(f"No .bin file found for certId {cert_file_path}.")
            self.update_status_label("Failed", "red", ("Helvetica", 12, "bold"))
            
        # Simulate flashing the certificate
        used_cert_ids.add(cert_file_path)
        return True

    def get_remaining_cert_ids(self, cert_ids):
        return [cert_file_path for cert_file_path in cert_ids if cert_file_path not in used_cert_ids]
        
    def get_certId(self):
        try:
            with open('/usr/src/app/ATSoftwareDevelopmentTool/FlashingTool/device_data.txt', 'r') as file:
                for line in file:
                    if 'Matter Cert ID:' in line and 'Status: None' in line:
                        certId = line.split('Matter Cert ID: ')[1].split(',')[0].strip()
                        return certId
                self.log_message("No certId found in the text file.")
                return None
        except IOError as e:
            self.log_message(f"Error reading cert info from file: {e}")
            return None

    def create_folder(self):
        sn = self.get_serial_number()
        if sn:
            directory = os.path.join(os.path.dirname(__file__), sn)
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.log_message(f"Directory {directory} created.")
            else:
                self.log_message(f"Directory {directory} already exists.")
        else:
            self.log_message("No serial number found.")

    def save_cert_id_to_ini(self, directory, certId):
        config = configparser.ConfigParser()
        config['CERT'] = {'certId': certId}
        config['SN'] = {'serialNumber': self.get_serial_number()}
        with open(os.path.join(directory, 'cert_info.ini'), 'w') as configfile:
            config.write(configfile)
        self.log_message(f"CertId {certId} saved to {os.path.join(directory, 'cert_info.ini')}")

    def certify(self, bin_path, selected_port):
        command = (
            f"openocd -f openocd/esp_usb_jtag.cfg -f openocd/esp32s3-builtin.cfg "
            f"--command 'program_esp {bin_path} 0x10000 verify exit'"
        )
        
        try:
            # Open subprocess with stdout redirected to PIPE
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            # Read stdout line by line and log in real-time
            for line in iter(process.stdout.readline, ''):
                logger.info(line.strip())
                if "** Verify OK **" in line:
                    process.terminate()
                    logger.info("Cert Flashing Complete")
                    break
            
            # Ensure the process has terminated
            process.stdout.close()
            process.wait()
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running openocd: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    def update_status(self, certId):
        file_path = '/usr/src/app/ATSoftwareDevelopmentTool/FlashingTool/device_data.txt'

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            with open(file_path, 'w') as file:
                for line in lines:
                    if f'cert-id: {certId}' in line and 'Status: None' in line:
                        logger.debug(f"Updating status to '0' for certId {certId}")
                        line = line.replace('Status: None', 'Status: 0')
                    file.write(line)
            
            self.log_message(f"Status updated to '0' for certId {certId} in cert_info.txt.")
        except IOError as e:
            self.log_message(f"Error updating status in file: {e}")
        except Exception as e:
            self.log_message(f"An unexpected error occurred: {e}")

    def flash_cert(self, port_var):
        certId = self.get_certId()
        selected_port = port_var
        if certId:
            bin_path = self.get_bin_path(certId)
            if bin_path:
                if selected_port:
                    self.log_message(f"Flashing cert {certId} on port {selected_port}...")
                    self.certify(bin_path, selected_port)
                    self.update_status(certId)
                    self.create_folder()
                    self.save_cert_id_to_ini(os.path.join(os.path.dirname(__file__), self.get_serial_number()), certId)
                    self.log_message(f"Cert {certId} flashed successfully.")
                    self.update_status_label("Completed", "green", ("Helvetica", 12, "bold"))
                else:
                    self.log_message("No port selected. Please select a port before flashing.")
                    self.update_status_label("Failed", "red", ("Helvetica", 12, "bold"))
            else:
                self.log_message(f"No .bin file found for certId {certId}.")
                self.update_status_label("Failed", "red", ("Helvetica", 12, "bold"))
        else:
            self.log_message("No available certId found in the text file.")
            self.update_status_label("Failed", "red", ("Helvetica", 12, "bold"))

    def get_bin_path(self, certId):
        # for root, dirs, files in os.walk("/usr/src/app/ATSoftwareDevelopmentTool/FlashingTool/certs"):
        for root, dirs, files in os.walk("/usr/src/app/ATSoftwareDevelopmentTool/FlashingTool/certs"):
            for file in files:
                if file.endswith(".bin") and certId in file:
                    return os.path.join(root, file)  # Return the path of the .bin file
        return None  # Return None if no .bin file with the certId is found

    def get_serial_number(self):
        return "DummySerialNumber"  # Replace with actual logic to retrieve serial number

    def log_message(self, message):
        logger.info(message)  # Replace this with your preferred logging mechanism
        # self.log_message_callback(message)

    def update_status_label(self, message, fg, font):
        self.status_label.config(text=message, fg=fg, font=font)  # Update the status label with the message
