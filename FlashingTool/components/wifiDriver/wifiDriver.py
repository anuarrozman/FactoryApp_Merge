# import subprocess
# import re

# def scan_wifi_networks(interface='wlan0', fallback_interface='wlp44s0'):
#     try:
#         # Run iwlist scan command and capture output
#         scan_output = subprocess.check_output(['sudo', 'iwlist', interface, 'scan'], stderr=subprocess.STDOUT)
#         scan_output = scan_output.decode('utf-8')
#     except subprocess.CalledProcessError as e:
#         print(f"Error scanning WiFi networks on {interface}: {e}")
#         if fallback_interface and interface != fallback_interface:
#             print(f"Attempting to scan using fallback interface: {fallback_interface}")
#             return scan_wifi_networks(fallback_interface, None)
#         else:
#             return []

#     # Debug: Print the raw scan output
#     print("Raw scan output:")
#     print(scan_output)

#     # Use regular expressions to extract SSID and signal level (RSSI)
#     networks = []
#     current_network = {}
#     lines = scan_output.splitlines()
#     for line in lines:
#         if re.match(r'^\s*Cell', line):
#             if current_network:
#                 networks.append(current_network)
#                 current_network = {}
#         elif re.search(r'\s*Signal level=(-?\d+) dBm', line):
#             # Extract signal level (RSSI)
#             match = re.search(r'Signal level=(-?\d+) dBm', line)
#             if match:
#                 current_network['Signal_Level'] = match.group(1) + ' dBm'
#         elif re.search(r'\s*ESSID', line):
#             # Extract SSID
#             match = re.search(r'ESSID:"(.*)"', line)
#             if match:
#                 current_network['SSID'] = match.group(1)

#     # Append the last network found
#     if current_network:
#         networks.append(current_network)

#     return networks


import subprocess
import re

def scan_wifi_networks(interface='wlan0', fallback_interface='wlp44s0'):
    """Scan for available WiFi networks using the specified interface."""
    try:
        # Run iwlist scan command and capture output
        scan_output = subprocess.check_output(['sudo', 'iwlist', interface, 'scan'], stderr=subprocess.STDOUT)
        scan_output = scan_output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error scanning WiFi networks on {interface}: {e}")
        if fallback_interface and interface != fallback_interface:
            print(f"Attempting to scan using fallback interface: {fallback_interface}")
            return scan_wifi_networks(fallback_interface, None)
        else:
            return []

    # Debug: Print the raw scan output
    print("Raw scan output:")
    print(scan_output)

    # Use regular expressions to extract SSID and signal level (RSSI)
    networks = []
    current_network = {}
    lines = scan_output.splitlines()
    for line in lines:
        if re.match(r'^\s*Cell', line):
            if current_network:
                networks.append(current_network)
                current_network = {}
        elif re.search(r'\s*Signal level=(-?\d+) dBm', line):
            # Extract signal level (RSSI)
            match = re.search(r'Signal level=(-?\d+) dBm', line)
            if match:
                current_network['Signal_Level'] = match.group(1) + ' dBm'
        elif re.search(r'\s*ESSID', line):
            # Extract SSID
            match = re.search(r'ESSID:"(.*)"', line)
            if match:
                ssid = match.group(1)
                if ssid.startswith("AT"):  # Only add networks starting with 'AT'
                    current_network['SSID'] = ssid

    # Append the last network found
    if current_network:
        networks.append(current_network)

    return networks

def connect_to_network(interface, ssid, password):
    """Connect to a specified wireless network."""
    print(f"Connecting to {ssid}...")
    connect_command = ["sudo", "nmcli", "dev", "wifi", "connect", ssid, "password", password]
    result = subprocess.run(connect_command, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Failed to connect to {ssid}. Error: {result.stderr.strip()}")
        return False
    
    print(f"Successfully connected to {ssid}.")
    return True

def get_ip_address(interface):
    """Retrieve the IP address of the specified interface."""
    result = subprocess.run(["ip", "addr", "show", interface], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Failed to get IP address.")
        return None
    
    # Find the IP address in the output
    ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', result.stdout)
    if ip_match:
        return ip_match.group(1)
    
    print("No IP address found.")
    return None

def main():
    interface = 'wlan0'  # Change this if your wireless interface is different
    networks = scan_wifi_networks(interface)

    if not networks:
        print("No networks found.")
        return

    print("Available networks starting with 'AT':")
    for i, network in enumerate(networks):
        # Ensure 'SSID' exists before printing
        if 'SSID' in network:
            print(f"{i + 1}: {network['SSID']} (Signal: {network['Signal_Level']})")

    if not networks:
        print("No 'AT' networks found.")
        return

    choice = int(input("Select the network to connect to (number): ")) - 1
    if choice < 0 or choice >= len(networks):
        print("Invalid selection.")
        return

    ssid = networks[choice].get('SSID')
    if not ssid:
        print("Invalid network selected.")
        return

    password = input(f"Enter password for {ssid}: ")

    if connect_to_network(interface, ssid, password):
        ip_address = get_ip_address(interface)
        if ip_address:
            print(f"Your IP address is: {ip_address}")

if __name__ == "__main__":
    main()
