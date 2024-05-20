import os
import mysql.connector
import subprocess

# from serialCom.serialCom import SerialCom
# from updateDB.updateDB import UpdateDB

class FlashCert:
    
    # Function to retrieve a certId where status is not true
    def get_certId(self):
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="anuarrozman2303",
            password="Matter2303!",
            database="device_mac_sn"
        )

        cursor = connection.cursor()

        # Retrieve a certId where status is NULL or FALSE
        query = "SELECT matter_cert_id FROM device_info WHERE status IS NULL"
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return result[0]  # Return the certId
        else:
            return None  # Return None if no certId found

    # Function to get the path of the .bin file for the selected certId
    def get_bin_path(self, certId):
        for root, dirs, files in os.walk("/"):  # Walk through all files and directories in the current directory and its subdirectories
            for file in files:
                if file.endswith(".bin") and certId in file:  # Check if the file is a .bin file and contains the certId in its name
                    return os.path.join(root, file)  # Return the path of the .bin file
        return None  # Return None if no .bin file with the certId is found

    def flash_cert(self, port_var, port_var1):
        certId = self.get_certId()
        selected_port = port_var.get()  # Retrieve the selected port from the Combobox
        if certId:
            bin_path = self.get_bin_path(certId)
            if bin_path:
                if selected_port:  # Use the selected port obtained from the Combobox
                    print(f"Flashing cert {certId} on port {selected_port}...")
                    self.certify(bin_path, selected_port)  # Pass the selected port to the certify function
                    print(f"Cert {certId} flashed successfully.")
                    self.update_status(certId)  # Update status only if .bin file is found
                    self.log_message(f"Flashing cert {certId} on port {selected_port}...")
                    self.log_message(f"Cert {certId} flashed successfully.")
                    # create folder to store the flashed certId in text file
                    # get the serial_number from the same certId and name the folder as the serial number
                    # store the certId in the .ini file
                else:
                    self.log_message("No port selected. Please select a port before flashing.")
            else:
                self.log_message("No .bin file found for this certId.")
        else:
            self.log_message("No available certId with status not true.")
            
        # factory_port = port_var1.get()
        # self.open_serial_port(factory_port, 115200)
        
        # # Get s/n from db
        # get_serial_number = UpdateDB()
        # serial_number = get_serial_number.get_serial_number()
        # print(f"Serial number: {serial_number}")
        

    # Function to flash the .bin file onto the device
    def certify(self, bin_path, selected_port):
        subprocess.run(["esptool.py", "-p", selected_port, "write_flash", "0x10000", bin_path])
        
    def update_status(self, certId):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="anuarrozman2303",
                password="Matter2303!",
                database="device_mac_sn"
            )
            cursor = connection.cursor()
            query = "UPDATE device_info SET status = 0 WHERE matter_cert_id = %s"
            cursor.execute(query, (certId,))
            connection.commit()
        except mysql.connector.Error as e:
            self.log_message(f"Error updating status in database: {e}")
        finally:
            cursor.close()
            connection.close()
        
    def log_message(self, message):
        print(message)  # Replace this with your preferred logging mechanism