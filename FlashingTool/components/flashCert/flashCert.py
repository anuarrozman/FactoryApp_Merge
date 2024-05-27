import os
import mysql.connector
import subprocess
import configparser

class FlashCert:
    def __init__(self, log_message_callback):
        self.log_message_callback = log_message_callback
        self.db_config = {
            "host": "localhost",
            "user": "anuarrozman2303",
            "password": "Matter2303!",
            "database": "device_mac_sn"
        }

    def get_certId(self):
        try:
            connection = self._connect_to_database()
            cursor = connection.cursor()
            query = "SELECT matter_cert_id FROM device_info WHERE status IS NULL LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            if result:
                return result[0]  # Return the certId
            else:
                return None  # Return None if no certId found
        except mysql.connector.Error as e:
            self.log_message(f"Error retrieving certId from database: {e}")
            return None

    def get_serial_number(self):
        try:
            connection = self._connect_to_database()
            cursor = connection.cursor()
            query = "SELECT serial_number FROM device_info WHERE status = 0 LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            if result:
                return result[0]  # Return the s/n
            else:
                return None  # Return None if no s/n found
        except mysql.connector.Error as e:
            self.log_message(f"Error retrieving s/n from database: {e}")
            return None

    def _connect_to_database(self):
        return mysql.connector.connect(**self.db_config)

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
        with open(os.path.join(directory, 'cert_info.ini'), 'w') as configfile:
            config.write(configfile)
        self.log_message(f"CertId {certId} saved to {os.path.join(directory, 'cert_info.ini')}")

    def certify(self, bin_path, selected_port):
        try:
            subprocess.run(["esptool.py", "-p", selected_port, "write_flash", "0x10000", bin_path], check=True)
        except subprocess.CalledProcessError as e:
            self.log_message(f"Error flashing cert: {e}")

    def update_status(self, certId):
        try:
            connection = self._connect_to_database()
            cursor = connection.cursor()
            query = "UPDATE device_info SET status = 0 WHERE matter_cert_id = %s"
            cursor.execute(query, (certId,))
            connection.commit()
            cursor.close()
            connection.close()
            self.log_message(f"Status for certId {certId} updated successfully.")
        except mysql.connector.Error as e:
            self.log_message(f"Error updating status in database: {e}")

    def flash_cert(self, port_var):
        certId = self.get_certId()
        selected_port = port_var.get()  # Retrieve the selected port from the Combobox
        if certId:
            bin_path = self.get_bin_path(certId)
            if bin_path:
                if selected_port:
                    self.log_message(f"Flashing cert {certId} on port {selected_port}...")
                    self.certify(bin_path, selected_port)
                    self.update_status(certId)
                    self.create_folder()    
                    self.log_message(f"Cert {certId} flashed successfully.")
                else:
                    self.log_message("No port selected. Please select a port before flashing.")
            else:
                self.log_message(f"No .bin file found for certId {certId}.")
        else:
            self.log_message("No available certId with status not true.")

    def get_bin_path(self, certId):
        for root, dirs, files in os.walk("/"):
            for file in files:
                if file.endswith(".bin") and certId in file:
                    return os.path.join(root, file)  # Return the path of the .bin file
        return None  # Return None if no .bin file with the certId is found

    def log_message(self, message):
        print(message)  # Replace this with your preferred logging mechanism
        self.log_message_callback(message)

# Example usage:
def log_callback(message):
    # Replace this with your logging mechanism
    print(message)

flash_cert_instance = FlashCert(log_callback)
# Use the flash_cert_instance to call methods like flash_cert(), etc.
