import serial
import logging
from threading import Thread
from components.updateDB.updateDB import UpdateDB
from threading import Lock
import time
import requests

logger = logging.getLogger(__name__)

exit_read_thread = False

class SerialCom:
    def __init__(self, status_label, status_label1, status_label2, status_label3, status_label4, status_label5, status_label6, status_label7, status_label8, status_label9, status_label10, status_label11, status_label12, status_label13, status_label14, status_label15, status_label16):
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
        self.status_label11 = status_label11
        self.status_label12 = status_label12
        self.status_label13 = status_label13
        self.status_label14 = status_label14
        self.status_label15 = status_label15
        self.status_label16 = status_label16
        self.update_db = UpdateDB()
        self.sensor_temp_variable = None
        self.sensor_humid_variable = None
        self.mac_address_variable = None
        self.product_name_variable = None
        self.serial_port = None
        self.read_thread = None
        self.button_flag = None
        self.device_factory_mode = False

    def reset_flag_device_factory_mode(self):
        self.device_factory_mode = False

    def open_serial_port(self, port_var, baud_var):
        global exit_read_thread
        exit_read_thread = False
        selected_port = port_var
        selected_baud = baud_var
        logger.debug(f"Opening port {selected_port} at {selected_baud} baud")
        print(f"Opening port {selected_port} at {selected_baud} baud")
        self.reset_flag_device_factory_mode()
        try:
            self.serial_port = serial.Serial(selected_port, selected_baud, timeout=1)
            logger.info(f"Opened port {selected_port} at {selected_baud} baud")
            print(f"Opened port {selected_port} at {selected_baud} baud")
            self.read_thread = Thread(target=self.read_serial_data)
            self.read_thread.start()
        except serial.SerialException as e:
            logger.error(f"Error opening serial port: {e}")
            print(f"Error opening serial port: {e}")

    def close_serial_port(self):
        logger.info(f"Close Serial Port")
        print(f"Close Serial Port")
        global exit_read_thread
        exit_read_thread = True
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                logger.debug("Close Port")
                print("Close Port")
            else:
                logger.debug("Port is not open.")
                print("Port is not open.")
        except serial.SerialException as e:
            logger.debug(f"Error closing serial port: {e}") 
            print(f"Error closing serial port: {e}")

    def read_serial_data(self):
        # while self.serial_port.is_open:
        factory_mode_counter = 0
        while True:
            try:

                if exit_read_thread == True:
                    logger.info("Exit Serial Com Loop")
                    print("Exit Serial Com Loop")
                    break

                raw_data = self.serial_port.readline()
                decoded_data = raw_data.decode("utf-8", errors='replace').strip()

                if decoded_data:
                    logger.debug(f"Received: {decoded_data}")
                    
                    if "." in decoded_data:
                        if (self.device_factory_mode == False) and (len(decoded_data) == 1):
                            logger.debug("Data contains '.'")
                            self.send_data_auto()
                            if factory_mode_counter == 0:
                                self.update_status_label("Pass", "green", ("Helvetica", 10, "bold"))
                                factory_mode_counter += 1
                            elif factory_mode_counter == 1:
                                self.update_status_label14("Pass", "green", ("Helvetica", 10, "bold"))
                                factory_mode_counter = 0
                    
                    if "3;MAC? = " in decoded_data:
                        self.device_factory_mode = True
                        if factory_mode_counter == 1:
                            self.update_status_label3("Pass", "green", ("Helvetica", 10, "bold"))
                            self.process_mac_address(decoded_data)

                    if "3;PRD? = " in decoded_data:
                        self.process_product_name(decoded_data)
                        # self.update_status_label5("Failed", "red", ("Helvetica", 10, "bold"))

                    # if "3;DID-" in decoded_data:
                    if "3;SRN? = " in decoded_data:
                        self.process_srn(decoded_data)
                        
                    if "3;MTQRS? = " in decoded_data:
                        self.process_mtqrs(decoded_data)

                    if "3;saveDevData" in decoded_data:
                        self.process_savedevdata(decoded_data)
                        
                    if "3;sensorTemp? = " in decoded_data:
                        self.process_sensor_temperature(decoded_data)
                    
                    if "3;sensorHumi? = " in decoded_data:
                        self.process_sensor_humidity(decoded_data)
                    
                    if "3;test_buttonshort = pressed" in decoded_data:
                        # self.status_label4.config(text="Pass")
                        self.update_status_label4("Pass", "green", ("Helvetica", 10, "bold"))
                        self.button_flag = True

                    if "3;test_buttonlong = pressed" in decoded_data:
                        # self.status_label4.config(text="Pass")
                        self.update_status_label4("Failed", "red", ("Helvetica", 10, "bold"))

                    if "3;irdevconf? = " in decoded_data:
                        self.process_ir_definition(decoded_data)
                        self.update_status_label5("Pass", "green", ("Helvetica", 10, "bold"))

                    if "3;resetDevice" in decoded_data or "3;factoryRST" in decoded_data:
                        self.update_status_label15("Pass", "green", ("Helvetica", 10, "bold"))

                    if "3;RSSI? = " in decoded_data:
                        print("RSSI: ")
                        print(decoded_data)
                        self.process_wifi_rssi(decoded_data)

            except UnicodeDecodeError as decode_error:
                logger.error(f"Error decoding data: {decode_error}")
                print(f"Error decoding data: {decode_error}")
            except Exception as e:
                logger.error(f"Exception in read_serial_data: {e}")
                print(f"Exception in read_serial_data: {e}")
        logger.info(f"Serial Com Thread End")
        print(f"Serial Com Thread End")

    def get_button_flag(self):
        return self.button_flag
        
    def process_mac_address(self, decoded_data):
        mac_address = decoded_data.split("=")[1].strip()
        self.mac_address_variable = mac_address
        logger.info(f"SerialCom, MAC Address: {mac_address}")
        print(f"SerialCom, MAC Address: {mac_address}")
        # self.update_db.update_text_file(self.mac_address_variable) # Temporary block this code
        # logger.info(f"MAC Address done")
        # self.status_label3.config(text="Success")
        # self.update_status_label3("Pass", "green", ("Helvetica", 10, "bold"))
        self.update_status_label7(f"{self.mac_address_variable}", "black", ("Helvetica", 10, "italic"))
        self.mac_address_variable = ""
        
    def process_product_name(self, decoded_data):
        product_name = decoded_data.split("=")[1].strip()
        self.product_name_variable = product_name
        logger.info(f"SerialCom, Product Name: {product_name}")
        print(f"SerialCom, Product Name: {product_name}")
        # self.update_status_label6("Pass", "green", ("Helvetica", 10, "bold"))
        self.update_status_label8(f"{self.product_name_variable}", "black", ("Helvetica", 10, "italic"))
        self.product_name_variable = ""
        
    def process_srn(self, decoded_data):
        srn = decoded_data.split("=")[1].strip()
        # logger.info(f"DID: {did}")
        logger.info(f"SerialCom, Serial Number: {srn}")
        print(f"SerialCom, Serial Number: {srn}")
        self.update_status_label9(f"{srn}", "black", ("Helvetica", 10, "italic"))
        
    def process_mtqrs(self, decoded_data):
        mtqrs = decoded_data.split("=", 1)[1].strip()
        logger.info(f"SerialCom, Matter QR String: {mtqrs}")
        print(f"SerialCom, Matter QR String: {mtqrs}")
        self.update_status_label10(f"{mtqrs}", "black", ("Helvetica", 10, "italic"))

    def process_savedevdata(self, decoded_data):
        savedevicedata = decoded_data.split(";", 1)[1].strip()
        logger.info(f"SerialCom, Save Device Data: {savedevicedata}")
        print(f"SerialCom, Save Device Data: {savedevicedata}")
        self.update_status_label12(f"{savedevicedata}", "black", ("Helvetica", 10, "italic"))

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

    def process_ir_definition(self, decoded_data):
        ir_def = decoded_data.split("=")[1].strip()
        logger.info(f"Serial Com, Read IR Definition: {ir_def} %")
        print(f"Serial Com, Read IR Definition: {ir_def} %")

    def process_wifi_rssi(self, decoded_data):
        wifi_rssi = decoded_data.split("=")[1].strip()
        logger.info(f"Serial Com, Read WiFi RSSI: {wifi_rssi} dBm")
        print(f"Serial Com, Read WiFi RSSI: {wifi_rssi} dBm")
        self.update_status_label16(f"{wifi_rssi} dBm", "black", ("Helvetica", 10, "bold"))


    def save_sensor_temp_variable(self):
        try:
            with open('sensor.txt', 'w') as file:
                file.write(f"ATBeam Temperature: {self.sensor_temp_variable}\n")
                # self.status_label1.config(text=f"{self.sensor_temp_variable} C")
                self.update_status_label1(f"{self.sensor_temp_variable} °C", "black", ("Helvetica", 10, "italic"))
            logger.info(f"SerialCom, Device Temparature Reading '{self.sensor_temp_variable}' written to file 'sensor.txt'")
            print(f"SerialCom, Device Temparature Reading '{self.sensor_temp_variable}' written to file 'sensor.txt'")
        except Exception as e:
            logger.error(f"Error writing to file: {e}")
            print(f"Error writing to file: {e}")
            # self.status_label1.config(text="Failed")
            # self.update_status_label1("Failed", "red", ("Helvetica", 10, "bold"))

    def save_sensor_humid_variable(self):
        try:
            with open('sensor.txt', 'a') as file:
                file.write(f"ATBeam Humidity: {self.sensor_humid_variable}\n")
                # self.status_label2.config(text=f"{self.sensor_humid_variable} %")
                self.update_status_label2(f"{self.sensor_humid_variable} %", "black", ("Helvetica", 10, "italic"))
            logger.debug(f"SerialCom, Device Humidity Reading '{self.sensor_humid_variable}' written to file 'sensor.txt'")
            print(f"SerialCom, Device Humidity Reading '{self.sensor_humid_variable}' written to file 'sensor.txt'")
        except Exception as e:
            logger.error(f"Error writing to file: {e}")
            print(f"Error writing to file: {e}")
            # self.status_label2.config(text="Failed")
            # self.update_status_label2("Failed", "red", ("Helvetica", 10, "bold"))

    def send_data_auto(self):
        auto_data = "polyaire&ADT\r\n"
        # self.status_label.config(text="Success")
        # self.update_status_label("Pass", "green", ("Helvetica", 10, "bold"))
        if self.serial_port.is_open:
            self.serial_port.write(auto_data.encode())
            logger.debug(f"SerialCom, Factory: {auto_data}")
            print(f"SerialCom, Factory: {auto_data}")
        else:
            # self.status_label.config(text="Failed")
            # self.update_status_label("Failed", "red", ("Helvetica", 10, "bold"))
            logger.debug(f"Serial Port is closed")
            print(f"Serial Port is closed")
            
    # In Progress: Retrieve Device IP Address
    # URL = http://<device_ip>/getDeviceState
    def http_response(self):
        print("HTTP Response")
        url = 'http://192.168.0.44:5000/getDeviceState'
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
            print("Success")
            print("Response JSON: ")
            print(json_data)
            
            temp = json_data['data']['temp']
        else:
            print(f"Failed to retrieve data. HTTP status code: {response.status_code}")

    def update_status_label(self, message, fg, font): #Update factory mode label
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

    def update_status_label11(self, message, fg, font):
        self.status_label11.config(text=message, fg=fg, font=font)

    def update_status_label12(self, message, fg, font):
        self.status_label12.config(text=message, fg=fg, font=font)

    def update_status_label13(self, message, fg, font):
        self.status_label13.config(text=message, fg=fg, font=font)

    def update_status_label14(self, message, fg, font):
        self.status_label14.config(text=message, fg=fg, font=font)

    def update_status_label15(self, message, fg, font):
        self.status_label15.config(text=message, fg=fg, font=font)

    def update_status_label16(self, message, fg, font):
        self.status_label16.config(text=message, fg=fg, font=font)

    def get_status_label_text(self):
        return self.status_label.cget("text")
    
    def get_status_label1_text(self):
        return self.status_label1.cget("text")
    
    def get_status_label2_text(self):
        return self.status_label2.cget("text")
    
    def get_status_label3_text(self):
        return self.status_label3.cget("text")
    
    def get_status_label4_text(self):
        return self.status_label4.cget("text")
    
    def get_status_label5_text(self):
        return self.status_label5.cget("text")
    
    def get_status_label6_text(self):
        return self.status_label6.cget("text")
    
    def get_status_label7_text(self):
        return self.status_label7.cget("text")
    
    def get_status_label8_text(self):
        return self.status_label8.cget("text")
    
    def get_status_label9_text(self):
        return self.status_label9.cget("text")
    
    def get_status_label10_text(self):
        return self.status_label10.cget("text")
    
    def get_status_label11_text(self):
        return self.status_label11.cget("text")
    
    def get_status_label12_text(self):
        return self.status_label12.cget("text")
    
    def get_status_label13_text(self):
        return self.status_label13.cget("text")
    
    def get_status_label14_text(self):
        return self.status_label14.cget("text")
    
    def get_status_label15_text(self):
        return self.status_label15.cget("text")
    
    def get_status_label16_text(self):
        return self.status_label16.cget("text")




