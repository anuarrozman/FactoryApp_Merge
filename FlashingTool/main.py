import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from tkinter.filedialog import askopenfilename
import serial.tools.list_ports
import os
from tkinter import messagebox
from cryptography.fernet import Fernet
import configparser
import time
import threading
import logging
import concurrent.futures
import shutil

from datetime import datetime
from components.settingWindow.settingWindow import SettingApp
from components.toolsBar.toolsBar import ToolsBar
from components.flashFirmware.flashFirmware import FlashFirmware
from components.flashCert.flashCert import FlashCert
from components.serialCom.serialCom import SerialCom
from components.writeDevInfo.writeDeviceInfo import WriteDeviceInfo
from components.dmmReader.multimeter import Multimeter
from components.dmmReader.dmmReader import DeviceSelectionApp
from components.dmmReader.ut61eplus import UT61EPLUS
from components.adminLoginWindow.adminLoginWindow import AdminLoginApp
from components.manualTest.manualTest import ManualTestApp
from components.uploadReport import uploadReport
from components.loadTestScript.loadTestScript import LoadTestScript
from components.aht20Sensor.aht20Sensor import SensorLogger
# from components.servoControl.servoControl import ServoController
from components.processOrderNumber.processOrderNumber import get_order_numbers
from components.readOrderFile.readOrderFile import parse_order_file
# from components.rebootPinS3.rebootPinS3 import RebootPinS3
from components.loggingReport.loggingReport import setup_logging
from components.wifiDriver.wifiDriver import scan_wifi_networks, run_iwconfig
from components.sendToPrinter import sendToPrinterFunc

logger = logging.getLogger(__name__)

script_dir = os.path.dirname(__file__)

factroy_app_version = ""

formatted_date = ""
formatted_time = ""

logs_file_name = "factory_app"
logs_file_extension = ".log"
logs_dir_name = "logs"
logs_dir = str(script_dir) + "/" + str(logs_dir_name)

ini_file_name = "testscript.ini"

device_data_file_name = "device_data.txt"
device_data_file_path = str(script_dir) + "/" + str(device_data_file_name)

device_data = ""

orderNum_label = ""
macAddress_label = ""
serialID_label = ""
certID_label = ""
secureCertPartition_label = ""
commissionableDataPartition_label = ""
qrCode_label = ""
manualCode_label = ""
discriminator_label = ""
passcode_label = ""

orderNum_data = ""
macAddress_esp32s3_data = ""
serialID_data = ""
certID_data = ""
secureCertPartition_data = ""
commissionableDataPartition_data = ""
qrCode_data = ""
manualCode_data = ""
discriminator_data = ""
passcode_data = ""

available_com_ports = []

file_path = '/usr/src/app/FactoryApp_Merge/FlashingTool/device_data.txt'  # Specify the correct path to your text file
# file_path = '/home/anuarrozman/Airdroitech/ATSoftwareDevelopmentTool/FlashingTool/device_data.txt'
# file_path = '/home/anuarrozman2303/Airdroitech/FactoryApp/device_data.txt'
orders = parse_order_file(device_data_file_path)
order_numbers = get_order_numbers(orders)
qrcode = None
manualcode = None

break_printer = None

class SerialCommunicationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Communication App")
        self.root.attributes('-zoomed', True)
        # self.root.attributes('-fullscreen', True)
        self.root.resizable(True, True)

        # Serial port configuration
        self.serial_port = None
        self.task1_thread = None
        self.task2_thread = None
        self.task1_completed = threading.Event()
        self.task1_thread_failed = threading.Event()
        self.stop_event = threading.Event()
        self.selected_port = ""
        self.step_delay = 3
        self.long_delay = 5
        self.manual_test = False
        self.factory_flag = None
        self.used_cert_ids = set()
        self.selected_cert_id = None
        self.current_set = 0
        self.button_sets = []

        #self.configure_logging()

        # Create GUI elements
        self.initialize_gui()

        # Initialize components
        self.initialize_components()

        # Store reference to the Manual Test menu item
        self.manual_test_menu = None
        # self.task1_completed = threading.Event() #duplicate with above declaration, soo

    def initialize_logging(self, mac_address, serialID):
        global formatted_date
        global formatted_time

        if not mac_address:
            return True

        # Configure logging
        log_file_name = logs_dir + "/" + logs_file_name + '_' + str(mac_address) + '_' + str(serialID) + '_' + str(formatted_date) + '_' + str(formatted_time) + logs_file_extension
        print(str(log_file_name))
        logging.basicConfig(
            filename=str(log_file_name),  # Name of the log file
            level=logging.DEBUG,  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return False

    def initialize_gui(self):
        global factroy_app_version
        self.create_menubar()
        self.create_widgets()
        # self.create_text_widgets()

        factroy_app_version = self.read_version_from_file("version.txt")  # Read version from file
        self.add_version_label(factroy_app_version)  # Add version number here
        print("initialize gui done")

    def initialize_components(self):

        # file_path = '/usr/src/app/ATSoftwareDevelopmentTool/FlashingTool/device_data.txt'
        # file_path = '/home/anuarrozman/Airdroitech/ATSoftwareDevelopmentTool/FlashingTool/device_data.txt'
        self.toolsBar = ToolsBar()
        self.flashFw = FlashFirmware(self.result_flashing_fw_label, self.result_flashing_fw_h2_label, self.result_mac_address_s3_label, self.result_mac_address_h2_label) #(self.receive_text)
        self.flashCert = FlashCert(self.result_flashing_cert_label) #(self.log_message)
        self.serialCom = SerialCom(self.result_factory_mode_label, self.atbeam_temp_value, self.atbeam_humid_value, self.result_read_device_mac, self.result_button_label, self.result_ir_def_label, self.result_read_prod_name, self.read_device_mac, self.read_prod_name, self.read_device_sn, self.read_device_mtqr, self.result_save_device_data_label, self.read_save_device_data_label, self.result_ir_rx_label, self.result_group2_factory_mode, self.result_factory_reset, self.result_group2_wifi_station_rssi) #self.atbeam_sensor_temp_update) #(self.receive_text)

        self.sendEntry = WriteDeviceInfo(self.send_command, self.result_write_serialnumber, self.result_write_mtqr) #, self.log_message)
        self.dmmReader = DeviceSelectionApp(self.dmm_frame, self.input_3_3V_dmm, self.input_5V_dmm)
        self.multimeter = Multimeter()
        # self.rebootPin = RebootPinS3()
        # self.aht20Sensor = SensorLogger()
        # self.servo_controller = ServoController()
        print("initialize components done")

    def read_temp_aht20(self):
        # ext_sensor = self.aht20Sensor.read_temp_sensor()
        ext_sensor = 25.0
        logger.debug(f"External Temperature: {ext_sensor}")
        print(f"External Temperature: {ext_sensor}")
        self.ext_temp_value.config(text=f"{ext_sensor} °C", fg="black", font=("Helvetica", 10, "normal"))
        # self.get_atbeam_temp()
        # time.sleep(1)
        range = self.range_temp_value.cget("text")
        self.compare_temp(ext_sensor, self.serialCom.sensor_temp_variable, float(range.strip()))

        time.sleep(2)
        # atbeam_temp = self.serialCom.sensor_temp_variable
        atbeam_temp = self.atbeam_temp_value.cget("text")
        atbeam_temp = atbeam_temp.split(' ')[0]
        atbeam_temp = float(atbeam_temp)
        logger.info(f"ATBeam Temperature: {atbeam_temp}")
        print(f"ATBeam Temperature: {atbeam_temp}")

        # self.get_atbeam_temp()
        # time.sleep(1)
        range = self.range_temp_value.cget("text")
        range = float(range.strip())
        logger.info(f"Temperature Range: {range}")
        print(f"Temperature Range: {range}")

        if abs(ext_sensor - atbeam_temp) <= float(range):
            logger.info(f"Temperature is within ±{range} range")
            print(f"Temperature is within ±{range} range")
            self.result_temp_label.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
        else:
            logger.info(f"Temperature is out of ±{range} range")
            print(f"Temperature is out of ±{range} range")
            self.result_temp_label.config(text=f"Failed", fg="red", font=("Helvetica", 10, "bold"))
        # self.compare_temp(ext_sensor, self.serialCom.sensor_temp_variable, float(range.strip()))
        # pass

    def get_atbeam_temp(self):
        command = "FF:3;sensorTemp?\r\n"
        self.send_command(command)

    def compare_temp(self, ext_sensor, atbeam_temp, test_temperature_range):
        try:
            with open('sensor.txt', 'r') as file:
                for line in file:
                    if "ATBeam Temperature:" in line:
                        ext_sensor = float(ext_sensor)
                        atbeam_temp = line.split(":")[1].strip()
                        atbeam_temp = float(atbeam_temp)
                        logger.info(f"ATBeam Temperature: {atbeam_temp}")
                        print(f"ATBeam Temperature: {atbeam_temp}")
                        logger.info(f"External Temperature: {ext_sensor}")
                        print(f"External Temperature: {ext_sensor}")
                        if ext_sensor == atbeam_temp:
                            logger.info("Temperature matches")
                            print("Temperature matches")
                            self.result_temp_label.config(text=f"Pass", fg="green", font=("Helvetica", 10, "bold"))
                        if abs(ext_sensor - atbeam_temp) <= float(test_temperature_range):
                            logger.info(f"Temperature is within ±{test_temperature_range} range")
                            print(f"Temperature is within ±{test_temperature_range} range")
                            self.result_temp_label.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                        else:
                            logger.info(f"Temperature is out of ±{test_temperature_range} range")
                            print(f"Temperature is out of ±{test_temperature_range} range")
                            self.result_temp_label.config(text=f"Failed", fg="red", font=("Helvetica", 10, "bold"))
        except FileNotFoundError:
            logger.error("File not found")
            print("File not found")

    def read_humid_aht20(self):
        # ext_sensor = self.aht20Sensor.read_humid_sensor()
        ext_sensor = 50.5
        logger.debug(f"External Humidity: {ext_sensor}")
        self.ext_humid_value.config(text=f"{ext_sensor} %", fg="black", font=("Helvetica", 10, "normal"))
        # self.get_atbeam_humid()
        # time.sleep(1)
        range = self.range_humid_value.cget("text")
        self.compare_humid(ext_sensor, self.serialCom.sensor_humid_variable, float(range.strip()))
        # pass

        time.sleep(2)
        atbeam_humid = self.serialCom.sensor_humid_variable
        atbeam_humid = self.atbeam_humid_value.cget("text")
        atbeam_humid = atbeam_humid.split(' ')[0]
        atbeam_humid = float(atbeam_humid)
        logger.info(f"ATBeam Humidity: {atbeam_humid}")
        print(f"ATBeam Humidity: {atbeam_humid}")


        # self.get_atbeam_humid()
        # time.sleep(1)
        range = self.range_humid_value.cget("text")
        range = float(range.strip())
        logger.info(f"Humidity Range: {range}")
        print(f"Humidity Range: {range}")

        if abs(ext_sensor - atbeam_humid) <= float(range): # humid range
            logger.info(f"Humidity is within ±{range} range")
            print(f"Humidity is within ±{range} range")
            self.result_humid_label.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
        else:
            logger.info(f"Humidity is out of ±{range} range")
            print(f"Humidity is out of ±{range} range")
            self.result_humid_label.config(text=f"Failed", fg="red", font=("Helvetica", 10, "bold"))
        # self.compare_humid(ext_sensor, self.serialCom.sensor_humid_variable, float(range.strip()))
        # pass

    def get_atbeam_humid(self):
        command = "FF:3;sensorHumi?\r\n"
        self.send_command(command)

    def compare_humid(self, ext_sensor, atbeam_humid, test_humidity_range):
        try:
            with open('sensor.txt', 'r') as file:
                for line in file:
                    if "ATBeam Humidity:" in line:
                        ext_sensor = float(ext_sensor)
                        atbeam_humid = line.split(":")[1].strip()
                        atbeam_humid = float(atbeam_humid)
                        logger.info(f"ATBeam Humidity: {atbeam_humid}")
                        print(f"ATBeam Humidity: {atbeam_humid}")
                        logger.info(f"External Humidity: {ext_sensor}")
                        print(f"External Humidity: {ext_sensor}")
                        if ext_sensor == atbeam_humid:
                            logger.info("Humidity matches")
                            print("Humidity matches")
                            self.result_humid_label.config(text=f"Pass", fg="green", font=("Helvetica", 10, "bold"))
                        elif abs(ext_sensor - atbeam_humid) <= float(test_humidity_range): # humid range
                            logger.info(f"Humidity is within ±{test_humidity_range} range")
                            print(f"Humidity is within ±{test_humidity_range} range")
                            self.result_humid_label.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                        else:
                            logger.info(f"Humidity is out of ±{test_humidity_range} range")
                            print(f"Humidity is out of ±{test_humidity_range} range")
                            self.result_humid_label.config(text=f"Failed", fg="red", font=("Helvetica", 10, "bold"))
        except FileNotFoundError:
            logger.error("File not found")
            print("File not found")

    def isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def dmm_reader_3_3V_value_manual(self, dmm_value):
        self.submit_3_3V_dmm.config(state=tk.DISABLED)
        dmm_manual_input = dmm_value.get()
        range_value_input = self.range_value_3_3V_dmm.cget("text")
        logger.debug(f"Manual 3.3V DMM Value: {dmm_manual_input}")
        print(f"Manual 3.3V DMM Value: {dmm_manual_input}")
        logger.debug(f"Manual 3.3V Test Range Value: {range_value_input}")
        print(f"Manual 3.3V Test Range Value: {range_value_input}")
        self.dmm_3_3V_reader.config(text=f"{dmm_manual_input} V", fg="black", font=("Helvetica", 10, "bold"))

        # if isinstance(dmm_manual_input, (int, float)):
        if dmm_manual_input.isdigit() or self.isfloat(dmm_manual_input):
            logger.info(f"'dmm_manual_input' is numeric")
            print(f"'dmm_manual_input' is numeric")
            if (3.3 - float(range_value_input)) <= float(dmm_manual_input) <= (3.3 + float(range_value_input)):
                self.result_3_3v_test.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
            else:
                self.result_3_3v_test.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        else:
            logger.info(f"'dmm_manual_input' is not numeric")
            print(f"'dmm_manual_input' is not numeric")
            self.result_3_3v_test.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))

    def dmm_reader_5V_value_manual(self, dmm_value):
        self.submit_5V_dmm.config(state=tk.DISABLED)
        dmm_manual_input = dmm_value.get()
        range_value_input = self.range_value_5V_dmm.cget("text")
        logger.debug(f"Manual 5V DMM Value: {dmm_manual_input}")
        print(f"Manual 5V DMM Value: {dmm_manual_input}")
        logger.debug(f"Manual 5V Test Range Value: {range_value_input}")
        print(f"Manual 5V Test Range Value: {range_value_input}")
        self.dmm_5V_reader.config(text=f"{dmm_manual_input} V", fg="black", font=("Helvetica", 10, "bold"))

        # if isinstance(dmm_manual_input, (int, float)):
        if dmm_manual_input.isdigit() or self.isfloat(dmm_manual_input):
            logger.info(f"'dmm_manual_input' is numeric")
            print(f"'dmm_manual_input' is numeric")
            if (5.0 - float(range_value_input)) <= float(dmm_manual_input) <= (5.0 + float(range_value_input)):
                self.result_5v_test.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
            else:
                self.result_5v_test.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        else:
            logger.info(f"'dmm_manual_input' is not numeric")
            print(f"'dmm_manual_input' is not numeric")
            self.result_5v_test.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))

    def wifi_scanning(self, test_range):
        global qrCode_data
        if qrCode_data != "":
            mtqr_wifi = self.read_device_mtqr.cget("text")
            mtqr_wifi_name = f"AT-{mtqr_wifi}"
            logger.info(f"Device Wi-Fi Soft AP Development: {mtqr_wifi_name}")
            print(f"Device Wi-Fi Soft AP Name 1: {mtqr_wifi_name}")
            device_wifi_softap_name1 = f"AT-{qrCode_data}" #This is the same name use above "mtqr_wifi_name"
            logger.info(f"Device Wi-Fi Soft AP Name 1: {device_wifi_softap_name1}")
            print(f"Device Wi-Fi Soft AP Name 1: {device_wifi_softap_name1}")
            string = str(qrCode_data)
            last_six_character = string[-6:]
            device_wifi_softap_name2 = f"AT BEAM {last_six_character}"
            logger.info(f"Device Wi-Fi Soft AP Name 2: {device_wifi_softap_name2}")
            print(f"Device Wi-Fi Soft AP Name 2: {device_wifi_softap_name2}")
            logger.info(f"Wi-Fi Soft AP RSSI Test Range: {test_range}")
            print(f"Wi-Fi Soft AP RSSI Test Range: {test_range}")
            wifi_networks = scan_wifi_networks()
            if wifi_networks:
                print("Available WiFi networks:")
                for network in wifi_networks:
                    ssid = network.get('SSID', 'Unknown')
                    signal_level = network.get('Signal_Level', 'N/A')
                    # print(f"SSID: {ssid}, Signal Level: {signal_level}")
                    if ssid == mtqr_wifi_name:
                        logger.info(f"Target network found: SSID: {ssid}, Signal Level: {signal_level}")
                        print(f"Target network found: SSID: {ssid}, Signal Level: {signal_level}")
                        self.result_group2_wifi_softap_ssid.config(text=f"{ssid}", fg="black", font=("Helvetica", 10, "bold"))
                        self.result_group2_wifi_softap_rssi.config(text=f"{signal_level} dBm", fg="black", font=("Helvetica", 10, "bold"))
                        signal_level = int(signal_level.split(' ')[0]) # this step to remove 'dBm"
                        if signal_level >= int(test_range):
                            logger.info("Wi-Fi Soft AP Test: Pass")
                            print("Wi-Fi Soft AP Test: Pass")
                            self.result_group2_wifi_softap.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                        else:
                            logger.info("Wi-Fi Soft AP Test: Failed")
                            print("Wi-Fi Soft AP Test: Failed")
                            self.result_group2_wifi_softap.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                        break
                    elif ssid == device_wifi_softap_name1:
                        logger.info(f"Target network found: SSID: {ssid}, Signal Level: {signal_level}")
                        print(f"Target network found: SSID: {ssid}, Signal Level: {signal_level}")
                        self.result_group2_wifi_softap_ssid.config(text=f"{ssid}", fg="black", font=("Helvetica", 10, "bold"))
                        self.result_group2_wifi_softap_rssi.config(text=f"{signal_level} dBm", fg="black", font=("Helvetica", 10, "bold"))
                        signal_level = int(signal_level.split(' ')[0]) # this step to remove 'dBm"
                        if signal_level >= int(test_range):
                            logger.info("Wi-Fi Soft AP Test: Pass")
                            print("Wi-Fi Soft AP Test: Pass")
                            self.result_group2_wifi_softap.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                        else:
                            logger.info("Wi-Fi Soft AP Test: Failed")
                            print("Wi-Fi Soft AP Test: Failed")
                            self.result_group2_wifi_softap.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                        break
                    elif ssid == device_wifi_softap_name2:
                        logger.info(f"Target network found: SSID: {ssid}, Signal Level: {signal_level}")
                        print(f"Target network found: SSID: {ssid}, Signal Level: {signal_level}")
                        self.result_group2_wifi_softap_ssid.config(text=f"{ssid}", fg="black", font=("Helvetica", 10, "bold"))
                        self.result_group2_wifi_softap_rssi.config(text=f"{signal_level} dBm", fg="black", font=("Helvetica", 10, "bold"))
                        signal_level = int(signal_level.split(' ')[0]) # this step to remove 'dBm"
                        if signal_level >= int(test_range):
                            logger.info("Wi-Fi Soft AP Test: Pass")
                            print("Wi-Fi Soft AP Test: Pass")
                            self.result_group2_wifi_softap.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                        else:
                            logger.info("Wi-Fi Soft AP Test: Failed")
                            print("Wi-Fi Soft AP Test: Failed")
                            self.result_group2_wifi_softap.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                        break
            else:
                logger.info("No WiFi networks found.")
                print("No WiFi networks found.")
        else:
            logger.info("qrCode_data is empty")
            print("qrCode_data is empty")

    def get_atbeam_rssi(self, test_range):
        # iwconfig_info = run_iwconfig()
        # read_ssid = iwconfig_info.get('SSID', 'Unknown')
        # read_signal_level = iwconfig_info.get('Signal_Level', 'N/A')
        # if read_signal_level:
        # logger.info(f"Wi-Fi Station RSSI: {read_signal_level}")
        # print(f"Wi-Fi Station RSSI: {read_signal_level}")
        logger.info(f"Wi-Fi Station RSSI Test Range: {test_range}")
        print(f"Wi-Fi Station RSSI Test Range: {test_range}")
        # self.result_group2_wifi_station_rssi.config(text=f"{read_signal_level}", fg="black", font=("Helvetica", 10, "bold"))
        read_signal_level = self.result_group2_wifi_station_rssi.cget("text")
        read_signal_level = int(read_signal_level.split(' ')[0])
        if read_signal_level >= int(test_range):
            logger.info(f"Wi-Fi Station RSSI: Pass")
            print(f"Wi-Fi Station RSSI: Pass")
            self.result_group2_wifi_station.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
        else:
            logger.info(f"Wi-Fi Station RSSI: Failed")
            print(f"Wi-Fi Station RSSI: Failed")
            self.result_group2_wifi_station.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
        # else:
        #     logger.info(f"Wi-Fi Station RSSI: Error!")
        #     print(f"Wi-Fi Station RSSI: Error!")

    def refresh_dmm_devices(self):
        self.dmmReader.refresh_devices()

    def flash_tool_checking(self):
        self.toolsBar.flash_tool_checking()

    def download_list(self):
        self.toolsBar.download_list()

    def flash_s3_firmwareButton(self):
        selected_port = self.port_var1.get()
        selected_baud = int(self.baud_var1.get())
        # self.flash_s3_firmware(selected_port, selected_baud)
        
    def reboot_s3(self, port_var, baud_var):
        print("Reboot S3 : ", port_var, baud_var)
        self.flashFw.reset_esptool_device(port_var, baud_var)

    # def reboot_s3(self, gpio_method, use_esptool, port_var, baud_var):
    #     if gpio_method == True:
    #         self.rebootPin.reboot_esp32()
    #         self.rebootPin.cleanup()
    #     else:
    #         if use_esptool == True:
    #             self.flashFw.reset_esptool_device(port_var, baud_var)
    #         else:
    #             self.flashFw.reset_openocd_device(port_var, baud_var)

    def reboot_h2(self, use_esptool, port_var, baud_var):
        if use_esptool == True:
            self.flashFw.reset_esptool_device(port_var, baud_var)
        else:
            self.flashFw.reset_openocd_device(port_var, baud_var)

    def read_s3_mac_address(self, port_var, baud_var):
        self.flashFw.get_openocd_device_mac_address(port_var, baud_var)

    def read_h2_mac_address(self, port_var, baud_var):
        self.flashFw.get_esptool_device_mac_address(port_var, baud_var)

    def record_s3_mac_address(self, mac_address):
        self.flashFw.record_esp32s3_mac_address(mac_address)

    def erase_flash_esp32s3(self, enable, use_esptool, port_var, baud_var, start_addr, end_addr):
        if enable == "True":
            self.flashFw.erase_flash_s3(use_esptool, port_var, baud_var, start_addr, end_addr)
        else:
            pass

    def erase_flash_esp32h2(self, enable, use_esptool, port_var, baud_var, start_addr, end_addr):
        if enable == "True":
            self.flashFw.erase_flash_h2(use_esptool, port_var, baud_var, start_addr, end_addr)
        else:
            pass

    def flash_s3_firmware(self, use_esptool, port_var, baud_var, bootloader_addr, partition_table_addr, ota_data_initial_addr, fw_addr):
        print('flash_s3_firmware-start');
        # self.flashFw.flash_s3_firmware(self.port_var, self.baud_var)
        self.flashFw.flash_s3_firmware(use_esptool, port_var, baud_var, bootloader_addr, partition_table_addr, ota_data_initial_addr, fw_addr)
        print('flash_s3_firmware-end');

    def flash_h2_firmware(self, use_esptool, port_var, baud_var, bootloader_addr, partition_table_addr, fw_addr):
        self.flashFw.flash_h2_firmware(use_esptool, port_var, baud_var, bootloader_addr, partition_table_addr, fw_addr)

    def flash_cert(self, port_var):
        # self.flashCert.flash_cert(self.port_var)
        self.flashCert.flash_cert(port_var)

    def open_serial_port(self):
        selected_port = self.port_var1.get()
        selected_baud = int(self.baud_var1.get())
        self.serialCom.open_serial_port(selected_port, selected_baud)

    def close_serial_port(self):
        self.serialCom.close_serial_port()

    def get_device_mac(self):
        command = "FF:3;MAC?\r\n"
        self.send_command(command)

    def send_command(self, command):
        if self.serialCom.serial_port and self.serialCom.serial_port.is_open:
            self.serialCom.serial_port.write(command.encode())
            logger.debug(f"SerialCom, Sent: {command.strip()}")
            print(f"SerialCom, Sent: {command.strip()}")
        else:
            logger.error("SerialCom, Port is not open. Please open the port before sending commands.")
            print("SerialCom, Port is not open. Please open the port before sending commands.")

    def send_serial_number(self, serial_number):
        self.sendEntry.send_serial_number_command(serial_number)

    def send_mqtr(self, mtqr):
        self.sendEntry.send_mtqr_command(mtqr)

    def create_menubar(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Setting", command=self.config_setting)
        file_menu.add_command(label="Run As Admin", command=self.admin_login)
        file_menu.add_separator()
        #file_menu.add_command(label="Exit", command=self.on_exit)
        menubar.add_cascade(label="File", menu=file_menu)

        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Check Flash Tool", command=self.flash_tool_checking)
        tools_menu.add_command(label="Download List", command=self.download_list)
        tools_menu.add_command(label="Upload Test Script", command=self.load_test_script)
        self.manual_test_menu = tools_menu.add_command(label="Manual Test", command=self.manual_test)
        tools_menu.entryconfig("Manual Test", state=tk.DISABLED)
        self.tools_menu = tools_menu
        menubar.add_cascade(label="Tools", menu=tools_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def admin_login(self):
        login_window = tk.Toplevel(self.root)
        app = AdminLoginApp(login_window, self)
        login_window.wait_window(login_window)  # Wait for the login window to close
        if app.result:
            # Decrypt and verify the password
            decrypted_password = self.decrypt_password()
            logger.debug("Decrypted Password: %s", decrypted_password)  # Debugging message
            if decrypted_password == "admin":  # Replace "admin" with the actual password if needed
                messagebox.showinfo("Login Successful", "Admin login successful. Manual Test enabled.")
                # Change the Manual Test from menubar state to Normal
                self.tools_menu.entryconfig("Manual Test", state=tk.NORMAL)

                self.exit_button.grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)
                self.port_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
                self.port_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
                self.baud_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
                self.baud_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
                self.flash_button.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
                self.cert_flash_button.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
                self.port_label1.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
                self.port_dropdown1.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
                self.baud_label1.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
                self.baud_dropdown1.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
                self.open_port_button.grid(row=1, column=4, padx=5, pady=5, sticky=tk.W)
                self.close_port_button.grid(row=1, column=5, padx=5, pady=5, sticky=tk.W)
                self.read_device_mac_button.grid(row=1, column=6, padx=5, pady=5, sticky=tk.W)
                self.write_device_serialnumber_button.grid(row=1, column=7, padx=5, pady=5, sticky=tk.W)
                self.write_device_mtqr_button.grid(row=1, column=8, padx=5, pady=5, sticky=tk.W)
                self.read_atbeam_temp_button.grid(row=1, column=9, padx=5, pady=5, sticky=tk.W)
                self.read_atbeam_humid_button.grid(row=1, column=10, padx=5, pady=5, sticky=tk.W)


                self.enable_frame(self.serial_baud_frame)
                self.serial_baud_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

                self.enable_frame(self.text_frame)
                self.text_frame.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

                self.enable_frame(self.servo_frame)
                self.servo_frame.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)


            else:
                messagebox.showerror("Error", "Failed to decrypt password or invalid password!")


    def config_setting(self):
        SettingApp(tk.Toplevel(self.root))

    def manual_test(self):
        ManualTestApp(self.root, self.send_command).open_manual_test_window()

    def decrypt_password(self):
        key_file = "secret.key"
        password_file = "password.txt"
        try:
            with open(key_file, "rb") as kf:
                key = kf.read()
            with open(password_file, "rb") as pf:
                encrypted_password = pf.read()
            fernet = Fernet(key)
            decrypted_password = fernet.decrypt(encrypted_password).decode()
            return decrypted_password
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None

    def upload_report(self):
        ini_file_path = filedialog.askopenfilename(title="Select .ini file", filetypes=[("INI files", "*.ini")])
        if not ini_file_path:
            return

        config = configparser.ConfigParser()
        config.read(ini_file_path)

        # Create a single dictionary from the INI file sections
        combined_data = {}
        for section in config.sections():
            combined_data.update(config[section])

        # Convert to the desired JSON format: a list of one dictionary
        data = [combined_data]

        # Debugging: Print the data dictionary to verify its contents
        logger.debug("Converted data: %s", data)

        api_url = "http://localhost:4000/api/endpoint"   # Replace with actual API endpoint

        response = uploadReport.post_report(api_url, data)

        if response and response.status_code == 200:
            messagebox.showinfo("Success", "Report uploaded successfully!")
        else:
            messagebox.showerror("Error", "Failed to upload report.")

    def read_order_numbers(self, file_path):
        order_numbers = []
        with open(file_path, 'r') as file:
            for line in file:
                if 'order-no' in line:
                    order_number = line.split('order-no: ')[1].split(',')[0].strip()
                    if order_number not in order_numbers:
                        order_numbers.append(order_number)
        return order_numbers

    def on_order_selected(self, event):
        selected_order = event.widget.get()
        cert_ids = self.flashCert.get_cert_ids_for_order(orders, selected_order)
        remaining_cert_ids = self.flashCert.get_remaining_cert_ids(cert_ids)

        if remaining_cert_ids:
            self.cert_id_dropdown['values'] = remaining_cert_ids
            self.cert_id_dropdown.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        else:
            self.cert_id_label.config(text="No Cert IDs available for this order.")
            self.cert_id_dropdown.pack_forget()

        logger.info(f"Selected order: {selected_order}")

    def read_port_from_config(self):
        global ini_file_name
        global script_dir

        # Check in the specified directory
        ini_file_path = os.path.join(script_dir, ini_file_name)

        config = configparser.ConfigParser()
        config.read(ini_file_path)
        return config.get('flash', 'port', fallback=None)

    def flashCertificate(self, use_esptool, selected_port, selected_baud, serialID_label, serialID, certID_label, uuid, macAddr_label, macAddr, securecert_addr, dataprovider_addr):
        self.flashCert.flash_certificate(use_esptool, selected_port, selected_baud, serialID_label, serialID, certID_label, uuid, macAddr_label, macAddr, securecert_addr, dataprovider_addr)

    # def on_select_cert_id(self, event):
    #     selected_cert_id = event.widget.get()

    #     if selected_cert_id:
    #         if selected_cert_id not in self.used_cert_ids:
    #             # Flash the certificate
    #             self.flashCertificate(selected_cert_id, "/dev/ttyUSB0")

    #             # Mark the cert_id as used
    #             self.used_cert_ids.add(selected_cert_id)

    #             # Update remaining cert_ids
    #             remaining_cert_ids = self.flashCert.get_remaining_cert_ids(
    #                 self.flashCert.get_cert_ids_for_order(orders, self.order_number_dropdown.get())
    #             )
    #             remaining_cert_ids = [cert_id for cert_id in remaining_cert_ids if cert_id not in self.used_cert_ids]
    #             self.cert_id_dropdown['values'] = remaining_cert_ids

    #             # Update status label
    #             self.cert_status_label.config(text=f"Cert {selected_cert_id} flashed.")

    #         else:
    #             # If the cert_id has already been used
    #             self.cert_status_label.config(text=f"Cert {selected_cert_id} has already been used.")
    #     else:
    #         # If no cert_id is selected
    #         self.cert_status_label.config(text=f"Failed to flash cert {selected_cert_id}.")

    def on_select_cert_id(self, event):
        global qrcode
        global manualcode
        # Retrieve the selected certificate ID from the dropdown
        selected_cert_id = event.widget.get()

        if selected_cert_id:
            # Store the selected certificate ID in an instance variable
            self.selected_cert_id = selected_cert_id

            # Update status label
            self.cert_status_label.config(text=f"Cert {selected_cert_id} selected.")
            qrcode = self.flashCert.get_qrcode_for_cert_id(orders, selected_cert_id)
            qrcode = str(qrcode).strip("[]'")
            manualcode = self.flashCert.get_manualcode_for_cert_id(orders, selected_cert_id)
            manualcode = str(manualcode).strip("[]'")
        else:
            # If no certificate ID is selected
            self.cert_status_label.config(text="No certificate selected.")


    def disable_frame(self, frame):
        for child in frame.winfo_children():
            child.configure(state='disabled')

    def enable_frame(self, frame):
        for child in frame.winfo_children():
            child.configure(state='normal')

    def cancel_to_printer(self):
        global break_printer

        logger.info(f"Print Sticker: Cancel")
        print(f"Print Sticker: Cancel")
        self.printer_status_data_label.config(text="Cancel", fg="red", font=("Helvetica", 10, "bold"))
        break_printer = 1

    def send_to_printer(self):
        print(f"send_to_printer")
        global qrCode_data
        global manualCode_data
        global break_printer

        if qrCode_data and manualCode_data:
            qrcode = qrCode_data
            manualcode = manualCode_data
        else:
            qrcode = ""
            manualcode =""

        if qrcode and manualcode:
            logger.info(f"Print Sticker, QR code payload = {qrcode}")
            print(f"Print Sticker, QR code payload = {qrcode}")
            logger.info(f"Print Sticker, Manual Code = {manualcode}")
            print(f"Print Sticker, Manual Code = {manualcode}")

            # printer_ip = self.printer_ip_var.get()
            # printer_port = self.printer_port_var.get()
            # sendToPrinterFunc(qrcode, manualcode, printer_ip, printer_port)
            sendToPrinterFunc(qrcode, manualcode, "1", "1")
            logger.info(f"Print Sticker: Done")
            print(f"Print Sticker: Done")
            self.printer_status_data_label.config(text="Printed", fg="green", font=("Helvetica", 10, "bold"))
        else:
            logger.info(f"Print Sticker: Failed")
            print(f"Print Sticker: Failed")
            logger.error("Please select a Cert ID first before printing.")
            print("Please select a Cert ID first before printing.")
            self.printer_status_data_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))

        break_printer = 1

    def retrieve_device_data(self, database_file_path, order_number, mac_address):
        if not mac_address:
            # logger.info("Device MAC address not available")
            print("retrieve_device_data: Device MAC address not available")
            return ""

        try:
            database_file = open (database_file_path, "r")
        except FileNotFoundError:
            pass
        else:
            for database in database_file:
                database_str = str(database.strip())
                # print(database_str)
                data_str = database_str.split(',')
                orderNum_data_str = str(data_str[0])
                macAddress_data_str = str(data_str[1])
                serialID_data_str = str(data_str[2])
                certID_data_str = str(data_str[3])
                secureCertPartition_data_str = str(data_str[4])
                commissionableDataPartition_data_str = str(data_str[5])
                qrCode_data_str = str(data_str[6])
                manualCode_data_str = str(data_str[7])
                discriminator_data_str = str(data_str[8])
                passcode_data_str = str(data_str[9])
                # print(orderNum_data_str)
                # print(macAddress_data_str)
                # print(serialID_data_str)
                # print(certID_data_str)
                # print(secureCertPartition_data_str)
                # print(commissionableDataPartition_data_str)
                # print(qrCode_data_str)
                # print(manualCode_data_str)
                # print(discriminator_data_str)
                # print(passcode_data_str)
                macAddress_data_array = macAddress_data_str.split(": ")
                # print(macAddress_data_array[0])
                # print(macAddress_data_array[1])
                if str(mac_address) == macAddress_data_array[1]:
                    orderNum_data_array = orderNum_data_str.split(": ")
                    if str(order_number) == orderNum_data_array[1]:
                        # logger.info(str(mac_address) + " found in " + str(database_file_path))
                        # logger.info("Data = " + str(database_str))
                        print(str(mac_address) + " found in " + str(database_file_path))
                        print("Data = " + str(database_str))
                        database_file.close()
                        return database_str
                    else:
                        pass
                else:
                    pass
            database_file.close()

        # logger.info(str(mac_address) + " not found in " + str(database_file_path))
        print(str(mac_address) + " not found in " + str(database_file_path))
        try:
            database_file = open (database_file_path, "r")
        except FileNotFoundError:
            pass
        else:
            for database in database_file:
                database_str = str(database.strip())
                # print(database_str)
                data_str = database_str.split(',')
                orderNum_data_str = str(data_str[0])
                macAddress_data_str = str(data_str[1])
                serialID_data_str = str(data_str[2])
                certID_data_str = str(data_str[3])
                secureCertPartition_data_str = str(data_str[4])
                commissionableDataPartition_data_str = str(data_str[5])
                qrCode_data_str = str(data_str[6])
                manualCode_data_str = str(data_str[7])
                discriminator_data_str = str(data_str[8])
                passcode_data_str = str(data_str[9])
                # print(orderNum_data_str)
                # print(macAddress_data_str)
                # print(serialID_data_str)
                # print(certID_data_str)
                # print(secureCertPartition_data_str)
                # print(commissionableDataPartition_data_str)
                # print(qrCode_data_str)
                # print(manualCode_data_str)
                # print(discriminator_data_str)
                # print(passcode_data_str)
                macAddress_data_array = macAddress_data_str.split(": ")
                # print(macAddress_data_array[0])
                # print(macAddress_data_array[1])
                if not macAddress_data_array[1]:
                    orderNum_data_array = orderNum_data_str.split(": ")
                    if str(order_number) == orderNum_data_array[1]:
                        # logger.info("Return available data slot")
                        # logger.info(f"Data = {database_str}")
                        print("Return available data slot")
                        print(f"Data = {database_str}")
                        database_file.close()
                        return database_str
                    else:
                        pass
                else:
                    pass
            print("No available data slot")
            database_file.close()
            return ""

    def parse_device_data(self, database_data, mac_address):
        global device_data
        global orderNum_label
        global macAddress_label
        global serialID_label
        global certID_label
        global secureCertPartition_label
        global commissionableDataPartition_label
        global qrCode_label
        global manualCode_label
        global discriminator_label
        global passcode_label
        global orderNum_data
        global macAddress_esp32s3_data
        global serialID_data
        global certID_data
        global secureCertPartition_data
        global commissionableDataPartition_data
        global qrCode_data
        global manualCode_data
        global discriminator_data
        global passcode_data

        if not mac_address:
            # logger.info("Device MAC address not available")
            print("parse_device_data: Device MAC address not available")
            return ""

        data_str = database_data.split(',')
        orderNum_data_str = str(data_str[0])
        macAddress_data_str = str(data_str[1])
        serialID_data_str = str(data_str[2])
        certID_data_str = str(data_str[3])
        secureCertPartition_data_str = str(data_str[4])
        commissionableDataPartition_data_str = str(data_str[5])
        qrCode_data_str = str(data_str[6])
        manualCode_data_str = str(data_str[7])
        discriminator_data_str = str(data_str[8])
        passcode_data_str = str(data_str[9])
        # print(orderNum_data_str)
        # print(macAddress_data_str)
        # print(serialID_data_str)
        # print(certID_data_str)
        # print(secureCertPartition_data_str)
        # print(commissionableDataPartition_data_str)
        # print(qrCode_data_str)
        # print(manualCode_data_str)
        # print(discriminator_data_str)
        # print(passcode_data_str)
        orderNum_data_array = orderNum_data_str.split(": ")
        orderNum_label = orderNum_data_array[0]
        orderNum_data = orderNum_data_array[1]
        # print(orderNum_label)
        # print(orderNum_data)
        macAddress_data_array = macAddress_data_str.split(": ")
        macAddress_label = macAddress_data_array[0]
        # macAddress_esp32s3_data = macAddress_data_array[1]
        macAddress_esp32s3_data = mac_address
        # print(macAddress_label)
        # print(macAddress_esp32s3_data)
        serialID_data_array = serialID_data_str.split(": ")
        serialID_label = serialID_data_array[0]
        serialID_data = serialID_data_array[1]
        # print(serialID_label)
        # print(serialID_data)
        certID_data_array = certID_data_str.split(": ")
        certID_label = certID_data_array[0]
        certID_data = certID_data_array[1]
        # print(certID_label)
        # print(certID_data)
        secureCertPartition_data_array = secureCertPartition_data_str.split(": ")
        secureCertPartition_label = secureCertPartition_data_array[0]
        secureCertPartition_data = secureCertPartition_data_array[1]
        # print(secureCertPartition_label)
        # print(secureCertPartition_data)
        commissionableDataPartition_data_array = commissionableDataPartition_data_str.split(": ")
        commissionableDataPartition_label = commissionableDataPartition_data_array[0]
        commissionableDataPartition_data = commissionableDataPartition_data_array[1]
        # print(commissionableDataPartition_label)
        # print(commissionableDataPartition_data)
        qrCode_data_array = qrCode_data_str.split(": ")
        qrCode_label = qrCode_data_array[0]
        qrCode_data = qrCode_data_array[1]
        # print(qrCode_label)
        # print(qrCode_data)
        manualCode_data_array = manualCode_data_str.split(": ")
        manualCode_label = manualCode_data_array[0]
        manualCode_data = manualCode_data_array[1]
        # print(manualCode_label)
        # print(manualCode_data)
        discriminator_data_array = discriminator_data_str.split(": ")
        discriminator_label = discriminator_data_array[0]
        discriminator_data = discriminator_data_array[1]
        # print(discriminator_label)
        # print(discriminator_data)
        passcode_data_array = passcode_data_str.split(": ")
        passcode_label = passcode_data_array[0]
        passcode_data = passcode_data_array[1]
        # print(passcode_label)
        # print(passcode_data)
        
    # Binding Page Up and Page Down keys to scroll the canvas
        
    def bind_scroll_keys(self):
        self.canvas.bind_all("<Prior>", self.scroll_page_up)
        self.canvas.bind_all("<Next>", self.scroll_page_down)
        
    def bind_keys(self):
        print("Binding keys")
        self.root.bind("<space>", self.space_key)
        self.root.bind("<Escape>", self.escape_key)
        
    def space_key(self, event):
        if self.current_set < len(self.button_sets):
            self.on_yes_click(self.current_set)

    def escape_key(self, event):
        if self.current_set < len(self.button_sets):
            self.on_no_click(self.current_set)
            
    def on_yes_click(self, set_number):
        if set_number == self.current_set:
            self.handle_click(set_number, "Yes")

    def on_no_click(self, set_number):
        if set_number == self.current_set:
            self.handle_click(set_number, "No")

    def scroll_page_up(self, event):
        self.canvas.yview_scroll(-1, "pages")

    def scroll_page_down(self, event):
        self.canvas.yview_scroll(1, "pages")
        
    def handle_click(self, set_number, button_type):
        # messagebox.showinfo("Button Clicked", f"Set {set_number + 1} {button_type} button clicked")
        if button_type == "Yes":
            self.button_sets[set_number][0].invoke()
        elif button_type == "No":
            self.button_sets[set_number][1].invoke()
        
        self.disable_buttons(set_number)
        self.current_set = min(self.current_set + 1, len(self.button_sets) - 1)
        
    def disable_buttons(self, set_number):
        for button in self.button_sets[set_number]:
            button.config(state=tk.DISABLED)

    def refresh_com_ports_list(self):
        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(self.serial_baud_frame, textvariable=self.port_var)
        self.port_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.port_dropdown['values'] = [port.device for port in serial.tools.list_ports.comports()]
        for port in serial.tools.list_ports.comports():
            # print(str(port.device))
            if str(port.device) == "/dev/ttyUSB0":
                self.port_dropdown.set(port.device)

        self.port_var1 = tk.StringVar()
        self.port_dropdown1 = ttk.Combobox(self.serial_baud_frame, textvariable=self.port_var1)
        self.port_dropdown1.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.port_dropdown1['values'] = [port.device for port in serial.tools.list_ports.comports()]
        for port in serial.tools.list_ports.comports():
            # print(str(port.device))
            if str(port.device) == "/dev/ttyUSB1":
                self.port_dropdown1.set(port.device)

        self.port_var2 = tk.StringVar()
        self.port_dropdown2 = ttk.Combobox(self.serial_baud_frame, textvariable=self.port_var2)
        self.port_dropdown2.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.port_dropdown2['values'] = [port.device for port in serial.tools.list_ports.comports()]
        for port in serial.tools.list_ports.comports():
            # print(str(port.device))
            if str(port.device) == "/dev/ttyUSB2":
                self.port_dropdown2.set(port.device)

    def create_widgets(self):
        global device_data_file_path
        # file_path = '/usr/src/app/ATSoftwareDevelopmentTool/FlashingTool/device_data.txt'
        # file_path = '/home/anuarrozman/Airdroitech/ATSoftwareDevelopmentTool/FlashingTool/device_data.txt'        
        
        order_numbers = self.read_order_numbers(device_data_file_path)

        # Create a frame for the canvas
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas and add a scrollbar
        self.canvas = tk.Canvas(self.canvas_frame)
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create another frame inside the canvas
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.bind_scroll_keys()
        
        self.bind_keys()

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configure the weight for the scrollable_frame to expand
        self.scrollable_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        self.serial_baud_frame = tk.Frame(self.scrollable_frame)
        self.serial_baud_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.exit_button = ttk.Button(self.serial_baud_frame, text="Exit", command=self.root.quit)
        self.exit_button.grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)

        self.port_label = tk.Label(self.serial_baud_frame, text="ESP32S3 Flash Port/ESP32S3烧录端口:")
        self.port_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(self.serial_baud_frame, textvariable=self.port_var)
        self.port_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.port_dropdown['values'] = [port.device for port in serial.tools.list_ports.comports()]
        for port in serial.tools.list_ports.comports():
            # print(str(port.device))
            if str(port.device) == "/dev/ttyUSB0":
                self.port_dropdown.set(port.device)

        self.baud_label = tk.Label(self.serial_baud_frame, text="Baud Rate/波特率:")
        self.baud_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        # self.baud_label.grid_forget()

        self.baud_var = tk.StringVar()
        self.baud_dropdown = ttk.Combobox(self.serial_baud_frame, textvariable=self.baud_var)
        self.baud_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.baud_dropdown['values'] = ["9600", "115200", "460800"]
        self.baud_dropdown.set("460800")
        # self.baud_dropdown.grid_forget()

        self.flash_button = ttk.Button(self.serial_baud_frame, text="Flash FW", command=self.flash_s3_firmwareButton)
        self.flash_button.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)

        self.cert_flash_button = ttk.Button(self.serial_baud_frame, text="Flash Cert", command=self.flash_cert)
        self.cert_flash_button.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        self.port_label1 = tk.Label(self.serial_baud_frame, text="ESP32S3 Factory Port/ESP32S3工厂模式端口:")
        self.port_label1.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.port_var1 = tk.StringVar()
        self.port_dropdown1 = ttk.Combobox(self.serial_baud_frame, textvariable=self.port_var1)
        self.port_dropdown1.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.port_dropdown1['values'] = [port.device for port in serial.tools.list_ports.comports()]
        for port in serial.tools.list_ports.comports():
            # print(str(port.device))
            if str(port.device) == "/dev/ttyUSB1":
                self.port_dropdown1.set(port.device)

        self.baud_label1 = tk.Label(self.serial_baud_frame, text="Baud Rate/波特率:")
        self.baud_label1.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        # self.baud_label1.grid_forget()

        self.baud_var1 = tk.StringVar()
        self.baud_dropdown1 = ttk.Combobox(self.serial_baud_frame, textvariable=self.baud_var1)
        self.baud_dropdown1.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        self.baud_dropdown1['values'] = ["9600", "115200", "460800"]
        self.baud_dropdown1.set("115200")
        # self.baud_dropdown1.grid_forget()

        self.open_port_button = ttk.Button(self.serial_baud_frame, text="Open Port", command=self.open_serial_port)
        self.open_port_button.grid(row=1, column=4, padx=5, pady=5, sticky=tk.W)

        self.close_port_button = ttk.Button(self.serial_baud_frame, text="Close Port", command=self.close_serial_port)
        self.close_port_button.grid(row=1, column=5, padx=5, pady=5, sticky=tk.W)

        self.read_device_mac_button = ttk.Button(self.serial_baud_frame, text="Read Device MAC", command=self.get_device_mac)
        self.read_device_mac_button.grid(row=1, column=6, padx=5, pady=5, sticky=tk.W)

        self.write_device_serialnumber_button = ttk.Button(self.serial_baud_frame, text="Write S/N", command=self.send_serial_number)
        self.write_device_serialnumber_button.grid(row=1, column=7, padx=5, pady=5, sticky=tk.W)

        self.write_device_mtqr_button = ttk.Button(self.serial_baud_frame, text="Write MTQR", command=self.send_mqtr)
        self.write_device_mtqr_button.grid(row=1, column=8, padx=5, pady=5, sticky=tk.W)

        self.read_atbeam_temp_button = ttk.Button(self.serial_baud_frame, text="Read ATBeam Temp", command=self.get_atbeam_temp)
        self.read_atbeam_temp_button.grid(row=1, column=9, padx=5, pady=5, sticky=tk.W)

        self.read_atbeam_humid_button = ttk.Button(self.serial_baud_frame, text="Read ATBeam Humid", command=self.get_atbeam_humid)
        self.read_atbeam_humid_button.grid(row=1, column=10, padx=5, pady=5, sticky=tk.W)

        self.port_label2 = tk.Label(self.serial_baud_frame, text="ESP32H2 Flash Port/ESP32H2烧录端口:")
        self.port_label2.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.port_var2 = tk.StringVar()
        self.port_dropdown2 = ttk.Combobox(self.serial_baud_frame, textvariable=self.port_var2)
        self.port_dropdown2.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.port_dropdown2['values'] = [port.device for port in serial.tools.list_ports.comports()]
        for port in serial.tools.list_ports.comports():
            # print(str(port.device))
            if str(port.device) == "/dev/ttyUSB2":
                self.port_dropdown2.set(port.device)

        self.baud_label2 = tk.Label(self.serial_baud_frame, text="Baud Rate/波特率:")
        self.baud_label2.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        # self.baud_label2.grid_forget()

        self.baud_var2 = tk.StringVar()
        self.baud_dropdown2 = ttk.Combobox(self.serial_baud_frame, textvariable=self.baud_var2)
        self.baud_dropdown2.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)
        self.baud_dropdown2['values'] = ["9600", "115200", "460800"]
        self.baud_dropdown2.set("115200")
        # self.baud_dropdown2.grid_forget()

        #self.disable_frame(self.serial_baud_frame)
        #self.serial_baud_frame.grid_forget()
        self.flash_button.grid_forget()
        self.cert_flash_button.grid_forget()
        self.flash_button.grid_forget()
        self.open_port_button.grid_forget()
        self.close_port_button.grid_forget()
        self.read_device_mac_button.grid_forget()
        self.write_device_serialnumber_button.grid_forget()
        self.write_device_mtqr_button.grid_forget()
        self.read_atbeam_temp_button.grid_forget()
        self.read_atbeam_humid_button.grid_forget()
        self.exit_button.grid_forget()

        self.text_frame = tk.Frame(self.scrollable_frame)
        self.text_frame.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.send_entry_frame = ttk.Entry(self.text_frame, width=50)
        self.send_entry_frame.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.send_button = ttk.Button(self.text_frame, text="Send", command=lambda: self.sendEntry.send_entry_command(self.send_entry_frame))
        self.send_button.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.disable_frame(self.text_frame)
        self.text_frame.grid_forget()

        self.servo_frame = tk.Frame(self.scrollable_frame)
        self.servo_frame.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)

        self.angle_label = tk.Label(self.servo_frame, text="Enter servo angle:")
        self.angle_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.angle_entry = tk.Entry(self.servo_frame)
        self.angle_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.duration_label = tk.Label(self.servo_frame, text="Enter pressing duration:")
        self.duration_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.duration_entry = tk.Entry(self.servo_frame)
        self.duration_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        self.pressing_time_label = tk.Label(self.servo_frame, text="Enter pressing time:")
        self.pressing_time_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.pressing_time_entry = tk.Entry(self.servo_frame)
        self.pressing_time_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.disable_frame(self.servo_frame)
        self.servo_frame.grid_forget()

        self.dmm_frame = tk.Frame(self.scrollable_frame)
        self.dmm_frame.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

        self.upload_report_button = ttk.Button(self.dmm_frame, text="Upload Report", command=self.upload_report)
        self.upload_report_button.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.upload_report_button.grid_forget()

        self.read_temp_aht20_button = ttk.Button(self.dmm_frame, text="Read Temperature Sensor", command=self.read_temp_aht20)
        self.read_temp_aht20_button.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        self.read_humid_aht20_button = ttk.Button(self.dmm_frame, text="Read Humidity Sensor", command=self.read_humid_aht20)
        self.read_humid_aht20_button.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)
        self.read_humid_aht20_button.grid_forget()

        # self.disable_frame(self.dmm_frame)
        # self.dmm_frame.grid_forget()

        
        # Order Number
        self.order_number_frame = tk.Frame(self.scrollable_frame)
        self.order_number_frame.grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)

        self.order_number_label = tk.Label(self.order_number_frame, text="Order Number/订单号:")
        self.order_number_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.order_number_dropdown = tk.StringVar()
        self.order_number_dropdown_list = ttk.Combobox(self.order_number_frame, textvariable=self.order_number_dropdown, values=order_numbers)
        # self.order_number_dropdown_list.bind("<<ComboboxSelected>>", self.on_order_selected)
        self.order_number_dropdown_list.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.selected_order_no_label = tk.Label(self.order_number_frame, text="")
        self.selected_order_no_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.cert_id_label = tk.Label(self.order_number_frame, text="Select Cert ID:")
        self.cert_id_label.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.cert_id_label.grid_forget()
        
        cert_id_var = tk.StringVar()
        self.cert_id_dropdown = ttk.Combobox(self.order_number_frame, textvariable=cert_id_var)
        self.cert_id_dropdown.bind("<<ComboboxSelected>>", self.on_select_cert_id)
        self.cert_id_dropdown.grid_forget()
        
        self.cert_status_label = tk.Label(self.order_number_frame, text="")
        self.cert_status_label.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        # Start and Stop buttons
        self.control_frame = tk.Frame(self.scrollable_frame)
        self.control_frame.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)

        self.start_button = ttk.Button(self.control_frame, text="Start/开始", command=self.combine_tasks)
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.stop_button = ttk.Button(self.control_frame, text="Stop", command=None)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.stop_button.grid_forget()

        self.reset_button = ttk.Button(self.control_frame, text="Reset", command=self.reset_tasks)
        self.reset_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.reset_button.grid_forget()

        self.retest_label = tk.Label(self.control_frame, text="Retest MAC:")
        self.retest_label.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.retest_label.grid_forget()

        self.retest_mac_input = tk.Entry(self.control_frame)
        self.retest_mac_input.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.retest_mac_input.grid_forget()

        self.retest_button = ttk.Button(self.control_frame, text="Retest", command=None)
        self.retest_button.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        self.retest_button.grid_forget()

        self.notes_label = tk.Label(self.control_frame, text="<<- Select order number to start/首先选择订单号", font=("Helvetica", 10, "bold"))
        self.notes_label.grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)

        # Group 1
        # Flash FW, Flash Cert, Factory Mode, Read Device MAC, Read Product Name, Write Device S/N, Write Device MTQR, 3.3V, 5V, Button Pressed, Sensor Temperature, Sensor Humidity
        self.group1_frame = tk.Frame(self.scrollable_frame, highlightbackground="black", highlightcolor="black", highlightthickness=2, bd=2)
        self.group1_frame.grid(row=7, column=0, padx=10, pady=10, sticky=tk.W)

        self.auto_frame_label = tk.Label(self.group1_frame, text="Semi Auto Test/半自动测试", font=("Helvetica", 10, "bold"))
        self.auto_frame_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.read_mac_address_label = tk.Label(self.group1_frame, text="MAC Address/MAC地址: ")
        self.read_mac_address_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_mac_address_s3_index = tk.Label(self.group1_frame, text="ESP32S3: ")
        self.result_mac_address_s3_index.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)  

        self.result_mac_address_s3_label = tk.Label(self.group1_frame, text="Not Yet")
        self.result_mac_address_s3_label.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)  

        self.result_mac_address_h2_index = tk.Label(self.group1_frame, text="ESP32H2: ")
        self.result_mac_address_h2_index.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)  

        self.result_mac_address_h2_label = tk.Label(self.group1_frame, text="Not Yet")
        self.result_mac_address_h2_label.grid(row=1, column=4, padx=5, pady=5, sticky=tk.W)       
        
        self.status_flashing_fw = tk.Label(self.group1_frame, text="Flashing Firmware/写入固件: ")
        self.status_flashing_fw.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_flashing_fw_s3_index = tk.Label(self.group1_frame, text="ESP32S3: ")
        self.result_flashing_fw_s3_index.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.result_flashing_fw_label = tk.Label(self.group1_frame, text="Not Yet")
        self.result_flashing_fw_label.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)

        self.result_flashing_fw_h2_index = tk.Label(self.group1_frame, text="ESP32H2: ")
        self.result_flashing_fw_h2_index.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)
        
        self.result_flashing_fw_h2_label = tk.Label(self.group1_frame, text="Not Yet")
        self.result_flashing_fw_h2_label.grid(row=2, column=4, padx=5, pady=5, sticky=tk.W)
        
        self.status_flashing_cert = tk.Label(self.group1_frame, text="Flashing DAC/写入DAC: ")
        self.status_flashing_cert.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_flashing_cert_label = tk.Label(self.group1_frame, text="Not Yet")
        self.result_flashing_cert_label.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.status_factory_mode = tk.Label(self.group1_frame, text="Factory Mode/工厂模式: ")
        self.status_factory_mode.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_factory_mode_label = tk.Label(self.group1_frame, text="Not Yet")
        self.result_factory_mode_label.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.status_read_device_mac = tk.Label(self.group1_frame, text="Read Device MAC/读MAC地址: ")
        self.status_read_device_mac.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_read_device_mac = tk.Label(self.group1_frame, text="Not Yet")
        self.result_read_device_mac.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

        self.read_device_mac = tk.Label(self.group1_frame, text="-")
        self.read_device_mac.grid(row=5, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.status_read_prod_name = tk.Label(self.group1_frame, text="Product Name/产品名称: ")
        self.status_read_prod_name.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_read_prod_name = tk.Label(self.group1_frame, text="Not Yet")
        self.result_read_prod_name.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.read_prod_name = tk.Label(self.group1_frame, text="-")
        self.read_prod_name.grid(row=6, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.status_write_device_sn = tk.Label(self.group1_frame, text="Write Device S/N/写入S/N号: ")
        self.status_write_device_sn.grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_write_serialnumber = tk.Label(self.group1_frame,text="Not Yet")
        self.result_write_serialnumber.grid(row=7, column=1, padx=5, pady=5, sticky=tk.W)

        self.read_device_sn = tk.Label(self.group1_frame, text="-")
        self.read_device_sn.grid(row=7, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.status_write_device_mtqr = tk.Label(self.group1_frame, text="Write Device Matter QR/写入Matter二维码: ")
        self.status_write_device_mtqr.grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_write_mtqr = tk.Label(self.group1_frame, text="Not Yet")
        self.result_write_mtqr.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)

        self.read_device_mtqr = tk.Label(self.group1_frame, text="-")
        self.read_device_mtqr.grid(row=8, column=2, padx=5, pady=5, sticky=tk.W)

        self.status_save_device_data_label = tk.Label(self.group1_frame, text="Save Device Data/保存数据: ")
        self.status_save_device_data_label.grid(row=9, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_save_device_data_label = tk.Label(self.group1_frame, text="Not Yet")
        self.result_save_device_data_label.grid(row=9, column=1, padx=5, pady=5, sticky=tk.W)

        self.read_save_device_data_label = tk.Label(self.group1_frame, text="-")
        self.read_save_device_data_label.grid(row=9, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.status_5v_test = tk.Label(self.group1_frame, text="5V Test/5伏测试: ")
        self.status_5v_test.grid(row=10, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_5v_test = tk.Label(self.group1_frame, text="Not Yet")
        self.result_5v_test.grid(row=10, column=1, padx=5, pady=5, sticky=tk.W)

        self.dmm_5V_reader = tk.Label(self.group1_frame, text="-")
        self.dmm_5V_reader.grid(row=10, column=2, padx=5, pady=5, sticky=tk.W)

        self.input_5V_dmm = tk.Entry(self.group1_frame)
        self.input_5V_dmm.grid(row=10, column=3, padx=5, pady=5, sticky=tk.W)

        self.submit_5V_dmm = ttk.Button(self.group1_frame, text="Submit/输入", command=lambda: self.dmm_reader_5V_value_manual(self.input_5V_dmm))
        self.submit_5V_dmm.grid(row=10, column=4, padx=5, pady=5, sticky=tk.W)
        self.submit_5V_dmm.config(state=tk.DISABLED)

        self.range_index_5V_dmm = tk.Label(self.group1_frame, text="Range/测试范围(±): ")
        self.range_index_5V_dmm.grid(row=10, column=5, padx=5, pady=5, sticky=tk.W)

        self.range_value_5V_dmm = tk.Label(self.group1_frame, text="-")
        self.range_value_5V_dmm.grid(row=10, column=6, padx=5, pady=5, sticky=tk.W)

        self.status_3_3v_test = tk.Label(self.group1_frame, text="3.3V Test/3.3伏测试: ")
        self.status_3_3v_test.grid(row=11, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_3_3v_test = tk.Label(self.group1_frame, text="Not Yet")
        self.result_3_3v_test.grid(row=11, column=1, padx=5, pady=5, sticky=tk.W)

        self.dmm_3_3V_reader = tk.Label(self.group1_frame, text="-")
        self.dmm_3_3V_reader.grid(row=11, column=2, padx=5, pady=5, sticky=tk.W)

        self.input_3_3V_dmm = tk.Entry(self.group1_frame)
        self.input_3_3V_dmm.grid(row=11, column=3, padx=5, pady=5, sticky=tk.W)

        self.submit_3_3V_dmm = ttk.Button(self.group1_frame, text="Submit/输入", command=lambda: self.dmm_reader_3_3V_value_manual(self.input_3_3V_dmm))
        self.submit_3_3V_dmm.grid(row=11, column=4, padx=5, pady=5, sticky=tk.W)
        self.submit_3_3V_dmm.config(state=tk.DISABLED)

        self.range_index_3_3V_dmm = tk.Label(self.group1_frame, text="Range/测试范围(±): ")
        self.range_index_3_3V_dmm.grid(row=11, column=5, padx=5, pady=5, sticky=tk.W)

        self.range_value_3_3V_dmm = tk.Label(self.group1_frame, text="-")
        self.range_value_3_3V_dmm.grid(row=11, column=6, padx=5, pady=5, sticky=tk.W)
        
        self.status_atbeam_temp = tk.Label(self.group1_frame, text="Temperature Test/温度测试: ")
        self.status_atbeam_temp.grid(row=12, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_temp_label = tk.Label(self.group1_frame, text="Not Yet")
        self.result_temp_label.grid(row=12, column=1, padx=5, pady=5, sticky=tk.W)

        self.atbeam_temp_index = tk.Label(self.group1_frame, text="Device/产品传感器: ")
        self.atbeam_temp_index.grid(row=12, column=2, padx=5, pady=5, sticky=tk.W)

        self.atbeam_temp_value = tk.Label(self.group1_frame, text="AT °C")
        self.atbeam_temp_value.grid(row=12, column=3, padx=5, pady=5, sticky=tk.W)

        self.ext_temp_index = tk.Label(self.group1_frame, text="External/外部传感器: ")
        self.ext_temp_index.grid(row=12, column=4, padx=5, pady=5, sticky=tk.W)

        self.ext_temp_value = tk.Label(self.group1_frame, text="Ext °C")
        self.ext_temp_value.grid(row=12, column=5, padx=5, pady=5, sticky=tk.W)

        self.range_temp_index = tk.Label(self.group1_frame, text="Range/测试范围(±): ")
        self.range_temp_index.grid(row=12, column=6, padx=5, pady=5, sticky=tk.W)

        self.range_temp_value = tk.Label(self.group1_frame, text="-")
        self.range_temp_value.grid(row=12, column=7, padx=5, pady=5, sticky=tk.W)

        self.status_atbeam_humidity = tk.Label(self.group1_frame, text="Humidity Test/湿度测试: ")
        self.status_atbeam_humidity.grid(row=13, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_humid_label = tk.Label(self.group1_frame, text="Not Yet")
        self.result_humid_label.grid(row=13, column=1, padx=5, pady=5, sticky=tk.W)

        self.atbeam_humid_index = tk.Label(self.group1_frame, text="Device/产品传感器: ")
        self.atbeam_humid_index.grid(row=13, column=2, padx=5, pady=5, sticky=tk.W)

        self.atbeam_humid_value = tk.Label(self.group1_frame, text="AT %")
        self.atbeam_humid_value.grid(row=13, column=3, padx=5, pady=5, sticky=tk.W)

        self.ext_humid_index = tk.Label(self.group1_frame, text="External/外部传感器: ")
        self.ext_humid_index.grid(row=13, column=4, padx=5, pady=5, sticky=tk.W)

        self.ext_humid_value = tk.Label(self.group1_frame, text="Ext %")
        self.ext_humid_value.grid(row=13, column=5, padx=5, pady=5, sticky=tk.W)

        self.range_humid_index = tk.Label(self.group1_frame, text="Range/测试范围(±): ")
        self.range_humid_index.grid(row=13, column=6, padx=5, pady=5, sticky=tk.W)

        self.range_humid_value = tk.Label(self.group1_frame, text="-")
        self.range_humid_value.grid(row=13, column=7, padx=5, pady=5, sticky=tk.W)

        self.status_button_label = tk.Label(self.group1_frame, text="Button Test/按钮测试: ")
        self.status_button_label.grid(row=14, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_button_label = tk.Label(self.group1_frame, text="Not Yet")
        self.result_button_label.grid(row=14, column=1, padx=5, pady=5, sticky=tk.W)

        self.instruction_button_label = tk.Label(self.group1_frame, text="Press Device Button/按产品按钮", font=("Helvetica", 10, "bold"))
        self.instruction_button_label.grid(row=14, column=2, padx=5, pady=5, sticky=tk.W)
        self.instruction_button_label.grid_forget()
        
        # Group 2
        
        self.group2_frame = tk.Frame(self.scrollable_frame, highlightbackground="black", highlightcolor="black", highlightthickness=2, bd=2)
        self.group2_frame.grid(row=10, column=0, padx=10, pady=10, sticky=tk.W)

        self.group2_label = tk.Label(self.group2_frame, text="ESP32S3 Wi-Fi Test/ESP32S3 Wi-Fi测试", font=("Helvetica", 10, "bold"))
        self.group2_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.status_group2_factory_mode = tk.Label(self.group2_frame, text="Factory Mode/工厂模式: ")
        self.status_group2_factory_mode.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_group2_factory_mode = tk.Label(self.group2_frame, text="Not Yet")
        self.result_group2_factory_mode.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        self.status_group2_wifi_softap_label = tk.Label(self.group2_frame, text="Wi-Fi Soft AP: ")
        self.status_group2_wifi_softap_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_group2_wifi_softap = tk.Label(self.group2_frame, text="Not Yet")
        self.result_group2_wifi_softap.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.result_group2_wifi_softap_rssi = tk.Label(self.group2_frame, text="-")
        self.result_group2_wifi_softap_rssi.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)

        self.range_group2_wifi_softap_rssi_index = tk.Label(self.group2_frame, text="Range/测试范围(>): ")
        self.range_group2_wifi_softap_rssi_index.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)

        self.range_group2_wifi_softap_rssi = tk.Label(self.group2_frame, text="-")
        self.range_group2_wifi_softap_rssi.grid(row=2, column=4, padx=5, pady=5, sticky=tk.W)

        self.result_group2_wifi_softap_ssid_index = tk.Label(self.group2_frame, text="SSID: ")
        self.result_group2_wifi_softap_ssid_index.grid(row=2, column=5, padx=5, pady=5, sticky=tk.W)

        self.result_group2_wifi_softap_ssid = tk.Label(self.group2_frame, text="-")
        self.result_group2_wifi_softap_ssid.grid(row=2, column=6, padx=5, pady=5, sticky=tk.W)

        self.status_group2_wifi_station = tk.Label(self.group2_frame, text="Wi-Fi Station: ")
        self.status_group2_wifi_station.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_group2_wifi_station = tk.Label(self.group2_frame, text="Not Yet")
        self.result_group2_wifi_station.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        self.result_group2_wifi_station_rssi = tk.Label(self.group2_frame, text="-")
        self.result_group2_wifi_station_rssi.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)

        self.range_group2_wifi_station_rssi_index = tk.Label(self.group2_frame, text="Range/测试范围(>): ")
        self.range_group2_wifi_station_rssi_index.grid(row=3, column=3, padx=5, pady=5, sticky=tk.W)

        self.range_group2_wifi_station_rssi = tk.Label(self.group2_frame, text="-")
        self.range_group2_wifi_station_rssi.grid(row=3, column=4, padx=5, pady=5, sticky=tk.W)
        
        # Group 3
        self.group3_frame = tk.Frame(self.scrollable_frame, highlightbackground="black", highlightcolor="black", highlightthickness=2, bd=2)
        self.group3_frame.grid(row=9, column=0, padx=10, pady=10, sticky=tk.W)
        
        self.group3_label = tk.Label(self.group3_frame, text="Manual Test/手动测试", font=("Helvetica", 10, "bold"))
        self.group3_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_ir_def = tk.Label(self.group3_frame, text="IR Definition/红外线代码: ")
        self.result_ir_def.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_ir_def_label = tk.Label(self.group3_frame, text="Not Yet")
        self.result_ir_def_label.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.status_rgb_red_label = tk.Label(self.group3_frame, text="Red LED/红灯: ")
        self.status_rgb_red_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_rgb_red_label = tk.Label(self.group3_frame, text="Not Yet")
        self.result_rgb_red_label.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.yes_button_red = ttk.Button(self.group3_frame, text="Yes/有", command=lambda: self.update_yesno_label(self.result_rgb_red_label, "Pass", "green"))
        self.yes_button_red.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        self.yes_button_red.config(state=tk.DISABLED)

        self.no_button_red = ttk.Button(self.group3_frame, text="No/没有", command=lambda: self.update_yesno_label(self.result_rgb_red_label, "Failed", "red"))
        self.no_button_red.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)
        self.no_button_red.config(state=tk.DISABLED)

        self.status_rgb_green_label = tk.Label(self.group3_frame, text="Green LED/绿灯: ")
        self.status_rgb_green_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_rgb_green_label = tk.Label(self.group3_frame, text="Not Yet")
        self.result_rgb_green_label.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        self.yes_button_green = ttk.Button(self.group3_frame, text="Yes/有", command=lambda: self.update_yesno_label(self.result_rgb_green_label, "Pass", "green"))
        self.yes_button_green.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
        self.yes_button_green.config(state=tk.DISABLED)

        self.no_button_green = ttk.Button(self.group3_frame, text="No/没有", command=lambda: self.update_yesno_label(self.result_rgb_green_label, "Failed", "red"))
        self.no_button_green.grid(row=3, column=3, padx=5, pady=5, sticky=tk.W)
        self.no_button_green.config(state=tk.DISABLED)

        self.status_rgb_blue_label = tk.Label(self.group3_frame, text="Blue LED/蓝灯: ")
        self.status_rgb_blue_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_rgb_blue_label = tk.Label(self.group3_frame, text="Not Yet")
        self.result_rgb_blue_label.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        self.yes_button_blue = ttk.Button(self.group3_frame, text="Yes/有", command=lambda: self.update_yesno_label(self.result_rgb_blue_label, "Pass", "green"))
        self.yes_button_blue.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)
        self.yes_button_blue.config(state=tk.DISABLED)

        self.no_button_blue = ttk.Button(self.group3_frame, text="No/没有", command=lambda: self.update_yesno_label(self.result_rgb_blue_label, "Failed", "red"))
        self.no_button_blue.grid(row=4, column=3, padx=5, pady=5, sticky=tk.W)
        self.no_button_blue.config(state=tk.DISABLED)

        self.status_ir_rx_label = tk.Label(self.group3_frame, text="Off LED/关灯(IR Receiver Test/红外线接收器测试): ")
        self.status_ir_rx_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_ir_rx_label = tk.Label(self.group3_frame, text="Not Yet")
        self.result_ir_rx_label.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

        self.yes_button_ir_rx = ttk.Button(self.group3_frame, text="Yes/有", command=lambda: self.update_yesno_label(self.result_ir_rx_label, "Pass", "green"))
        self.yes_button_ir_rx.grid(row=5, column=2, padx=5, pady=5, sticky=tk.W)
        self.yes_button_ir_rx.config(state=tk.DISABLED)

        self.no_button_ir_rx = ttk.Button(self.group3_frame, text="No/没有", command=lambda: self.update_yesno_label(self.result_ir_rx_label, "Failed", "red"))
        self.no_button_ir_rx.grid(row=5, column=3, padx=5, pady=5, sticky=tk.W)
        self.no_button_ir_rx.config(state=tk.DISABLED)
        
        self.ir_led1_label = tk.Label(self.group3_frame, text="IR LED 1/红外线1: ")
        self.ir_led1_label.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_ir_led1 = tk.Label(self.group3_frame, text="Not Yet")
        self.result_ir_led1.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.yes_button_ir_led1 = ttk.Button(self.group3_frame, text="Yes/有", command=lambda: self.update_yesno_label(self.result_ir_led1, "Pass", "green"))
        self.yes_button_ir_led1.grid(row=6, column=2, padx=5, pady=5, sticky=tk.W)
        self.yes_button_ir_led1.config(state=tk.DISABLED)
        
        self.no_button_ir_led1 = ttk.Button(self.group3_frame, text="No/没有", command=lambda: self.update_yesno_label(self.result_ir_led1, "Failed", "red"))
        self.no_button_ir_led1.grid(row=6, column=3, padx=5, pady=5, sticky=tk.W)
        self.no_button_ir_led1.config(state=tk.DISABLED)
        
        self.ir_led2_label = tk.Label(self.group3_frame, text="IR LED 2/红外线2: ")
        self.ir_led2_label.grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_ir_led2 = tk.Label(self.group3_frame, text="Not Yet")
        self.result_ir_led2.grid(row=7, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.yes_button_ir_led2 = ttk.Button(self.group3_frame, text="Yes/有", command=lambda: self.update_yesno_label(self.result_ir_led2, "Pass", "green"))
        self.yes_button_ir_led2.grid(row=7, column=2, padx=5, pady=5, sticky=tk.W)
        self.yes_button_ir_led2.config(state=tk.DISABLED)
        
        self.no_button_ir_led2 = ttk.Button(self.group3_frame, text="No/没有", command=lambda: self.update_yesno_label(self.result_ir_led2, "Failed", "red"))
        self.no_button_ir_led2.grid(row=7, column=3, padx=5, pady=5, sticky=tk.W)
        self.no_button_ir_led2.config(state=tk.DISABLED)
        
        self.ir_led3_label = tk.Label(self.group3_frame, text="IR LED 3/红外线3: ")
        self.ir_led3_label.grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_ir_led3 = tk.Label(self.group3_frame, text="Not Yet")
        self.result_ir_led3.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.yes_button_ir_led3 = ttk.Button(self.group3_frame, text="Yes/有", command=lambda: self.update_yesno_label(self.result_ir_led3, "Pass", "green"))
        self.yes_button_ir_led3.grid(row=8, column=2, padx=5, pady=5, sticky=tk.W)
        self.yes_button_ir_led3.config(state=tk.DISABLED)
        
        self.no_button_ir_led3 = ttk.Button(self.group3_frame, text="No/没有", command=lambda: self.update_yesno_label(self.result_ir_led3, "Failed", "red"))
        self.no_button_ir_led3.grid(row=8, column=3, padx=5, pady=5, sticky=tk.W)
        self.no_button_ir_led3.config(state=tk.DISABLED)
        
        self.ir_led4_label = tk.Label(self.group3_frame, text="IR LED 4/红外线4: ")
        self.ir_led4_label.grid(row=9, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_ir_led4 = tk.Label(self.group3_frame, text="Not Yet")
        self.result_ir_led4.grid(row=9, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.yes_button_ir_led4 = ttk.Button(self.group3_frame, text="Yes/有", command=lambda: self.update_yesno_label(self.result_ir_led4, "Pass", "green"))
        self.yes_button_ir_led4.grid(row=9, column=2, padx=5, pady=5, sticky=tk.W)
        self.yes_button_ir_led4.config(state=tk.DISABLED)
        
        self.no_button_ir_led4 = ttk.Button(self.group3_frame, text="No/没有", command=lambda: self.update_yesno_label(self.result_ir_led4, "Failed", "red"))
        self.no_button_ir_led4.grid(row=9, column=3, padx=5, pady=5, sticky=tk.W)
        self.no_button_ir_led4.config(state=tk.DISABLED)
        
        self.ir_led5_label = tk.Label(self.group3_frame, text="IR LED 5/红外线5: ")
        self.ir_led5_label.grid(row=10, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_ir_led5 = tk.Label(self.group3_frame, text="Not Yet")
        self.result_ir_led5.grid(row=10, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.yes_button_ir_led5 = ttk.Button(self.group3_frame, text="Yes/有", command=lambda: self.update_yesno_label(self.result_ir_led5, "Pass", "green"))
        self.yes_button_ir_led5.grid(row=10, column=2, padx=5, pady=5, sticky=tk.W)
        self.yes_button_ir_led5.config(state=tk.DISABLED)
        
        self.no_button_ir_led5 = ttk.Button(self.group3_frame, text="No/没有", command=lambda: self.update_yesno_label(self.result_ir_led5, "Failed", "red"))
        self.no_button_ir_led5.grid(row=10, column=3, padx=5, pady=5, sticky=tk.W)
        self.no_button_ir_led5.config(state=tk.DISABLED)
        

        # Group 4
        self.group4_frame = tk.Frame(self.scrollable_frame, highlightbackground="black", highlightcolor="black", highlightthickness=2, bd=2)
        self.group4_frame.grid(row=11, column=0, padx=10, pady=10, sticky=tk.W)
        
        self.group4_label = tk.Label(self.group4_frame, text="ESP32H2 Test/ESP32H2测试", font=("Helvetica", 10, "bold"))
        self.group4_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.status_short_header = tk.Label(self.group4_frame, text="Short Header/排针短路: ")
        self.status_short_header.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_short_header = tk.Label(self.group4_frame, text="Not Yet")
        self.result_short_header.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.yes_short_header = ttk.Button(self.group4_frame, text="Yes/有", command=lambda: self.update_yesno_label(self.result_short_header, "Pass", "green"))
        self.yes_short_header.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.yes_short_header.config(state=tk.DISABLED)
        
        self.no_short_header = ttk.Button(self.group4_frame, text="No/没有", command=lambda: self.update_yesno_label(self.result_short_header, "Failed", "red"))
        self.no_short_header.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        self.no_short_header.config(state=tk.DISABLED)
        
        self.status_factory_reset = tk.Label(self.group4_frame, text="Factory Reset/恢复出厂设置: ")
        self.status_factory_reset.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_factory_reset = tk.Label(self.group4_frame, text="Not Yet")
        self.result_factory_reset.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.status_h2_led_check = tk.Label(self.group4_frame, text="ESP32H2 Small LED Test/ESP32H2小红灯测试: ")
        self.status_h2_led_check.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_h2_led_check = tk.Label(self.group4_frame, text="Not Yet")
        self.result_h2_led_check.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.yes_h2_led_check = ttk.Button(self.group4_frame, text="Yes/有", command=lambda: self.update_yesno_label(self.result_h2_led_check, "Pass", "green"))
        self.yes_h2_led_check.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
        self.yes_h2_led_check.config(state=tk.DISABLED)
        
        self.no_h2_led_check = ttk.Button(self.group4_frame, text="No/没有", command=lambda: self.update_yesno_label(self.result_h2_led_check, "Failed", "red"))
        self.no_h2_led_check.grid(row=3, column=3, padx=5, pady=5, sticky=tk.W)
        self.no_h2_led_check.config(state=tk.DISABLED)
        
        self.button_sets = [
            [self.yes_button_red, self.no_button_red],
            [self.yes_button_green, self.no_button_green],
            [self.yes_button_blue, self.no_button_blue],
            [self.yes_button_ir_rx, self.no_button_ir_rx],
            [self.yes_button_ir_led1, self.no_button_ir_led1],
            [self.yes_button_ir_led2, self.no_button_ir_led2],
            [self.yes_button_ir_led3, self.no_button_ir_led3],
            [self.yes_button_ir_led4, self.no_button_ir_led4],
            [self.yes_button_ir_led5, self.no_button_ir_led5],
            [self.yes_short_header, self.no_short_header],
            [self.yes_h2_led_check, self.no_h2_led_check]
        ]
        
        # Print
        self.printer_frame = tk.Frame(self.scrollable_frame, highlightbackground="black", highlightcolor="black", highlightthickness=2, bd=2)
        self.printer_frame.grid(row=12, column=0, padx=10, pady=10, sticky=tk.W)

        self.printer_label = tk.Label(self.printer_frame, text="Sticker Printing/打印贴纸", font=("Helvetica", 10, "bold"))
        self.printer_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.printer_ip_label = tk.Label(self.printer_frame, text="Printer Network IP/打印机网络IP地址:")
        self.printer_ip_label.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.printer_ip_label.grid_forget()

        self.printer_ip_var = tk.StringVar(value="10.10.23.220")
        self.printer_ip_entry = tk.Entry(self.printer_frame, textvariable=self.printer_ip_var)
        self.printer_ip_entry.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.printer_ip_entry.grid_forget()

        self.printer_port_label = tk.Label(self.printer_frame, text="Printer Network Port/打印机网络端口:")
        self.printer_port_label.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.printer_port_label.grid_forget()

        self.printer_port_var = tk.StringVar(value="9100")
        self.printer_port_entry = tk.Entry(self.printer_frame, textvariable=self.printer_port_var)
        self.printer_port_entry.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        self.printer_port_entry.grid_forget()

        self.printer_qrpayload_label = tk.Label(self.printer_frame, text="Matter QR Payload: ")
        self.printer_qrpayload_label.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        self.printer_qrpayload_data_label = tk.Label(self.printer_frame, text="-")
        self.printer_qrpayload_data_label.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)

        self.printer_manualcode_label = tk.Label(self.printer_frame, text="Matter QR Manual Code: ")
        self.printer_manualcode_label.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        self.printer_manualcode_data_label = tk.Label(self.printer_frame, text="-")
        self.printer_manualcode_data_label.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)

        self.printer_status_label = tk.Label(self.printer_frame, text="Print Status: ")
        self.printer_status_label.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

        self.printer_status_data_label = tk.Label(self.printer_frame, text="-")
        self.printer_status_data_label.grid(row=5, column=2, padx=5, pady=5, sticky=tk.W)

        self.printer_print = ttk.Button(self.printer_frame, text="Print/打印", command=lambda: self.send_to_printer())
        self.printer_print.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
        self.printer_print.config(state=tk.DISABLED)

        self.printer_no_print = ttk.Button(self.printer_frame, text="No Print/不打印", command=lambda: self.cancel_to_printer())
        self.printer_no_print.grid(row=6, column=2, padx=5, pady=5, sticky=tk.W)
        self.printer_no_print.config(state=tk.DISABLED)

        
    def update_yesno_label(self, label, text, color):
        label.config(text=text, fg=color, font=("Helvetica", 12, "bold"))

    def enable_configurable_ui(self):
        self.start_button.config(state=tk.NORMAL)
        self.port_dropdown.config(state=tk.NORMAL)
        self.port_dropdown1.config(state=tk.NORMAL)
        self.port_dropdown2.config(state=tk.NORMAL)
        self.baud_dropdown.config(state=tk.NORMAL)
        self.baud_dropdown1.config(state=tk.NORMAL)
        self.baud_dropdown2.config(state=tk.NORMAL)

        self.submit_5V_dmm.config(state=tk.DISABLED)
        self.submit_3_3V_dmm.config(state=tk.DISABLED)
        self.yes_button_red.config(state=tk.DISABLED)
        self.no_button_red.config(state=tk.DISABLED)
        self.yes_button_green.config(state=tk.DISABLED)
        self.no_button_green.config(state=tk.DISABLED)
        self.yes_button_blue.config(state=tk.DISABLED)
        self.no_button_blue.config(state=tk.DISABLED)
        self.yes_button_ir_led1.config(state=tk.DISABLED)
        self.no_button_ir_led1.config(state=tk.DISABLED)
        self.yes_button_ir_led2.config(state=tk.DISABLED)
        self.no_button_ir_led2.config(state=tk.DISABLED)
        self.yes_button_ir_led3.config(state=tk.DISABLED)
        self.no_button_ir_led3.config(state=tk.DISABLED)
        self.yes_button_ir_led4.config(state=tk.DISABLED)
        self.no_button_ir_led4.config(state=tk.DISABLED)
        self.yes_button_ir_led5.config(state=tk.DISABLED)
        self.no_button_ir_led5.config(state=tk.DISABLED)
        self.yes_short_header.config(state=tk.DISABLED)
        self.no_short_header.config(state=tk.DISABLED)
        self.yes_h2_led_check.config(state=tk.DISABLED)
        self.no_h2_led_check.config(state=tk.DISABLED)
        self.printer_print.config(state=tk.DISABLED)
        self.printer_no_print.config(state=tk.DISABLED)


    def disable_configurable_ui(self):
        self.start_button.config(state=tk.DISABLED)
        self.port_dropdown.config(state=tk.DISABLED)
        self.port_dropdown1.config(state=tk.DISABLED)
        self.port_dropdown2.config(state=tk.DISABLED)
        self.baud_dropdown.config(state=tk.DISABLED)
        self.baud_dropdown1.config(state=tk.DISABLED)
        self.baud_dropdown2.config(state=tk.DISABLED)

        self.submit_5V_dmm.config(state=tk.DISABLED)
        self.submit_3_3V_dmm.config(state=tk.DISABLED)
        self.yes_button_red.config(state=tk.DISABLED)
        self.no_button_red.config(state=tk.DISABLED)
        self.yes_button_green.config(state=tk.DISABLED)
        self.no_button_green.config(state=tk.DISABLED)
        self.yes_button_blue.config(state=tk.DISABLED)
        self.no_button_blue.config(state=tk.DISABLED)
        self.yes_button_ir_led1.config(state=tk.DISABLED)
        self.no_button_ir_led1.config(state=tk.DISABLED)
        self.yes_button_ir_led2.config(state=tk.DISABLED)
        self.no_button_ir_led2.config(state=tk.DISABLED)
        self.yes_button_ir_led3.config(state=tk.DISABLED)
        self.no_button_ir_led3.config(state=tk.DISABLED)
        self.yes_button_ir_led4.config(state=tk.DISABLED)
        self.no_button_ir_led4.config(state=tk.DISABLED)
        self.yes_button_ir_led5.config(state=tk.DISABLED)
        self.no_button_ir_led5.config(state=tk.DISABLED)
        self.yes_short_header.config(state=tk.DISABLED)
        self.no_short_header.config(state=tk.DISABLED)
        self.yes_h2_led_check.config(state=tk.DISABLED)
        self.no_h2_led_check.config(state=tk.DISABLED)
        self.printer_print.config(state=tk.DISABLED)
        self.printer_no_print.config(state=tk.DISABLED)


    def load_test_script(self):
        ini_file_path = askopenfilename(title="Select .ini file", filetypes=[("INI files", "*.ini")])
        if not ini_file_path:
            return

        self.loadtTestScript = LoadTestScript(ini_file_path)
        with open(ini_file_path, 'r') as file:
            content = file.read()
            print(content)

    def check_factory_flag(self):
        flag_value = self.serialCom.get_factory_flag()
        print(f"Factory Flag: {flag_value}")

    def start_test(self):
        global factroy_app_version
        global device_data
        global orderNum_label
        global macAddress_label
        global serialID_label
        global certID_label
        global secureCertPartition_label
        global commissionableDataPartition_label
        global qrCode_label
        global manualCode_label
        global discriminator_label
        global passcode_label
        global orderNum_data
        global macAddress_esp32s3_data
        global serialID_data
        global certID_data
        global secureCertPartition_data
        global commissionableDataPartition_data
        global qrCode_data
        global manualCode_data
        global discriminator_data
        global passcode_data

        global ini_file_name
        global device_data_file_path
        global script_dir

        # Check in the specified directory
        ini_file_path = os.path.join(script_dir, ini_file_name)

        if not os.path.exists(ini_file_path):
            logger.error(f"{ini_file_name} not found in the specified directory: {script_dir}")
            return

        # Proceed to load and process the INI file
        self.loadTestScript = LoadTestScript(ini_file_path)

        config = configparser.ConfigParser()
        config.read(ini_file_path)

        esp32s3_erase_flash_enable = config.get("erase_flash_esp32s3", "erase_flash_esp32s3_enable")
        esp32s3_start_addr = config.get("erase_flash_esp32s3", "erase_flash_esp32s3_start_address")
        esp32s3_end_addr = config.get("erase_flash_esp32s3", "erase_flash_esp32s3_end_address")
        esp32h2_erase_flash_enable = config.get("erase_flash_esp32h2", "erase_flash_esp32h2_enable")
        esp32h2_start_addr = config.get("erase_flash_esp32h2", "erase_flash_esp32h2_start_address")
        esp32h2_end_addr = config.get("erase_flash_esp32h2", "erase_flash_esp32h2_end_address")

        esp32s3_port = config.get("flash_firmware_esp32s3", "flash_firmware_esp32s3_port")
        esp32s3_baud = config.get("flash_firmware_esp32s3", "flash_firmware_esp32s3_baud")
        esp32s3_bootloader_address = config.get("flash_firmware_esp32s3", "flash_firmware_esp32s3_bootloader_address")
        esp32s3_partition_table_address = config.get("flash_firmware_esp32s3", "flash_firmware_esp32s3_partition_table_address")
        esp32s3_ota_data_initial_address = config.get("flash_firmware_esp32s3", "flash_firmware_esp32s3_ota_data_initial_address")
        esp32s3_fw_address = config.get("flash_firmware_esp32s3", "flash_firmware_esp32s3_address")
        esp32s3_use_esptool = config.get("flash_firmware_esp32s3", "flash_firmware_esp32s3_use_esptool")
        esp32s3_port = self.port_var.get()
        esp32s3_port = "/dev/ttyUSB0"
        esp32s3_baud = int(self.baud_var.get())

        esp32h2_port = config.get("flash_firmware_esp32h2", "flash_firmware_esp32h2_port")
        esp32h2_baud = config.get("flash_firmware_esp32h2", "flash_firmware_esp32h2_baud")
        esp32h2_bootloader_address = config.get("flash_firmware_esp32h2", "flash_firmware_esp32h2_bootloader_address")
        esp32h2_partition_table_address = config.get("flash_firmware_esp32h2", "flash_firmware_esp32h2_partition_table_address")
        esp32h2_fw_address = config.get("flash_firmware_esp32h2", "flash_firmware_esp32h2_address")
        esp32h2_use_esptool = config.get("flash_firmware_esp32h2", "flash_firmware_esp32h2_use_esptool")
        esp32h2_port = self.port_var2.get()
        esp32h2_baud = int(self.baud_var2.get())

        esp32s3_securecert_partition = config.get("flash_dac_esp32s3", "flash_dac_esp32s3_secure_cert_partition")
        esp32s3_data_provider_partition = config.get("flash_dac_esp32s3", "flash_dac_esp32s3_data_provider_partition")
        esp32s3_dac_use_esptool = config.get("flash_dac_esp32s3", "flash_dac_esp32s3_use_esptool")

        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     future_s3 = executor.submit(self.read_s3_mac_address, esp32s3_port, esp32s3_baud)
        #     future_h2 = executor.submit(self.read_h2_mac_address, esp32h2_port, esp32h2_baud)

        #     # Wait for both futures to complete
        #     concurrent.futures.wait([future_s3, future_h2])

        self.read_mac_address_label.config(fg="blue")
        self.read_mac_address_label.grid()

        print("Read ESP32S3 MAC Address")
        self.read_s3_mac_address(esp32s3_port, esp32s3_baud)

        print("System Sleep")
        time.sleep(5)

        print("Retrieve ESP32S3 MAC Address")
        esp32s3_mac_add = self.flashFw.retrieve_esp32s3_mac_address()

        print("Retrieve order number selected from ui")
        orderNumber = self.order_number_dropdown.get()

        print("Retrieve device data")
        device_data = self.retrieve_device_data(str(device_data_file_path), str(orderNumber), str(esp32s3_mac_add))
        if device_data == "":
            self.task1_thread_failed.set()
            print("No available data")
            messagebox.showwarning("Warning", "No data available in database")
            return True
        else:
            pass

        print("Parse device data")
        self.parse_device_data(str(device_data), str(esp32s3_mac_add))

        print("Initialize logging")
        if self.initialize_logging(str(esp32s3_mac_add), str(serialID_data)) == True:
            self.task1_thread_failed.set()
            print("Fail to initialize logging")
            return True
        else:
            pass

        logger.info(f"Factory App Version: {factroy_app_version}")
        print(f"Factory App Version: {factroy_app_version}")
        logger.info("Test 1 Start")
        print("Test 1 Start")
        logger.info(f"Below are information extracted based on ESP32S3 MAC Address")
        logger.info(f"{orderNum_label}: {orderNum_data}")
        logger.info(f"{macAddress_label}: {macAddress_esp32s3_data}")
        logger.info(f"{serialID_label}: {serialID_data}")
        logger.info(f"{certID_label}: {certID_data}")
        logger.info(f"{secureCertPartition_label}: {secureCertPartition_data}")
        logger.info(f"{commissionableDataPartition_label}: {commissionableDataPartition_data}")
        logger.info(f"{qrCode_label}: {qrCode_data}")
        logger.info(f"{manualCode_label}: {manualCode_data}")
        logger.info(f"{discriminator_label}: {discriminator_data}")
        logger.info(f"{passcode_label}: {passcode_data}")

        print(f"Below are information extracted based on ESP32S3 MAC Address")
        print(f"{orderNum_label}: {orderNum_data}")
        print(f"{macAddress_label}: {macAddress_esp32s3_data}")
        print(f"{serialID_label}: {serialID_data}")
        print(f"{certID_label}: {certID_data}")
        print(f"{secureCertPartition_label}: {secureCertPartition_data}")
        print(f"{commissionableDataPartition_label}: {commissionableDataPartition_data}")
        print(f"{qrCode_label}: {qrCode_data}")
        print(f"{manualCode_label}: {manualCode_data}")
        print(f"{discriminator_label}: {discriminator_data}")
        print(f"{passcode_label}: {passcode_data}")

        logger.info("Read ESP32S3 Mac Address")
        print("Read ESP32S3 Mac Address")
        self.record_s3_mac_address(macAddress_esp32s3_data)

        logger.info("Read ESP32H2 MAC Address")
        print("Read ESP32H2 MAC Address")
        self.read_h2_mac_address(esp32h2_port, esp32h2_baud)

        self.read_mac_address_label.config(fg="black")
        self.read_mac_address_label.grid()

        self.status_flashing_fw.config(fg="blue")
        self.status_flashing_fw.grid()

        # if "flash" in config:
        #     logger.info("Flashing firmware and certificate")
        #     port = config.get("flash", "port")
        #     baud = config.get("flash", "baud")
        #     logger.info(f"Port: {port}, Baud: {baud}")
        #     self.flashFw.export_esp_idf_path()
        #     self.flash_s3_firmware(port, baud)
            # self.flash_cert(port)

        # if "flash_firmware_esp32s3" in config:
        logger.info("Flashing esp32s3 and esp32h2 firmware")
        print("Flashing esp32s3 and esp32h2 firmware")

        logger.info(f"Erase Flash ESP32S3: {esp32s3_erase_flash_enable}")
        logger.info(f"Erase Flash ESP32S3 Start Address: {esp32s3_start_addr}")
        logger.info(f"Erase Flash ESP32S3 End Address: {esp32s3_end_addr}")

        logger.info(f"Erase Flash ESP32H2: {esp32h2_erase_flash_enable}")
        logger.info(f"Erase Flash ESP32H2 Start Address: {esp32h2_start_addr}")
        logger.info(f"Erase Flash ESP32H2 End Address: {esp32h2_end_addr}")

        print(f"Erase Flash ESP32S3: {esp32s3_erase_flash_enable}")
        print(f"Erase Flash ESP32S3 Start Address: {esp32s3_start_addr}")
        print(f"Erase Flash ESP32S3 End Address: {esp32s3_end_addr}")

        print(f"Erase Flash ESP32H2: {esp32h2_erase_flash_enable}")
        print(f"Erase Flash ESP32H2 Start Address: {esp32h2_start_addr}")
        print(f"Erase Flash ESP32H2 End Address: {esp32h2_end_addr}")

        logger.info(f"Flashing ESP32S3 firmware, Port: {esp32s3_port}, Baud: {esp32s3_baud}")
        logger.info(f"ESP32S3 Bootloader Address: {esp32s3_bootloader_address}")
        logger.info(f"ESP32S3 Partition Table Address: {esp32s3_partition_table_address}")
        logger.info(f"ESP32S3 OTA Data Initial Address: {esp32s3_ota_data_initial_address}")
        logger.info(f"ESP32S3 Firmware Address: {esp32s3_fw_address}")
        logger.info(f"ESP32S3 Use ESPTOOL: {esp32s3_use_esptool}")

        print(f"Flashing ESP32S3 firmware, Port: {esp32s3_port}, Baud: {esp32s3_baud}")
        print(f"ESP32S3 Bootloader Address: {esp32s3_bootloader_address}")
        print(f"ESP32S3 Partition Table Address: {esp32s3_partition_table_address}")
        print(f"ESP32S3 OTA Data Initial Address: {esp32s3_ota_data_initial_address}")
        print(f"ESP32S3 Firmware Address: {esp32s3_fw_address}")
        print(f"ESP32S3 Use ESPTOOL: {esp32s3_use_esptool}")

        logger.info(f"Flashing ESP32H2 firmware, Port: {esp32h2_port}, Baud: {esp32h2_baud}")
        logger.info(f"ESP32H2 Bootloader Address: {esp32h2_bootloader_address}")
        logger.info(f"ESP32H2 Partition Table Address: {esp32h2_partition_table_address}")
        logger.info(f"ESP32H2 Firmware Address: {esp32h2_fw_address}")
        logger.info(f"ESP32H2 Use ESPTOOL: {esp32h2_use_esptool}")

        print(f"Flashing ESP32H2 firmware, Port: {esp32h2_port}, Baud: {esp32h2_baud}")
        print(f"ESP32H2 Bootloader Address: {esp32h2_bootloader_address}")
        print(f"ESP32H2 Partition Table Address: {esp32h2_partition_table_address}")
        print(f"ESP32H2 Firmware Address: {esp32h2_fw_address}")
        print(f"ESP32H2 Use ESPTOOL: {esp32h2_use_esptool}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_s3 = executor.submit(self.erase_flash_esp32s3, esp32s3_erase_flash_enable, esp32s3_use_esptool, esp32s3_port, esp32s3_baud, esp32s3_start_addr, esp32s3_end_addr)
            future_h2 = executor.submit(self.erase_flash_esp32h2, esp32h2_erase_flash_enable, esp32h2_use_esptool, esp32h2_port, esp32h2_baud, esp32h2_start_addr, esp32h2_end_addr)

            # Wait for both futures to complete
            concurrent.futures.wait([future_s3, future_h2])

        time.sleep(1)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_s3 = executor.submit(self.flash_s3_firmware, esp32s3_use_esptool, esp32s3_port, esp32s3_baud, esp32s3_bootloader_address, esp32s3_partition_table_address, esp32s3_ota_data_initial_address, esp32s3_fw_address)
            future_h2 = executor.submit(self.flash_h2_firmware, esp32h2_use_esptool, esp32h2_port, esp32h2_baud, esp32h2_bootloader_address, esp32h2_partition_table_address, esp32h2_fw_address)

            # Wait for both futures to complete
            concurrent.futures.wait([future_s3, future_h2])

        time.sleep(1)

        self.status_flashing_fw.config(fg="black")
        self.status_flashing_fw.grid()

        self.status_flashing_cert.config(fg="blue")
        self.status_flashing_cert.grid()

        secureCertPartition_data_array = secureCertPartition_data.split('_')
        device_uuid = secureCertPartition_data_array[0]
        print(device_uuid)

        logger.info("Flashing esp32s3 certificate")
        print("Flashing esp32s3 certificate")
        logger.info(f"Flashing esp32s3 certificate, Port: {esp32s3_port}, Baud: {esp32s3_baud}")
        logger.info(f"ESP32S3 Secure Cert Partition Address: {esp32s3_securecert_partition}")
        logger.info(f"ESP32S3 Data Provider Partition Address: {esp32s3_data_provider_partition}")
        logger.info(f"ESP32S3 DAC Use ESPTOOL: {esp32s3_dac_use_esptool}")

        print(f"Flashing esp32s3 certificate, Port: {esp32s3_port}, Baud: {esp32s3_baud}")
        print(f"ESP32S3 Secure Cert Partition Address: {esp32s3_securecert_partition}")
        print(f"ESP32S3 Data Provider Partition Address: {esp32s3_data_provider_partition}")
        print(f"ESP32S3 Use ESPTOOL: {esp32s3_data_provider_partition}")
        print(f"ESP32S3 DAC Use ESPTOOL: {esp32s3_dac_use_esptool}")
        # self.flashFw.get_esptool_device_mac_address(selected_port, selected_baud)
        self.flashCertificate(esp32s3_dac_use_esptool, esp32s3_port, esp32s3_baud, serialID_label, serialID_data, secureCertPartition_label, device_uuid, macAddress_label, macAddress_esp32s3_data, esp32s3_securecert_partition, esp32s3_data_provider_partition)
        # self.flashCertificate(esp32s3_port, serialID_data, self.selected_cert_id)
        # self.flashCertificate("/dev/ttyUSB0", self.selected_cert_id)

        # time.sleep(10)
        # time.sleep(20)
        # time.sleep(1)

        self.status_flashing_cert.config(fg="black")
        self.status_flashing_cert.grid()

        # # export the ESP-IDF path
        # self.flashFw.export_esp_idf_path()

        logger.info("Test 1 Completed")
        print("Test 1 Completed")

        # Signal that task 1 is complete
        self.task1_completed.set()

        return False

    def start_task1_thread(self):
        self.task1_thread = threading.Thread(target=self.start_test)
        self.task1_thread.start()
        print("start_task1_thread")
        return self.task1_thread
        # return self.start_test()

    def start_test2(self):
        global factroy_app_version
        global device_data
        global orderNum_label
        global macAddress_label
        global serialID_label
        global certID_label
        global secureCertPartition_label
        global commissionableDataPartition_label
        global qrCode_label
        global manualCode_label
        global discriminator_label
        global passcode_label
        global orderNum_data
        global macAddress_esp32s3_data
        global serialID_data
        global certID_data
        global secureCertPartition_data
        global commissionableDataPartition_data
        global qrCode_data
        global manualCode_data
        global discriminator_data
        global passcode_data

        global ini_file_name
        global script_dir

        global break_printer

        # Check in the specified directory
        ini_file_path = os.path.join(script_dir, ini_file_name)

        if not os.path.exists(ini_file_path):
            logger.error(f"{ini_file_name} not found in the specified directory: {script_dir}")
            return

        # Proceed to load and process the INI file
        self.loadTestScript = LoadTestScript(ini_file_path)

        config = configparser.ConfigParser()
        config.read(ini_file_path)

        # Wait for task 1 to complete
        while not self.task1_completed.is_set():
            if self.task1_thread_failed.is_set():
                logger.info("System Error occured on Test 1, unable to proceed.")
                print("System Error occured on Test 1, unable to proceed.")
                self.fail_ui()
                self.enable_configurable_ui()
                messagebox.showwarning("Warning", "Test Stop!")
                return True
            else:
                # logger.info(f"Waiting for Test 1 to complete")
                # print(f"Waiting for Test 1 to complete")
                time.sleep(1)

        logger.info("Test 2 Start")
        print("Test 2 Start")

        self.status_factory_mode.config(fg="blue")
        self.status_factory_mode.grid()

        if "factory_esp32s3" in config:
            logger.info("Entering factory mode")
            print("Entering factory mode")

            # try:
            esp32s3_port = self.port_var.get()
            esp32s3_port = "/dev/ttyUSB0"
            esp32s3_baud = int(self.baud_var.get())

            esp32s3_factroy_port = self.port_var1.get()
            esp32s3_factory_baud = int(self.baud_var1.get())

            esp32h2_port = self.port_var2.get()
            esp32h2_baud = int(self.baud_var2.get())

            logger.info("Reset Factory Mode Flag")
            print("Reset Factory Mode Flag")
            self.serialCom.reset_flag_device_factory_mode()

            logger.info("Open esp32s3 Factory Port")
            print("Open esp32s3 Factory Port")
            logger.info(f"factory Port: {esp32s3_factroy_port}, Baud: {esp32s3_factory_baud}")
            self.serialCom.open_serial_port(esp32s3_factroy_port, esp32s3_factory_baud)

            logger.info("Reboot esp32s3 and esp32h2")
            print("Reboot esp32s3 and esp32h2")
            logger.info(f"Reboot esp32s3, Port: {esp32s3_port}, Baud: {esp32s3_baud}")
            logger.info(f"Reboot esp32h2, Port: {esp32h2_port}, Baud: {esp32h2_baud}")
            self.reboot_h2(True, esp32h2_port, esp32h2_baud)
            # self.reboot_s3(False, False, esp32s3_port, esp32s3_baud)
            self.reboot_s3(esp32s3_port, esp32s3_baud)


            logger.info("Start Wait 3")
            print("Start Wait 3")
            time.sleep(3)
            logger.info("Finish Wait 3")
            print("Finish Wait 3")

            # except configparser.NoOptionError:
            #     logger.error("Port not found in the INI file")
            #     print("Port not found in the INI file")

        # This is to update ui if the device successfully enter into factory mode
        if self.result_factory_mode_label.cget("text") == "Not Yet":
            self.result_factory_mode_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        else:
            pass

        self.status_factory_mode.config(fg="black")
        self.status_factory_mode.grid()

        time.sleep(1)

        self.status_read_device_mac.config(fg="blue")
        self.status_read_device_mac.grid()

        # Split by characters!! Capital and small letters
        if "read_mac_address" in config:
            logger.info("Read MAC Address")
            print("Read MAC Address")
            # self.get_device_mac()
            command = config.get("read_mac_address", "read_mac_address_command")
            self.send_command(command + "\r\n")
            logger.info(f"Read MAC Address Command: {command}")
            print(f"Read MAC Address Command: {command}")
            logger.info(f"Reference MAC Address: {macAddress_esp32s3_data}")
            print(f"Reference MAC Address: {macAddress_esp32s3_data}")
            time.sleep(self.step_delay) # This delay is to allow so time for serial com to respond
            if self.read_device_mac.cget("text").lower() == str(macAddress_esp32s3_data).lower():
                self.result_read_device_mac.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                logger.info("Read MAC Address: Pass")
                print("Read MAC Address: Pass")
            else:
                self.result_read_device_mac.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("Read MAC Address: Failed")
                print("Read MAC Address: Failed")
                # self.close_serial_port()
                self.enable_configurable_ui()
                messagebox.showwarning("Warning", "Test Stop!")
                return True

        self.status_read_device_mac.config(fg="black")
        self.status_read_device_mac.grid()

        self.status_read_prod_name.config(fg="blue")
        self.status_read_prod_name.grid()

        if "write_product_name" in config:
            logger.info("Write Product Name")
            print("Write Product Name")
            command = config.get("write_product_name", "write_product_name_command")
            self.send_command(command + "\r\n")
            logger.info(f"Write Product Name Command: {command}")
            print(f"Write Product Name Command: {command}")
            time.sleep(self.step_delay)

        if "read_product_name" in config:
            logger.info("Read Product Name")
            print("Read Product Name")
            command = config.get("read_product_name", "read_product_name_command")
            self.send_command(command + "\r\n")
            logger.info(f"Read Product Name Command: {command}")
            print(f"Read Product Name Command: {command}")
            data = config.get("read_product_name", "read_product_name_data")
            logger.info(f"Reference Product Name: {data}")
            print(f"Reference Product Name: {data}")
            time.sleep(self.step_delay) # This delay is to allow so time for serial com to respond
            if self.read_prod_name.cget("text") == str(data):
                self.result_read_prod_name.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                logger.info("Product Name: Pass")
                print("Product Name: Pass")
            else:
                self.result_read_prod_name.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("Product Name: Failed")
                print("Product Name: Failed")

        self.status_read_prod_name.config(fg="black")
        self.status_read_prod_name.grid()

        self.status_write_device_sn.config(fg="blue")
        self.status_write_device_sn.grid()

        if "write_serial_number" in config:
            logger.info("Write Serial Number")
            print("Write Serial Number")
            # self.send_serial_number(serialID_data)
            command = config.get("write_serial_number", "write_serial_number_command")
            command = command + str(serialID_data)
            self.send_command(command + "\r\n")
            logger.info(f"Write Serial Number Command: {command}")
            print(f"Write Serial Number Command: {command}")
            time.sleep(self.step_delay)

        if "read_serial_number" in config:
            logger.info("Read Serial Number")
            print("Read Serial Number")
            # self.send_serial_number(serialID_data)
            command = config.get("read_serial_number", "read_serial_number_command")
            self.send_command(command + "\r\n")
            logger.info(f"Read Serial Number Command: {command}")
            print(f"Read Serial Number Command: {command}")
            time.sleep(self.step_delay) # This delay is to allow so time for serial com to respond
            if self.read_device_sn.cget("text") == str(serialID_data):
                self.result_write_serialnumber.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                logger.info("Write Device S/N: Pass")
                print("Write Device S/N: Pass")
            else:
                self.result_write_serialnumber.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("Write Device S/N: Failed")
                print("Write Device S/N: Failed")

        self.status_write_device_sn.config(fg="black")
        self.status_write_device_sn.grid()

        self.status_write_device_mtqr.config(fg="blue")
        self.status_write_device_mtqr.grid()

        if "write_matter_qr" in config:
            logger.info("Write Matter QR String")
            print("Write Matter QR String")
            # self.send_mqtr(qrCode_data)
            command = config.get("write_matter_qr", "write_matter_qr_command")
            command = command + str(qrCode_data)
            self.send_command(command + "\r\n")
            logger.info(f"Write Matter QR String Command: {command}")
            print(f"Write Matter QR String Command: {command}")
            time.sleep(self.step_delay)

        if "read_matter_qr" in config:
            logger.info("Read Matter QR String")
            print("Read Matter QR String")
            # self.send_mqtr(qrCode_data)
            command = config.get("read_matter_qr", "read_matter_qr_command")
            self.send_command(command + "\r\n")
            logger.info(f"Read Matter QR String Command: {command}")
            print(f"Read Matter QR String Command: {command}")
            time.sleep(self.step_delay) # This delay is to allow so time for serial com to respond
            if self.read_device_mtqr.cget("text") == str(qrCode_data):
                self.result_write_mtqr.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                logger.info("Write Device Matter QR: Pass")
                print("Write Device Matter QR: Pass")
            else:
                self.result_write_mtqr.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("Write Device Matter QR: Failed")
                print("Write Device Matter QR: Failed")

        self.status_write_device_mtqr.config(fg="black")
        self.status_write_device_mtqr.grid()

        self.result_ir_def.config(fg="blue")
        self.result_ir_def.grid()

        if "write_ir_definition" in config:
            logger.info("Write IR Definition")
            print("Write IR Definition")
            command = config.get("write_ir_definition", "write_ir_definition_command")
            self.send_command(command + "\r\n")
            logger.info(f"Write IR Definition Command: {command}")
            print(f"Write IR Definition Command: {command}")
            time.sleep(5) # Need to have long wait time due to long command

        if "read_ir_definition" in config:
            logger.info("Read IR Definition")
            print("Read IR Definition")
            command = config.get("read_ir_definition", "read_ir_definition_command")
            self.send_command(command + "\r\n")
            logger.info(f"Read IR Definition Command: {command}")
            print(f"Read IR Definition Command: {command}")
            time.sleep(5)  # Need to have long wait time due to long command
            if self.result_ir_def_label.cget("text") == "Pass":
                # self.result_ir_def_label.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                logger.info("IR Definition Test: Pass")
                print("IR Definition Test: Pass")
            else:
                self.result_ir_def_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("IR Definition: Failed")
                print("IR Definition Test: Failed")

        self.result_ir_def.config(fg="black")
        self.result_ir_def.grid()

        self.status_save_device_data_label.config(fg="blue")
        self.status_save_device_data_label.grid()

        if "save_device_data" in config:
            logger.info("Save Device Data")
            print("Save Device Data")
            command = config.get("save_device_data", "save_device_data_command")
            logger.info(f"Save Device Data Command: {command}")
            print(f"Save Device Data Command: {command}")
            data_array = command.split(';')
            data = data_array[1]
            logger.info(f"Extracted data: {data}")
            print(f"Extracted data: {data}")
            self.send_command(command + "\r\n")
            time.sleep(10)
            if self.read_save_device_data_label.cget("text") == str(data.strip()):
                self.result_save_device_data_label.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                logger.info("Save Device Data: Pass")
                print("Save Device Data: Pass")
            else:
                self.result_save_device_data_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("Save Device Data: Failed")
                print("Save Device Data: Failed")

        self.status_save_device_data_label.config(fg="black")
        self.status_save_device_data_label.grid()

        self.status_5v_test.config(fg="blue")
        self.status_5v_test.grid()

        if "5v_test" in config:
            logger.info("5V Test")
            print("5V Test")
            # Test Loop
            self.submit_5V_dmm.config(state=tk.NORMAL)
            auto_mode = config.get("5v_test", "5v_test_auto_mode")
            logger.info(f"5V Test Auto Mode: {auto_mode}")
            print(f"5V Test Auto Mode: {auto_mode}")
            loop_seconds = config.get("5v_test", "5v_test_duration_seconds")
            logger.info(f"5V Test Time in seconds: {loop_seconds}")
            print(f"5V Test Time in seconds: {loop_seconds}")
            test_range = config.get("5v_test", "5v_test_range")
            logger.info(f"5V Test Range: {test_range} V")
            print(f"5V Test Range: {test_range}V")
            self.range_value_5V_dmm.config(text=f"{test_range}", fg="black", font=("Helvetica", 10, "bold"))
            if auto_mode =="True":
                self.dmmReader.select_device(0)
                self.dmm_reader_5V_value_manual(self.input_5V_dmm)
            label_appear = True
            start_time = time.time()
            while time.time() - start_time < float(loop_seconds):
                if label_appear == True:
                    self.status_5v_test.config(fg="blue")
                    self.status_5v_test.grid()
                    label_appear = False
                else:
                    self.status_5v_test.config(fg="black")
                    self.status_5v_test.grid()
                    label_appear = True

                if self.result_5v_test.cget("text") != "Not Yet":
                    break
                time.sleep(0.5)
            self.status_5v_test.config(fg="black")
            self.status_5v_test.grid()
            if self.dmm_5V_reader.cget("text") == "-":
                self.result_5v_test.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("5V Test: Failed")
                print("5V Test: Failed")
            else:
                # self.result_5v_test.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                # logger.info("5V Test: Pass")
                # print("5V Test: Pass")
                pass

        self.status_5v_test.config(fg="black")
        self.status_5v_test.grid()

        self.status_3_3v_test.config(fg="blue")
        self.status_3_3v_test.grid()

        if "3.3v_test" in config:
            logger.info("3.3V Test")
            print("3.3V Test")
            # Test Loop
            self.submit_5V_dmm.config(state=tk.DISABLED)
            self.submit_3_3V_dmm.config(state=tk.NORMAL)
            auto_mode = config.get("3.3v_test", "3.3v_test_auto_mode")
            logger.info(f"3.3V Test Auto Mode: {auto_mode}")
            print(f"3.3V Test Auto Mode: {auto_mode}")
            loop_seconds = config.get("3.3v_test", "3.3v_test_duration_seconds")
            logger.info(f"3.3V Test Time in seconds: {loop_seconds}")
            print(f"3.3V Test Time in seconds: {loop_seconds}")
            test_range = config.get("3.3v_test", "3.3v_test_range")
            logger.info(f"3.3V Test Range: {test_range}")
            print(f"3.3V Test Range: {test_range}")
            self.range_value_3_3V_dmm.config( text=f"{test_range}", fg="black", font=("Helvetica", 10, "bold"))
            if auto_mode =="True":
                self.dmmReader.select_device(1)
                self.dmm_reader_3_3V_value_manual(self.input_3_3V_dmm)
            label_appear = True
            start_time = time.time()
            while time.time() - start_time < float(loop_seconds):
                if label_appear == True:
                    self.status_3_3v_test.config(fg="blue")
                    self.status_3_3v_test.grid()
                    label_appear = False
                else:
                    self.status_3_3v_test.config(fg="black")
                    self.status_3_3v_test.grid()
                    label_appear = True

                if self.result_3_3v_test.cget("text") != "Not Yet":
                    break
                time.sleep(0.5)
            self.status_3_3v_test.config(fg="black")
            self.status_3_3v_test.grid()
            if self.dmm_3_3V_reader.cget("text") == "-":
                self.result_3_3v_test.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("3.3V Test: Failed")
                print("3.3V Test: Failed")
            else:
                # self.result_3_3v_test.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                # logger.info("3.3V Test: Pass")
                # print("3.3V Test: Pass")
                pass

        self.status_3_3v_test.config(fg="black")
        self.status_3_3v_test.grid()

        self.status_atbeam_temp.config(fg="blue")
        self.status_atbeam_temp.grid()

        if "atbeam_temp" in config:
            self.submit_3_3V_dmm.config(state=tk.DISABLED)
            logger.info("Read ATBeam Temperature")
            print("Read ATBeam Temperature")
            self.get_atbeam_temp()
            # time.sleep(self.step_delay)

        if "temp_compare" in config:
            logger.info("Compare Temperature")
            print("Compare Temperature")
            test_range = config.get("temp_compare", "temp_compare_range")
            logger.info(f"Temperature Test Range: {test_range}")
            print(f"Temperature Test Range: {test_range}")
            self.range_temp_value.config(text=f"{test_range}", fg="black", font=("Helvetica", 10, "bold"))
            self.read_temp_aht20()
            time.sleep(self.step_delay)
            if self.result_temp_label.cget("text") == "Pass":
                # self.result_temp_label.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                logger.info("Temperature Test: Pass")
                print("Temperature Test: Pass")
            else:
                self.result_temp_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("Temperature Test: Failed")
                print("Temperature Test: Failed")

        self.status_atbeam_temp.config(fg="black")
        self.status_atbeam_temp.grid()

        self.status_atbeam_humidity.config(fg="blue")
        self.status_atbeam_humidity.grid()

        if "atbeam_humid" in config:
            logger.info("Read ATBeam Humidity")
            print("Read ATBeam Humidity")
            self.get_atbeam_humid()
            # time.sleep(self.step_delay)
            self.manual_test = True

        if "humid_compare" in config:
            logger.info("Compare Humidity")
            print("Compare Humidity")
            test_range = config.get("humid_compare", "humid_compare_range")
            logger.info(f"Humidity Test Range: {test_range}")
            print(f"Humidity Test Time Range: {test_range}")
            self.range_humid_value.config(text=f"{test_range}", fg="black", font=("Helvetica", 10, "bold"))
            self.read_humid_aht20()
            # self.result_group2_factory_mode.config(text="Pass", fg="green", font=("Helvetica", 10, "normal"))
            # self.factory_flag = self.serialCom.device_factory_mode
            # self.factory_flag = False
            time.sleep(self.step_delay)
            if self.result_humid_label.cget("text") == "Pass":
                # self.result_humid_label.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                logger.info("Humidity Test: Pass")
                print("Humidity Test: Pass")
            else:
                self.result_humid_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("Humidity Test: Failed")
                print("Humidity Test: Failed")

        self.status_atbeam_humidity.config(fg="black")
        self.status_atbeam_humidity.grid()

        if "button" in config:
            logger.info("Button Test")
            print("Button Test")
            # Test Loop
            loop_seconds = config.get("button", "button_test_duration_seconds")
            logger.info(f"Button Test Time in seconds: {loop_seconds}")
            print(f"Button Test Time in seconds: {loop_seconds}")
            label_appear = True
            start_time = time.time()
            # while time.time() - start_time < float(loop_seconds):
            while True:
                if label_appear == True:
                    self.status_button_label.config(fg="blue")
                    self.status_button_label.grid()
                    # self.instruction_button_label.grid(row=14, column=2, padx=5, pady=5, sticky=tk.W)
                    label_appear = False
                else:
                    self.status_button_label.config(fg="black")
                    self.status_button_label.grid()
                    # self.instruction_button_label.grid_forget()
                    label_appear = True

                if self.result_button_label.cget("text") != "Not Yet":
                    break
                time.sleep(0.5)
            self.status_button_label.config(fg="black")
            self.status_button_label.grid()
            # self.instruction_button_label.grid_forget()
            if self.result_button_label.cget("text") == "Pass":
                # self.result_button_label.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                logger.info("Button Test: Pass")
                print("Button Test: Pass")
            else:
                self.result_button_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("Button Test: Failed")
                print("Button Test: Failed")

        if "manual_test" in config:
            if self.result_factory_mode_label.cget("text") == "Pass":
                redLed = config.get("manual_test", "redLed_command")
                greenLed = config.get("manual_test", "greenLed_command")
                blueLed = config.get("manual_test", "blueLed_command")
                offLed = config.get("manual_test", "offLed_command")
                ir_receive = config.get("manual_test", "ir_receive_command")
                ir_send = config.get("manual_test", "ir_send_command")
                loop_seconds = config.get("manual_test", "manual_test_duration_seconds")
                logger.info(f"Manual Test Time in seconds: {loop_seconds}")
                print(f"Manual Test Time in seconds: {loop_seconds}")
                # logger.debug(f"Red LED: {redLed}, Green LED: {greenLed}, Blue LED: {blueLed}, IR Send: {ir_send}")
                logger.info("Manual Test Loop Start")
                print("Manual Test Loop Start")
                # self.enable_frame(self.group3_frame)
                step_counter = 0
                start_time = time.time()
                # Manual test loop
                # while time.time() - start_time < float(loop_seconds):
                while True:
                    # if self.manual_test and self.factory_flag == True:
                    #     logger.debug(self.factory_flag)
                    match step_counter:
                        case 0:
                            if self.result_rgb_red_label.cget("text") == "Not Yet":
                                self.status_rgb_red_label.config(fg="blue")
                                self.status_rgb_red_label.grid()
                                self.yes_button_red.config(state=tk.NORMAL)
                                self.no_button_red.config(state=tk.NORMAL)
                                self.send_command(redLed + "\r\n")
                                # time.sleep(1)
                            elif self.result_rgb_red_label.cget("text") == "Pass":
                                logger.info("Red LED: Pass")
                                print("Red LED: Pass")
                                self.status_rgb_red_label.config(fg="black")
                                self.status_rgb_red_label.grid()
                                self.yes_button_red.config(state=tk.DISABLED)
                                self.no_button_red.config(state=tk.DISABLED)
                                step_counter += 1
                            elif self.result_rgb_red_label.cget("text") == "Failed":
                                logger.info("Red LED: Failed")
                                print("Red LED: Failed")
                                self.status_rgb_red_label.config(fg="black")
                                self.status_rgb_red_label.grid()
                                self.yes_button_red.config(state=tk.DISABLED)
                                self.no_button_red.config(state=tk.DISABLED)
                                step_counter += 1

                        case 1:
                            if self.result_rgb_green_label.cget("text") == "Not Yet":
                                self.status_rgb_green_label.config(fg="blue")
                                self.status_rgb_green_label.grid()
                                self.yes_button_green.config(state=tk.NORMAL)
                                self.no_button_green.config(state=tk.NORMAL)
                                self.send_command(greenLed + "\r\n")
                                # time.sleep(1)
                            elif self.result_rgb_green_label.cget("text") == "Pass":
                                logger.info("Green LED: Pass")
                                print("Green LED: Pass")
                                self.status_rgb_green_label.config(fg="black")
                                self.status_rgb_green_label.grid()
                                self.yes_button_green.config(state=tk.DISABLED)
                                self.no_button_green.config(state=tk.DISABLED)
                                step_counter += 1
                            elif self.result_rgb_green_label.cget("text") == "Failed":
                                logger.info("Green LED: Failed")
                                print("Green LED: Failed")
                                self.status_rgb_green_label.config(fg="black")
                                self.status_rgb_green_label.grid()
                                self.yes_button_green.config(state=tk.DISABLED)
                                self.no_button_green.config(state=tk.DISABLED)
                                step_counter += 1

                        case 2:
                            if self.result_rgb_blue_label.cget("text") == "Not Yet":
                                self.status_rgb_blue_label.config(fg="blue")
                                self.status_rgb_blue_label.grid()
                                self.yes_button_blue.config(state=tk.NORMAL)
                                self.no_button_blue.config(state=tk.NORMAL)
                                self.send_command(blueLed + "\r\n")
                                # time.sleep(1)
                            elif self.result_rgb_blue_label.cget("text") == "Pass":
                                logger.info("Blue LED: Pass")
                                print("Blue LED: Pass")
                                self.status_rgb_blue_label.config(fg="black")
                                self.status_rgb_blue_label.grid()
                                self.yes_button_blue.config(state=tk.DISABLED)
                                self.no_button_blue.config(state=tk.DISABLED)
                                step_counter += 1
                            elif self.result_rgb_blue_label.cget("text") == "Failed":
                                logger.info("Blue LED: Failed")
                                print("Blue LED: Failed")
                                self.status_rgb_blue_label.config(fg="black")
                                self.status_rgb_blue_label.grid()
                                self.yes_button_blue.config(state=tk.DISABLED)
                                self.no_button_blue.config(state=tk.DISABLED)
                                step_counter += 1

                        case 3:
                            # self.send_command(offLed + "\r\n") #The LED will be turn off by device when IR Rx is successful
                            self.send_command(ir_receive + "\r\n")
                            time.sleep(2)
                            self.send_command(ir_send + "\r\n")
                            if self.result_ir_rx_label.cget("text") == "Not Yet":
                                self.status_ir_rx_label.config(fg="blue")
                                self.status_ir_rx_label.grid()
                                self.yes_button_ir_rx.config(state=tk.NORMAL)
                                self.no_button_ir_rx.config(state=tk.NORMAL)
                            elif self.result_ir_rx_label.cget("text") == "Pass":
                                logger.info("IR Receiver/Turn off LED: Pass")
                                print("IR Receiver/Turn off LED: Pass")
                                self.status_ir_rx_label.config(fg="black")
                                self.status_ir_rx_label.grid()
                                self.yes_button_ir_rx.config(state=tk.DISABLED)
                                self.no_button_ir_rx.config(state=tk.DISABLED)
                                step_counter += 1
                            elif self.result_ir_rx_label.cget("text") == "Failed":
                                logger.info("IR Receiver/Turn off LED: Failed")
                                print("IR Receiver/Turn off LED: Failed")
                                self.status_ir_rx_label.config(fg="black")
                                self.status_ir_rx_label.grid()
                                self.yes_button_ir_rx.config(state=tk.DISABLED)
                                self.no_button_ir_rx.config(state=tk.DISABLED)
                                step_counter += 1

                        case 4:
                            self.send_command(ir_send + "\r\n")
                            if self.result_ir_led1.cget("text") == "Not Yet":
                                self.ir_led1_label.config(fg="blue")
                                self.ir_led1_label.grid()
                                self.yes_button_ir_led1.config(state=tk.NORMAL)
                                self.no_button_ir_led1.config(state=tk.NORMAL)
                            elif self.result_ir_led1.cget("text") == "Pass":
                                logger.info("IR LED 1: Pass")
                                print("IR LED 1: Pass")
                                self.ir_led1_label.config(fg="black")
                                self.ir_led1_label.grid()
                                self.yes_button_ir_led1.config(state=tk.DISABLED)
                                self.no_button_ir_led1.config(state=tk.DISABLED)
                                step_counter += 1
                            elif self.result_ir_led1.cget("text") == "Failed":
                                logger.info("IR LED 1: Failed")
                                print("IR LED 1: Failed")
                                self.ir_led1_label.config(fg="black")
                                self.ir_led1_label.grid()
                                self.yes_button_ir_led1.config(state=tk.DISABLED)
                                self.no_button_ir_led1.config(state=tk.DISABLED)
                                step_counter += 1

                        case 5:
                            self.send_command(ir_send + "\r\n")
                            if self.result_ir_led2.cget("text") == "Not Yet":
                                self.ir_led2_label.config(fg="blue")
                                self.ir_led2_label.grid()
                                self.yes_button_ir_led2.config(state=tk.NORMAL)
                                self.no_button_ir_led2.config(state=tk.NORMAL)
                            elif self.result_ir_led2.cget("text") == "Pass":
                                logger.info("IR LED 2: Pass")
                                print("IR LED 2: Pass")
                                self.ir_led2_label.config(fg="black")
                                self.ir_led2_label.grid()
                                self.yes_button_ir_led2.config(state=tk.DISABLED)
                                self.no_button_ir_led2.config(state=tk.DISABLED)
                                step_counter += 1
                            elif self.result_ir_led2.cget("text") == "Failed":
                                logger.info("IR LED 2: Failed")
                                print("IR LED 2: Failed")
                                self.ir_led2_label.config(fg="black")
                                self.ir_led2_label.grid()
                                self.yes_button_ir_led2.config(state=tk.DISABLED)
                                self.no_button_ir_led2.config(state=tk.DISABLED)
                                step_counter += 1

                        case 6:
                            self.send_command(ir_send + "\r\n")
                            if self.result_ir_led3.cget("text") == "Not Yet":
                                self.ir_led3_label.config(fg="blue")
                                self.ir_led3_label.grid()
                                self.yes_button_ir_led3.config(state=tk.NORMAL)
                                self.no_button_ir_led3.config(state=tk.NORMAL)
                            elif self.result_ir_led3.cget("text") == "Pass":
                                logger.info("IR LED 3: Pass")
                                print("IR LED 3: Pass")
                                self.ir_led3_label.config(fg="black")
                                self.ir_led3_label.grid()
                                self.yes_button_ir_led3.config(state=tk.DISABLED)
                                self.no_button_ir_led3.config(state=tk.DISABLED)
                                step_counter += 1
                            elif self.result_ir_led3.cget("text") == "Failed":
                                logger.info("IR LED 3: Failed")
                                print("IR LED 3: Failed")
                                self.ir_led3_label.config(fg="black")
                                self.ir_led3_label.grid()
                                self.yes_button_ir_led3.config(state=tk.DISABLED)
                                self.no_button_ir_led3.config(state=tk.DISABLED)
                                step_counter += 1

                        case 7:
                            self.send_command(ir_send + "\r\n")
                            if self.result_ir_led4.cget("text") == "Not Yet":
                                self.ir_led4_label.config(fg="blue")
                                self.ir_led4_label.grid()
                                self.yes_button_ir_led4.config(state=tk.NORMAL)
                                self.no_button_ir_led4.config(state=tk.NORMAL)
                            elif self.result_ir_led4.cget("text") == "Pass":
                                logger.info("IR LED 4: Pass")
                                print("IR LED 4: Pass")
                                self.ir_led4_label.config(fg="black")
                                self.ir_led4_label.grid()
                                self.yes_button_ir_led4.config(state=tk.DISABLED)
                                self.no_button_ir_led4.config(state=tk.DISABLED)
                                step_counter += 1
                            elif self.result_ir_led4.cget("text") == "Failed":
                                logger.info("IR LED 4: Failed")
                                print("IR LED 4: Failed")
                                self.ir_led4_label.config(fg="black")
                                self.ir_led4_label.grid()
                                self.yes_button_ir_led4.config(state=tk.DISABLED)
                                self.no_button_ir_led4.config(state=tk.DISABLED)
                                step_counter += 1

                        case 8:
                            self.send_command(ir_send + "\r\n")
                            if self.result_ir_led5.cget("text") == "Not Yet":
                                self.ir_led5_label.config(fg="blue")
                                self.ir_led5_label.grid()
                                self.yes_button_ir_led5.config(state=tk.NORMAL)
                                self.no_button_ir_led5.config(state=tk.NORMAL)
                            elif self.result_ir_led5.cget("text") == "Pass":
                                logger.info("IR LED 5: Pass")
                                print("IR LED 5: Pass")
                                self.ir_led5_label.config(fg="black")
                                self.ir_led5_label.grid()
                                self.yes_button_ir_led5.config(state=tk.DISABLED)
                                self.no_button_ir_led5.config(state=tk.DISABLED)
                                step_counter += 1
                            elif self.result_ir_led5.cget("text") == "Failed":
                                logger.info("IR LED 5: Failed")
                                print("IR LED 5: Failed")
                                self.ir_led5_label.config(fg="black")
                                self.ir_led5_label.grid()
                                self.yes_button_ir_led5.config(state=tk.DISABLED)
                                self.no_button_ir_led5.config(state=tk.DISABLED)
                                step_counter += 1

                        case _: #this is a whildcard case, matching any other value
                            break
                    if step_counter <= 2:
                        time.sleep(1)
                    elif step_counter >= 9:
                        time.sleep(1)
                    else:
                        time.sleep(2)

                    # else:
                    #     logger.error("Manual test loop not found in the INI file or conditions not met")
                    #     print("Manual test loop not found in the INI file or conditions not met")
                    #     break
                self.yes_button_red.config(state=tk.DISABLED)
                self.no_button_red.config(state=tk.DISABLED)
                self.yes_button_green.config(state=tk.DISABLED)
                self.no_button_green.config(state=tk.DISABLED)
                self.yes_button_blue.config(state=tk.DISABLED)
                self.no_button_blue.config(state=tk.DISABLED)
                self.yes_button_ir_rx.config(state=tk.DISABLED)
                self.no_button_ir_rx.config(state=tk.DISABLED)
                self.yes_button_ir_led1.config(state=tk.DISABLED)
                self.no_button_ir_led1.config(state=tk.DISABLED)
                self.yes_button_ir_led2.config(state=tk.DISABLED)
                self.no_button_ir_led2.config(state=tk.DISABLED)
                self.yes_button_ir_led3.config(state=tk.DISABLED)
                self.no_button_ir_led3.config(state=tk.DISABLED)
                self.yes_button_ir_led4.config(state=tk.DISABLED)
                self.no_button_ir_led4.config(state=tk.DISABLED)
                self.yes_button_ir_led5.config(state=tk.DISABLED)
                self.no_button_ir_led5.config(state=tk.DISABLED)

                self.status_rgb_red_label.config(fg="black")
                self.status_rgb_red_label.grid()
                self.status_rgb_green_label.config(fg="black")
                self.status_rgb_green_label.grid()
                self.status_rgb_blue_label.config(fg="black")
                self.status_rgb_blue_label.grid()
                self.status_ir_rx_label.config(fg="black")
                self.status_ir_rx_label.grid()
                self.ir_led1_label.config(fg="black")
                self.ir_led1_label.grid()
                self.ir_led2_label.config(fg="black")
                self.ir_led2_label.grid()
                self.ir_led3_label.config(fg="black")
                self.ir_led3_label.grid()
                self.ir_led4_label.config(fg="black")
                self.ir_led4_label.grid()
                self.ir_led5_label.config(fg="black")
                self.ir_led5_label.grid()

                if self.result_rgb_red_label.cget("text") == "Pass":
                    # self.result_rgb_red_label.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                    logger.info("Red LED: Pass")
                    print("Red: Pass")
                else:
                    self.result_rgb_red_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                    logger.info("Red: Failed")
                    print("Red: Failed")

                if self.result_rgb_green_label.cget("text") == "Pass":
                    # self.result_rgb_green_label.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                    logger.info("Green LED: Pass")
                    print("Green: Pass")
                else:
                    self.result_rgb_green_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                    logger.info("Green: Failed")
                    print("Green: Failed")

                if self.result_rgb_blue_label.cget("text") == "Pass":
                    # self.result_rgb_blue_label.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                    logger.info("Blue LED: Pass")
                    print("Blue: Pass")
                else:
                    self.result_rgb_blue_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                    logger.info("Blue: Failed")
                    print("Blue: Failed")

                if self.result_ir_rx_label.cget("text") == "Pass":
                    # self.result_ir_rx_label.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                    logger.info("IR Receiver: Pass")
                    print("IR Receiver: Pass")
                else:
                    self.result_ir_rx_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                    logger.info("IR Receiver: Failed")
                    print("IR Receiver: Failed")

                if self.result_ir_led1.cget("text") == "Pass":
                    # self.result_ir_led1.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                    logger.info("IR LED 1: Pass")
                    print("IR LED 1: Pass")
                else:
                    self.result_ir_led1.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                    logger.info("IR LED 1: Failed")
                    print("IR LED 1: Failed")

                if self.result_ir_led2.cget("text") == "Pass":
                    # self.result_ir_led2.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                    logger.info("IR LED 2: Pass")
                    print("IR LED 2: Pass")
                else:
                    self.result_ir_led2.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                    logger.info("IR LED 2: Failed")
                    print("IR LED 2: Failed")

                if self.result_ir_led3.cget("text") == "Pass":
                    # self.result_ir_led3.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                    logger.info("IR LED 3: Pass")
                    print("IR LED 3: Pass")
                else:
                    self.result_ir_led3.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                    logger.info("IR LED 3: Failed")
                    print("IR LED 3: Failed")

                if self.result_ir_led4.cget("text") == "Pass":
                    # self.result_ir_led4.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                    logger.info("IR LED 4: Pass")
                    print("IR LED 4: Pass")
                else:
                    self.result_ir_led4.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                    logger.info("IR LED 4: Failed")
                    print("IR LED 4: Failed")

                if self.result_ir_led5.cget("text") == "Pass":
                    # self.result_ir_led5.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                    logger.info("IR LED 5: Pass")
                    print("IR LED 5: Pass")
                else:
                    self.result_ir_led5.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                    logger.info("IR LED 5: Failed")
                    print("IR LED 5: Failed")

                logger.info("Manual Test Loop Completed")
                print("Manual Test Loop Completed")
            else:
                self.result_rgb_red_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                self.result_rgb_green_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                self.result_rgb_blue_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                self.result_ir_rx_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                self.result_ir_def_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                self.result_ir_led1.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                self.result_ir_led2.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                self.result_ir_led3.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                self.result_ir_led4.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                self.result_ir_led5.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("Manual Test Loop Failed")
                print("Manual Test Loop Failed")
            time.sleep(self.step_delay)

        self.status_group2_factory_mode.config(fg="blue")
        self.status_group2_factory_mode.grid()

        if "factory_esp32s3" in config:
            logger.info("Entering factory mode")
            print("Entering factory mode")

            # try:
            esp32s3_port = self.port_var.get()
            esp32s3_port = "/dev/ttyUSB0"
            esp32s3_baud = int(self.baud_var.get())

            esp32s3_factroy_port = self.port_var1.get()
            esp32s3_factory_baud = int(self.baud_var1.get())

            esp32h2_port = self.port_var2.get()
            esp32h2_baud = int(self.baud_var2.get())

            logger.info("Reset Factory Mode Flag")
            print("Reset Factory Mode Flag")
            self.serialCom.reset_flag_device_factory_mode()

            # logger.info("Open esp32s3 Factory Port")
            # print("Open esp32s3 Factory Port")
            # logger.info(f"factory Port: {esp32s3_factroy_port}, Baud: {esp32s3_factory_baud}")
            # self.serialCom.open_serial_port(esp32s3_factroy_port, esp32s3_factory_baud)

            logger.info("Reboot esp32s3 and esp32h2")
            print("Reboot esp32s3 and esp32h2")
            logger.info(f"Reboot esp32s3, Port: {esp32s3_port}, Baud: {esp32s3_baud}")
            logger.info(f"Reboot esp32h2, Port: {esp32h2_port}, Baud: {esp32h2_baud}")
            self.reboot_h2(True, esp32h2_port, esp32h2_baud)
            # self.reboot_s3(False, False, esp32s3_port, esp32s3_baud)
            self.reboot_s3(esp32s3_port, esp32s3_baud)


            logger.info("Start Wait 3")
            print("Start Wait 3")
            time.sleep(3)
            logger.info("Finish Wait 3")
            print("Finish Wait 3")

            # except configparser.NoOptionError:
            #     logger.error("Port not found in the INI file")
            #     print("Port not found in the INI file")

        if "read_mac_address" in config:
            logger.info("Read MAC Address")
            print("Read MAC Address")
            # self.get_device_mac()
            command = config.get("read_mac_address", "read_mac_address_command")
            self.send_command(command + "\r\n")
            logger.info(f"Read MAC Address Command: {command}")
            print(f"Read MAC Address Command: {command}")
            logger.info(f"Reference MAC Address: {macAddress_esp32s3_data}")
            print(f"Reference MAC Address: {macAddress_esp32s3_data}")
            time.sleep(self.step_delay) # This delay is to allow so time for serial com to respond

        self.status_group2_factory_mode.config(fg="black")
        self.status_group2_factory_mode.grid()

        self.status_group2_wifi_softap_label.config(fg="blue")
        self.status_group2_wifi_softap_label.grid()

        if "wifi_softap" in config:
            # self.factory_flag = self.serialCom.device_factory_mode
            # self.factory_flag = True
            # logger.debug(f"Factory Flag: {self.factory_flag}")
            time.sleep(3)
            
            # HTTP Req Device State
            self.serialCom.http_response()
            
            time.sleep(3)
            logger.info("Start Wi-Fi Soft AP Test")
            print("Start Wi-Fi Soft AP Test")
            test_range = config.get("wifi_softap", "wifi_softap_test_rssi_range")
            logger.info(f"Wi-Fi SoftAP RSSI Test Range: {test_range}")
            print(f"Wi-Fi SoftAP RSSI Time Range: {test_range}")
            self.range_group2_wifi_softap_rssi.config(text=f"{test_range} dBm", fg="black", font=("Helvetica", 10, "bold"))
            self.wifi_scanning(test_range)
            time.sleep(self.step_delay)
            if self.result_group2_wifi_softap.cget("text") == "Pass":
                # self.result_group2_wifi_softap_rssi.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                logger.info("Wi-Fi Soft AP: Pass")
                print("Wi-Fi Soft AP: Pass")
            else:
                self.result_group2_wifi_softap.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("Wi-Fi Soft AP: Failed")
                print("Wi-Fi Soft AP: Failed")

        self.status_group2_wifi_softap_label.config(fg="black")
        self.status_group2_wifi_softap_label.grid()

        self.status_group2_wifi_station.config(fg="blue")
        self.status_group2_wifi_station.grid()

        logger.info("Reset Factory Mode Flag")
        print("Reset Factory Mode Flag")
        self.serialCom.reset_flag_device_factory_mode()

        if "wifi_station" in config:
            logger.info("Start Wi-Fi Station Test")
            print("Start Wi-Fi Station Test")
            test_range = config.get("wifi_station", "wifi_station_test_rssi_range")
            wifi_ssid_command = config.get("wifi_station", "wifi_station_inputssid_command")
            logger.info(f"Wi-Fi Station RSSI Test Range: {test_range}")
            print(f"Wi-Fi Station RSSI Time Range: {test_range}")
            self.range_group2_wifi_station_rssi.config(text=f"{test_range} dBm", fg="black", font=("Helvetica", 10, "bold"))
            self.send_command(wifi_ssid_command + "\r\n")
            logger.info(f"Wi-Fi Station Command: {wifi_ssid_command}")
            print(f"Wi-Fi Station Command: {wifi_ssid_command}")
            time.sleep(2)
            connect_wifi_command = config.get("wifi_station" , "wifi_station_connectwifi_command")
            self.send_command(connect_wifi_command + "\r\n")
            logger.info(f"Wi-Fi Station Command: {connect_wifi_command}")
            print(f"Wi-Fi Station Command: {connect_wifi_command}")
            time.sleep(5) #Allow time for the device to connect to wifi
            wifi_rssi_command = config.get("wifi_station" , "wifi_station_rssi_command")
            self.send_command(wifi_rssi_command + "\r\n")
            logger.info(f"Wi-Fi Station RSSI Command: {wifi_rssi_command}")
            print(f"Wi-Fi Station RSSI Command: {wifi_rssi_command}")
            time.sleep(2)
            self.get_atbeam_rssi(test_range)
            time.sleep(self.step_delay)
            if self.result_group2_wifi_station.cget("text") == "Pass":
                self.result_group2_wifi_station.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                logger.info("Wi-Fi Station: Pass")
                print("Wi-Fi Station: Pass")
            else:
                self.result_group2_wifi_station.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("Wi-Fi Station: Failed")
                print("Wi-Fi Station: Failed")

        self.status_group2_wifi_station.config(fg="black")
        self.status_group2_wifi_station.grid()

        if "esp32h2_header_pin" in config:
            logger.info("ESP32H2 Header Pin")
            print("ESP32H2 header Pin")
            # Test Loop
            loop_seconds = config.get("esp32h2_header_pin", "esp32h2_header_pin_test_duration_seconds")
            logger.info(f"ESP32H2 Header Pin Test Time in seconds: {loop_seconds}")
            print(f"ESP32H2 Header Pin Test Time in seconds: {loop_seconds}")
            self.yes_short_header.config(state=tk.NORMAL)
            self.no_short_header.config(state=tk.NORMAL)
            label_appear = True
            start_time = time.time()
            # while time.time() - start_time < float(loop_seconds):
            while True:
                if label_appear == True:
                    self.status_short_header.config(fg="blue")
                    self.status_short_header.grid()
                    label_appear = False
                else:
                    self.status_short_header.config(fg="black")
                    self.status_short_header.grid()
                    label_appear = True

                if self.result_short_header.cget("text") != "Not Yet":
                    break
                time.sleep(0.5)
            self.status_short_header.config(fg="black")
            self.status_short_header.grid()
            if self.result_short_header.cget("text") == "Pass":
                # self.result_short_header.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                logger.info("ESP32H2 Header Pin: Pass")
                print("ESP32H2 Header Pin: Pass")
            else:
                self.result_short_header.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("ESP32H2 Header Pin: Failed")
                print("ESP32H2 Header Pin: Failed")
            self.yes_short_header.config(state=tk.DISABLED)
            self.no_short_header.config(state=tk.DISABLED)

        # self.status_factory_reset.config(fg="blue")
        # self.status_factory_reset.grid()

        # if "factory_reset" in config:
        #     logger.info("Factory Reset Device")
        #     print("Factory Reset Device")
        #     command = config.get("factory_reset", "factory_reset_command")
        #     self.send_command(command + "\r\n")
        #     logger.info(f"Factory Reset Device: {command}")
        #     print(f"Factory Reset Device: {command}")
        #     time.sleep(self.step_delay)
        #     if self.result_factory_reset.cget("text") == "Pass":
        #         # self.result_factory_reset.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
        #         logger.info("Factory Reset: Pass")
        #         print("Factory Reset: Pass")
        #     else:
        #         self.result_factory_reset.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        #         logger.info("Factory Reset: Failed")
        #         print("Factory Reset: Failed")

        # self.status_factory_reset.config(fg="black")
        # self.status_factory_reset.grid()

        if "factory_esp32s3" in config:
            logger.info("Entering factory mode")
            print("Entering factory mode")

            # try:
            esp32s3_port = self.port_var.get()
            esp32s3_port = "/dev/ttyUSB0"
            esp32s3_baud = int(self.baud_var.get())

            esp32s3_factroy_port = self.port_var1.get()
            esp32s3_factory_baud = int(self.baud_var1.get())

            esp32h2_port = self.port_var2.get()
            esp32h2_baud = int(self.baud_var2.get())

            logger.info("Reset Factory Mode Flag")
            print("Reset Factory Mode Flag")
            self.serialCom.reset_flag_device_factory_mode()

            # logger.info("Open esp32s3 Factory Port")
            # print("Open esp32s3 Factory Port")
            # logger.info(f"factory Port: {esp32s3_factroy_port}, Baud: {esp32s3_factory_baud}")
            # self.serialCom.open_serial_port(esp32s3_factroy_port, esp32s3_factory_baud)

            logger.info("Reboot esp32s3 and esp32h2")
            print("Reboot esp32s3 and esp32h2")
            logger.info(f"Reboot esp32s3, Port: {esp32s3_port}, Baud: {esp32s3_baud}")
            logger.info(f"Reboot esp32h2, Port: {esp32h2_port}, Baud: {esp32h2_baud}")
            self.reboot_h2(True, esp32h2_port, esp32h2_baud)
            # self.reboot_s3(False, False, esp32s3_port, esp32s3_baud)
            self.reboot_s3(esp32s3_port, esp32s3_baud)


            logger.info("Start Wait 3")
            print("Start Wait 3")
            time.sleep(3)
            logger.info("Finish Wait 3")
            print("Finish Wait 3")

            # except configparser.NoOptionError:
            #     logger.error("Port not found in the INI file")
            #     print("Port not found in the INI file")

        if "esp32h2_led" in config:
            logger.info("ESP32H2 LED Test")
            print("ESP32H2 LED Test")
            # Test Loop
            loop_seconds = config.get("esp32h2_led", "esp32h2_led_test_duration_seconds")
            logger.info(f"ESP32H2 LED Test Time in seconds: {loop_seconds}")
            print(f"ESP32H2 LED Test Time in seconds: {loop_seconds}")
            self.yes_h2_led_check.config(state=tk.NORMAL)
            self.no_h2_led_check.config(state=tk.NORMAL)
            label_appear = True
            start_time = time.time()
            # while time.time() - start_time < float(loop_seconds):
            while True:
                if label_appear == True:
                    self.status_h2_led_check.config(fg="blue")
                    self.status_h2_led_check.grid()
                    label_appear = False
                else:
                    self.status_h2_led_check.config(fg="black")
                    self.status_h2_led_check.grid()
                    label_appear = True

                if self.result_h2_led_check.cget("text") != "Not Yet":
                    break
                time.sleep(0.5)
            self.status_h2_led_check.config(fg="black")
            self.status_h2_led_check.grid()
            if self.result_h2_led_check.cget("text") == "Pass":
                # self.result_h2_led_check.config(text="Pass", fg="green", font=("Helvetica", 10, "bold"))
                logger.info("ESP32H2 Small LED: Pass")
                print("ESP32H2 Small LED: Pass")
            else:
                self.result_h2_led_check.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
                logger.info("ESP32H2 Small LED: Failed")
                print("ESP32H2 Small LED: Failed")
            self.yes_h2_led_check.config(state=tk.DISABLED)
            self.no_h2_led_check.config(state=tk.DISABLED)

        if "print_sticker" in config:
            logger.info("Sticker Printing")
            print("Sticker Printing")
            # Test Loop
            loop_seconds = config.get("print_sticker", "print_sticker_duration_seconds")
            logger.info(f"Print Sticker Time in seconds: {loop_seconds}")
            print(f"Print Sticker Time in seconds: {loop_seconds}")
            auto_mode = config.get("print_sticker", "print_sticker_auto_mode")
            logger.info(f"Print Sticker Auto Mode: {auto_mode}")
            print(f"Print Sticker Auto Mode: {auto_mode}")
            self.printer_qrpayload_data_label.config(text=f"{qrCode_data}")
            self.printer_manualcode_data_label.config(text=f"{manualCode_data}")
            self.printer_print.config(state=tk.NORMAL)
            self.printer_no_print.config(state=tk.NORMAL)
            if auto_mode == "True":
                self.send_to_printer()
            else:
                pass
            label_appear = True
            start_time = time.time()
            break_printer = 0
            # while time.time() - start_time < float(loop_seconds):
            while True:
                if label_appear == True:
                    self.printer_label.config(fg="blue")
                    self.printer_label.grid()
                    label_appear = False
                else:
                    self.printer_label.config(fg="black")
                    self.printer_label.grid()
                    label_appear = True

                if break_printer == 1:
                    break

                time.sleep(0.5)
            self.printer_label.config(fg="black")
            self.printer_label.grid()


        # except Exception as e:
        #     logger.error(f"An error occurred during the test: {e}")

        # finally:
        # Ensure all log entries are flushed
        logging.shutdown()

        # # Define source and destination paths
        # source_path = 'app.log'
        # destination_directory = '/usr/src/app/my-s3-bucket'
        # destination_path = os.path.join(destination_directory, 'app.log')

        # # Ensure the destination directory exists
        # logger.debug(f'Creating directory if it does not exist: {destination_directory}')
        # os.makedirs(destination_directory, exist_ok=True)

        # # Copy the log file to the destination
        # logger.debug(f'Copying log file from {source_path} to {destination_path}')
        # shutil.copy2(source_path, destination_path)

        # # Rename the copied log file with a timestamp or device serial number
        # log_name = self.read_device_sn.cget("text")
        # renamed_file_path = os.path.join(destination_directory, f'{log_name}.log')
        # logger.debug(f'Renaming copied log file to {renamed_file_path}')
        # os.rename(destination_path, renamed_file_path)
        # logger.info(f'Log file copied and renamed to {renamed_file_path}')
        # # self.process_reset_device()

        # self.close_serial_port()

        logger.info("Test 2 Completed")
        print("Test 2 Completed")

        # self.reset_tasks()
        self.enable_configurable_ui()

        messagebox.showinfo("Information", "Test Completed")
        return False

    def start_task2_thread(self):
        self.task2_thread = threading.Thread(target=self.start_test2)
        self.task2_thread.start()
        print("start_task2_thread")
        return self.task2_thread
        # self.start_test2()

    def combine_tasks(self):

        selected_order_number = self.order_number_dropdown_list.get()
        if selected_order_number:
            self.reset_ui()
            self.reset_tasks()
            # self.stop_event.clear()  # Clear the stop event before starting the tasks

            self.disable_configurable_ui()

            self.clear_task_threads()

            task1_thread = self.start_task1_thread()
            task2_thread = self.start_task2_thread()
            # task1_thread.join()
            # task2_thread.join()

            # logger.info("System Stop and Ready for next action")
            print("System Stop and Ready for next action")
        else:
            messagebox.showwarning("Warning", "Select order number")

    def clear_task_threads(self):
        self.stop_event.set()  # Signal the threads to stop
        if self.task1_thread and self.task1_thread.is_alive():
            self.task1_thread.join(timeout=10)  # Add a timeout to join to prevent hanging
        if self.task2_thread and self.task2_thread.is_alive():
            self.task2_thread.join(timeout=10)  # Add a timeout to join to prevent hanging

    def reset_tasks(self):
        # self.clear_task_threads()
        self.task1_completed.clear()
        self.task1_thread_failed.clear()
        self.stop_event.clear()

    def process_reset_device(self):
        logger.info("Resetting device")
        self.send_command("FF:3;factoryRST\r\n")
        logger.info("Test Completed")
        self.reset_tasks()

    def fail_ui(self):
        logger.info("Resetting tasks")
        # self.serialCom.close_serial_port()
        self.result_flashing_fw_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_flashing_fw_h2_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_flashing_cert_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_factory_mode_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_read_device_mac.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.read_device_mac.config(text="-", fg="black", font=("Helvetica", 10, "bold"))
        self.result_write_serialnumber.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.read_device_sn.config(text="-", fg="black", font=("Helvetica", 10, "bold"))
        self.result_write_mtqr.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.read_device_mtqr.config(text="-", fg="black", font=("Helvetica", 10, "bold"))
        self.result_save_device_data_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.read_save_device_data_label.config(text="-", fg="black", font=("Helvetica", 10, "bold"))
        self.result_3_3v_test.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.range_value_3_3V_dmm.config(text="-", fg="black", font=("Helvetica", 10, "bold"))
        self.result_5v_test.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.range_value_5V_dmm.config(text="-", fg="black", font=("Helvetica", 10, "bold"))
        self.result_temp_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.range_temp_value.config(text="-", fg="black", font=("Helvetica", 10, "bold"))
        self.result_humid_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.range_humid_value.config(text="-", fg="black", font=("Helvetica", 10, "bold"))
        self.result_rgb_red_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        # self.yes_button_red.config(state='bold')
        # self.no_button_red.config(state='bold')
        self.result_rgb_green_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        # self.yes_button_green.config(state='bold')
        # self.no_button_green.config(state='bold')
        self.result_rgb_blue_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        # self.yes_button_blue.config(state='bold')
        # self.no_button_blue.config(state='bold')
        self.result_button_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.dmm_3_3V_reader.config(text="-", fg="black", font=("Helvetica", 10, "bold"))
        self.dmm_5V_reader.config(text="-", fg="black", font=("Helvetica", 10, "bold"))
        self.atbeam_temp_value.config(text="AT °C", fg="black", font=("Helvetica", 10, "bold"))
        self.ext_temp_value.config(text="Ext °C", fg="black", font=("Helvetica", 10, "bold"))
        self.atbeam_humid_value.config(text="AT %", fg="black", font=("Helvetica", 10, "bold"))
        self.ext_humid_value.config(text="Ext %", fg="black", font=("Helvetica", 10, "bold"))
        self.input_3_3V_dmm.delete(0, tk.END)
        self.input_5V_dmm.delete(0, tk.END)
        self.result_read_prod_name.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.read_prod_name.config(text="-", fg="black", font=("Helvetica", 10, "bold"))
        self.result_mac_address_s3_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_mac_address_h2_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_group2_factory_mode.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_group2_wifi_softap.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_group2_wifi_softap_rssi.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.range_group2_wifi_softap_rssi.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_group2_wifi_softap_ssid.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_group2_wifi_station.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_group2_wifi_station_rssi.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.range_group2_wifi_station_rssi.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_ir_rx_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_ir_def_label.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_ir_led1.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_ir_led2.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_ir_led3.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_ir_led4.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_ir_led5.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.cert_status_label.config(text=" ", fg="black", font=("Helvetica", 10, "bold"))
        self.result_short_header.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_factory_reset.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.result_h2_led_check.config(text="Failed", fg="red", font=("Helvetica", 10, "bold"))
        self.printer_qrpayload_data_label.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.printer_manualcode_data_label.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.printer_status_data_label.config(text="-", fg="black", font=("Helvetica", 10, "normal"))


    def reset_ui(self):
        global device_data
        global orderNum_label
        global macAddress_label
        global serialID_label
        global certID_label
        global secureCertPartition_label
        global commissionableDataPartition_label
        global qrCode_label
        global manualCode_label
        global discriminator_label
        global passcode_label
        global orderNum_data
        global macAddress_esp32s3_data
        global serialID_data
        global certID_data
        global secureCertPartition_data
        global commissionableDataPartition_data
        global qrCode_data
        global manualCode_data
        global discriminator_data
        global passcode_data

        logger.info("Resetting tasks")

        device_data = ""

        orderNum_label = ""
        macAddress_label = ""
        serialID_label = ""
        certID_label = ""
        secureCertPartition_label = ""
        commissionableDataPartition_label = ""
        qrCode_label = ""
        manualCode_label = ""
        discriminator_label = ""
        passcode_label = ""

        orderNum_data = ""
        macAddress_esp32s3_data = ""
        serialID_data = ""
        certID_data = ""
        secureCertPartition_data = ""
        commissionableDataPartition_data = ""
        qrCode_data = ""
        manualCode_data = ""
        discriminator_data = ""
        passcode_data = ""

        # self.serialCom.close_serial_port()

        self.read_mac_address_label.config(fg="black")
        self.read_mac_address_label.grid()
        self.status_flashing_fw.config(fg="black")
        self.status_flashing_fw.grid()
        self.status_flashing_cert.config(fg="black")
        self.status_flashing_cert.grid()
        self.status_factory_mode.config(fg="black")
        self.status_factory_mode.grid()
        self.status_read_device_mac.config(fg="black")
        self.status_read_device_mac.grid()
        self.status_read_prod_name.config(fg="black")
        self.status_read_prod_name.grid()
        self.status_write_device_sn.config(fg="black")
        self.status_write_device_sn.grid()
        self.status_write_device_mtqr.config(fg="black")
        self.status_write_device_mtqr.grid()
        self.result_ir_def.config(fg="black")
        self.result_ir_def.grid()
        self.status_save_device_data_label.config(fg="black")
        self.status_save_device_data_label.grid()
        self.status_5v_test.config(fg="black")
        self.status_5v_test.grid()
        self.status_3_3v_test.config(fg="black")
        self.status_3_3v_test.grid()
        self.status_atbeam_temp.config(fg="black")
        self.status_atbeam_temp.grid()
        self.status_atbeam_humidity.config(fg="black")
        self.status_atbeam_humidity.grid()
        self.status_button_label.config(fg="black")
        self.status_button_label.grid()
        self.status_rgb_red_label.config(fg="black")
        self.status_rgb_red_label.grid()
        self.status_rgb_green_label.config(fg="black")
        self.status_rgb_green_label.grid()
        self.status_rgb_blue_label.config(fg="black")
        self.status_rgb_blue_label.grid()
        self.ir_led1_label.config(fg="black")
        self.ir_led1_label.grid()
        self.ir_led2_label.config(fg="black")
        self.ir_led2_label.grid()
        self.ir_led3_label.config(fg="black")
        self.ir_led3_label.grid()
        self.ir_led4_label.config(fg="black")
        self.ir_led4_label.grid()
        self.ir_led5_label.config(fg="black")
        self.ir_led5_label.grid()
        self.status_group2_factory_mode.config(fg="black")
        self.status_group2_factory_mode.grid()
        self.status_group2_wifi_softap_label.config(fg="black")
        self.status_group2_wifi_softap_label.grid()
        self.status_group2_wifi_station.config(fg="black")
        self.status_group2_wifi_station.grid()
        self.status_short_header.config(fg="black")
        self.status_short_header.grid()
        self.status_factory_reset.config(fg="black")
        self.status_factory_reset.grid()
        self.status_h2_led_check.config(fg="black")
        self.status_h2_led_check.grid()
        self.printer_label.config(fg="black")
        self.printer_label.grid()

        self.result_flashing_fw_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_flashing_fw_h2_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_flashing_cert_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_factory_mode_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_read_device_mac.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.read_device_mac.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_write_serialnumber.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.read_device_sn.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_write_mtqr.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.read_device_mtqr.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_save_device_data_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.read_save_device_data_label.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_3_3v_test.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.range_value_3_3V_dmm.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_5v_test.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.range_value_5V_dmm.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_temp_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.range_temp_value.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_humid_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.range_humid_value.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_rgb_red_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        # self.yes_button_red.config(state='normal')
        # self.no_button_red.config(state='normal')
        self.result_rgb_green_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        # self.yes_button_green.config(state='normal')
        # self.no_button_green.config(state='normal')
        self.result_rgb_blue_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        # self.yes_button_blue.config(state='normal')
        # self.no_button_blue.config(state='normal')
        self.result_button_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.dmm_3_3V_reader.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.dmm_5V_reader.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.atbeam_temp_value.config(text="AT °C", fg="black", font=("Helvetica", 10, "normal"))
        self.ext_temp_value.config(text="Ext °C", fg="black", font=("Helvetica", 10, "normal"))
        self.atbeam_humid_value.config(text="AT %", fg="black", font=("Helvetica", 10, "normal"))
        self.ext_humid_value.config(text="Ext %", fg="black", font=("Helvetica", 10, "normal"))
        self.input_3_3V_dmm.delete(0, tk.END)
        self.input_5V_dmm.delete(0, tk.END)
        self.result_read_prod_name.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.read_prod_name.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_mac_address_s3_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_mac_address_h2_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_group2_factory_mode.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_group2_wifi_softap.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_group2_wifi_softap_rssi.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.range_group2_wifi_softap_rssi.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_group2_wifi_softap_ssid.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_group2_wifi_station.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_group2_wifi_station_rssi.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.range_group2_wifi_station_rssi.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.result_ir_def_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_ir_rx_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_ir_led1.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_ir_led2.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_ir_led3.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_ir_led4.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_ir_led5.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.cert_status_label.config(text=" ", fg="black", font=("Helvetica", 10, "normal"))
        self.result_short_header.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_factory_reset.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_h2_led_check.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.printer_qrpayload_data_label.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.printer_manualcode_data_label.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.printer_status_data_label.config(text="-", fg="black", font=("Helvetica", 10, "normal"))

    # def press_button(self, angle, pressing_duration, pressing_time):
    #     # angle = float(self.angle_entry.get())
    #     # pressing_duration = float(self.duration_entry.get())
    #     # pressing_time = int(self.pressing_time_entry.get())

    #     angle = None
    #     pressing_duration = None
    #     pressing_time = None

    #     logger.info(f"Pressing button {pressing_time} times, angle: {angle}, duration: {pressing_duration}")

    #     for i in range(pressing_time):
    #         logger.info(f"Pressing button {i+1} time")
    #         self.servo_controller.set_angle(angle)
    #         time.sleep(pressing_duration)
    #         self.servo_controller.set_angle(0)
    #         time.sleep(0.5)

    def read_version_from_file(self, file_name):
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        try:
            with open(file_path, "r") as file:
                version = file.readline().strip()
                return version
        except FileNotFoundError:
            return "Version not found"

    def add_version_label(self, version):
        # Create a label for the version number
        version_label = tk.Label(self.scrollable_frame, text=f"Version: {version}")

        # Use a high row and column index to ensure it's at the bottom right
        version_label.grid(row=999, column=999, padx=10, pady=10, sticky=tk.SE)

        # Configure weights for the grid to ensure the label stays at the bottom right
        self.scrollable_frame.grid_rowconfigure(998, weight=1)
        self.scrollable_frame.grid_columnconfigure(998, weight=1)
        self.scrollable_frame.grid_rowconfigure(999, weight=1)
        self.scrollable_frame.grid_columnconfigure(999, weight=1)


    def on_exit(self):
        print('on_exit')
        self.root.destroy()
        # self.close_serial_port()
        print('on_exit-end')
        self.root.quit

    # def log_test(self):
    #     file_sn = self.read_device_sn.cget("text")

    #     logging.basicConfig(
    #         filename=file_sn,  # Name of the log file
    #         level=logging.DEBUG,  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    #         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #     )

    #def configure_logging(self):
        #filename = self.read_device_sn.cget("text")
        #log_filename = f'{filename}.log'
        #log_filename = f'{self.read_device_sn["text"]}.log' if self.read_device_sn["text"] != "-" else 'default.log'
        #logging.basicConfig(
        #    filename=log_filename,  # Name of the log file
        #    level=logging.DEBUG,    # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        #    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        #)
        #self.logger = logging.getLogger(__name__)
        #self.logger.debug("Logger initialized with filename: %s", log_filename)

if __name__ == "__main__":

    # Get the current date and time
    current_datetime = datetime.now()

    # Format the date and time
    # formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    formatted_date = current_datetime.strftime("%Y%m%d")
    formatted_time = current_datetime.strftime("%H%M%S")

    # Configure logging
    # log_file_name = logs_dir + "/" + logs_file_name + '_' + str(formatted_date) + logs_file_extension
    # print(str(log_file_name))
    # logging.basicConfig(
    #     filename=str(log_file_name),  # Name of the log file
    #     level=logging.DEBUG,  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # )

    #Check if logs folder exist on boot
    if (os.path.isdir(logs_dir) == False):
        os.chdir(script_dir)
        os.mkdir(logs_dir_name)

    # Delete "sensor.txt" file during boot up
    sensor_file = "sensor.txt"
    if os.path.exists(sensor_file):
        os.remove(sensor_file)

    root = tk.Tk()
    app = SerialCommunicationApp(root)

    root.protocol("WM_DELETE_WINDOW", app.on_exit)
    root.mainloop()

    # Copy the log file to the desired destination
    source_path = '/usr/src/app/app.log'
    destination_path = '/usr/src/app/my-s3-bucket/'

    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)

    # Copy the file
    shutil.copy2(source_path, destination_path)

    logger.info(f'Log file copied to {destination_path}')

