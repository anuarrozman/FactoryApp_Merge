import serial
import logging
from threading import Thread
from components.updateDB.updateDB import UpdateDB
from threading import Lock
import time

logger = logging.getLogger(__name__)

class SerialCom:
    def __init__(self, status_label, status_label1, status_label2, status_label3, status_label4, status_label5, status_label6, status_label7, status_label8, status_label9, status_label10):
        self.status_label = status_label
        self.status_label1 = status_label1
        self.status_label2 = status_label2
        self.status_label3 = status_label3
        self.status_label4 = status_label4
        self.status_label5 = status_label5
        self.status_label6 = status_label6
        self.status_label7 = status_label7
        self.status_label8 = status_label8
        self.status_label9 = status_label9
        self.status_label10 = status_label10
        self.update_db = UpdateDB()
        self.sensor_temp_variable = None
        self.sensor_humid_variable = None
        self.mac_address_variable = None
        self.product_name_variable = None
        self.serial_port = None
        self.read_thread = None
        self.button_flag = None
        self.device_factory_mode = None

    def open_serial_port(self, port_var, baud_var):
        self.device_factory_mode = False
        selected_port = port_var
        selected_baud = baud_var
        logger.debug(f"Opening port {selected_port} at {selected_baud} baud")
        try:
            self.serial_port = serial.Serial(selected_port, selected_baud, timeout=1)
            logger.info(f"Opened port {selected_port} at {selected_baud} baud")
            
            self.read_thread = Thread(target=self.read_serial_data)
            self.read_thread.start()
        except serial.SerialException as e:
            logger.error(f"Error opening serial port: {e}")

    def close_serial_port(self):
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                logger.debug("Closed port")
            else:
                logger.debug("Port is not open.")
        except serial.SerialException as e:
            logger.debug(f"Error closing serial port: {e}") 

    def read_serial_data(self):
        while self.serial_port.is_open:
            try:
                raw_data = self.serial_port.readline()
                decoded_data = raw_data.decode("utf-8", errors='replace').strip()

                if decoded_data:
                    logger.debug(f"Received: {decoded_data}")
                    
                    if "." in decoded_data:
                        if self.device_factory_mode == False:
                            logger.debug("Data contains '.'")
                            self.send_data_auto()
                    
                    if "3;MAC? = " in decoded_data:
                        self.device_factory_mode = True
                        self.update_status_label("Pass", "green", ("Helvetica", 12, "bold"))
                        self.process_mac_address(decoded_data)
                        
                    if "3;sensorTemp? = " in decoded_data:
                        self.process_sensor_temperature(decoded_data)
                    
                    if "3;sensorHumi? = " in decoded_data:
                        self.process_sensor_humidity(decoded_data)
                    
                    if "3;test_buttonshort = pressed" in decoded_data:
                        # self.status_label4.config(text="Pass")
                        self.update_status_label4("Pass", "green", ("Helvetica", 12, "bold"))
                        self.button_flag = True

                    if "3;irdevconf" in decoded_data:
                        self.update_status_label5("Pass", "green", ("Helvetica", 12, "bold"))
                        
                    if "3;PRD? = " in decoded_data:
                        self.process_product_name(decoded_data)
                        # self.update_status_label5("Failed", "red", ("Helvetica", 12, "bold"))
                    
                    if "3;DID-" in decoded_data:
                        self.process_did(decoded_data)
                        
                    if "3;MTQR-" in decoded_data:
                        self.process_mtqr(decoded_data)

            except UnicodeDecodeError as decode_error:
                logger.error(f"Error decoding data: {decode_error}")
            except Exception as e:
                logger.error(f"Exception in read_serial_data: {e}")

    def get_button_flag(self):
        return self.button_flag
        
    def process_mac_address(self, decoded_data):
        mac_address = decoded_data.split("=")[1].strip()
        self.mac_address_variable = mac_address
        logger.info(f"MAC Address: {mac_address}")
        
        self.update_db.update_text_file(self.mac_address_variable)
        # self.status_label3.config(text="Success")
        self.update_status_label3("Pass", "green", ("Helvetica", 12, "bold"))
        self.update_status_label8(f"{self.mac_address_variable}", "black", ("Helvetica", 12, "italic"))
        self.mac_address_variable = ""
        
    def process_product_name(self, decoded_data):
        product_name = decoded_data.split("=")[1].strip()
        self.product_name_variable = product_name
        logger.info(f"Product Name: {product_name}")
        self.update_status_label6("Pass", "green", ("Helvetica", 12, "bold"))
        self.update_status_label7(f"{self.product_name_variable}", "black", ("Helvetica", 12, "italic"))
        self.product_name_variable = ""
        
    def process_did(self, decoded_data):
        did = decoded_data.split("-")[1].strip()
        logger.info(f"DID: {did}")
        self.update_status_label9(f"{did}", "black", ("Helvetica", 12, "italic"))
        
    def process_mtqr(self, decoded_data):
        mtqr = decoded_data.split("-")[1].strip()
        logger.info(f"MTQR: {mtqr}")
        self.update_status_label10(f"{mtqr}", "black", ("Helvetica", 12, "italic"))

    def process_sensor_temperature(self, decoded_data):
        sensor_temp = decoded_data.split("=")[1].strip()
        self.sensor_temp_variable = sensor_temp
        logger.info(f"{self.sensor_temp_variable} C")
        self.save_sensor_temp_variable()

    def process_sensor_humidity(self, decoded_data):
        sensor_humid = decoded_data.split("=")[1].strip()
        self.sensor_humid_variable = sensor_humid
        logger.info(f"{sensor_humid} %")
        self.save_sensor_humid_variable()

    def save_sensor_temp_variable(self):
        try:
            with open('sensor.txt', 'w') as file:
                file.write(f"ATBeam Temperature: {self.sensor_temp_variable}\n")
                # self.status_label1.config(text=f"{self.sensor_temp_variable} C")
                self.update_status_label1(f"{self.sensor_temp_variable} C", "black", ("Helvetica", 12, "italic"))
            logger.debug(f"Value '{self.sensor_temp_variable}' written to file 'sensor.txt'")
        except Exception as e:
            logger.error(f"Error writing to file: {e}")
            # self.status_label1.config(text="Failed")
            self.update_status_label1("Failed", "red", ("Helvetica", 12, "bold"))

    def save_sensor_humid_variable(self):
        try:
            with open('sensor.txt', 'a') as file:
                file.write(f"ATBeam Humidity: {self.sensor_humid_variable}\n")
                # self.status_label2.config(text=f"{self.sensor_humid_variable} %")
                self.update_status_label2(f"{self.sensor_humid_variable} %", "black", ("Helvetica", 12, "italic"))
            logger.debug(f"Value '{self.sensor_humid_variable}' written to file 'sensor.txt'")
        except Exception as e:
            logger.error(f"Error writing to file: {e}")
            # self.status_label2.config(text="Failed")
            self.update_status_label2("Failed", "red", ("Helvetica", 12, "bold"))

    def send_data_auto(self):
        auto_data = "polyaire&ADT\r\n"
        # self.status_label.config(text="Success")
        # self.update_status_label("Pass", "green", ("Helvetica", 12, "bold"))
        if self.serial_port.is_open:
            self.serial_port.write(auto_data.encode())
            logger.debug(f"Sending automatic data: {auto_data}")
        else:
            # self.status_label.config(text="Failed")
            self.update_status_label("Failed", "red", ("Helvetica", 12, "bold"))

    def update_status_label(self, message, fg, font):
        self.status_label.config(text=message, fg=fg, font=font)  # Update the status label with the message

    def update_status_label1(self, message, fg, font):
        self.status_label1.config(text=message, fg=fg, font=font)  # Update the status label with the message

    def update_status_label2(self, message, fg, font):
        self.status_label2.config(text=message, fg=fg, font=font)  # Update the status label with the message

    def update_status_label3(self, message, fg, font):
        self.status_label3.config(text=message, fg=fg, font=font)  # Update the status label with the message

    def update_status_label4(self, message, fg, font):
        self.status_label4.config(text=message, fg=fg, font=font)  # Update the status label with the message
        
    def update_status_label5(self, message, fg, font):
        self.status_label5.config(text=message, fg=fg, font=font)  # Update the status label with the message
        
    def update_status_label6(self, message, fg, font):
        self.status_label6.config(text=message, fg=fg, font=font)
        
    def update_status_label7(self, message, fg, font):
        self.status_label7.config(text=message, fg=fg, font=font)
        
    def update_status_label8(self, message, fg, font):
        self.status_label8.config(text=message, fg=fg, font=font)
        
    def update_status_label9(self, message, fg, font):
        self.status_label9.config(text=message, fg=fg, font=font)
        
    def update_status_label10(self, message, fg, font):
        self.status_label10.config(text=message, fg=fg, font=font)




