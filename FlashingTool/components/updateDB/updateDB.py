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
                # Insert the MAC address into the database if it doesn't exist
                sql_query = """
                            UPDATE device_info SET mac_address = %s, status = 1
                            WHERE status = 0;
                            """
                cursor.execute(sql_query, (mac_address,))
                connection.commit()
                print("MAC address inserted into the database.")

        except mysql.connector.Error as error:
            print("Failed to update database:", error)

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection closed.")
