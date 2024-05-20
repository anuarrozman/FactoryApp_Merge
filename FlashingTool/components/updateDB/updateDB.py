import mysql.connector

class UpdateDB:
    
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
                
    def get_serial_number(self):
        try:
            connection = mysql.connector.connect(
        host="localhost",
        user="anuarrozman2303",
        password="Matter2303!",
        database="device_mac_sn"
            )
            
            cursor = connection.cursor()

            # Retrieve the serial number from the database
            cursor.execute("SELECT serial_number FROM device_info WHERE status = '0'")
            result = cursor.fetchone()
            serial_number = result[0] if result else None

            return serial_number
        except mysql.connector.Error as error:
            print("Failed to get serial number:", error)
            
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection closed.")