import subprocess
import mysql.connector
import requests

class ToolsBar:
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
            self.create_table_if_not_exists()  # Ensure table exists before inserting data
            self.insert_data(data)
            self.display_data(data)
        except Exception as e:
            self.log_message("Error downloading data: " + str(e))
    
    def create_table_if_not_exists(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="anuarrozman2303",
                password="Matter2303!",
                database="device_mac_sn"
            )
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS device_info (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    matter_cert_id VARCHAR(255),
                    serial_number VARCHAR(255),
                    mac_address VARCHAR(255),
                    status VARCHAR(255) DEFAULT NULL
                )
            """)
            conn.commit()
            self.log_message("Ensured that the table device_info exists.")
        except mysql.connector.Error as e:
            self.log_message(f"Error creating table: {e}")
        finally:
            cursor.close()
            conn.close()

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
            
    def display_data(self, data):
        for device in data:
            matter_cert_id = device.get("matter_cert_id", "N/A")
            serial_number = device.get("serial_number", "N/A")  # Correct field name
            self.log_message(f"Matter Cert ID: {matter_cert_id}, Serial: {serial_number}")
        self.log_message("Data downloaded successfully!")
        
    def log_message(self, message):
        print(message)  # Replace this with your preferred logging mechanism
