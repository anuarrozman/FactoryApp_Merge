import subprocess
import re

def scan_wifi_networks(interface='wlan0'):
    try:
        # Run iwlist scan command and capture output
        scan_output = subprocess.check_output(['sudo', 'iwlist', interface, 'scan'], stderr=subprocess.STDOUT)
        scan_output = scan_output.decode('utf-8')

        # Use regular expressions to extract SSID and signal level (RSSI)
        networks = []
        current_network = {}
        lines = scan_output.splitlines()
        for line in lines:
            if re.match('^\s*Cell', line):
                if current_network:
                    networks.append(current_network)
                    current_network = {}
            elif re.match('^\s*Quality', line):
                # Extract signal level (RSSI)
                match = re.search(r'=(\d+)/(\d+)', line)
                if match:
                    quality = int(match.group(1))
                    max_quality = int(match.group(2))
                    signal_percent = quality / max_quality * 100
                    current_network['Signal_Level'] = f'{signal_percent:.2f}%'
            elif re.match('^\s*ESSID', line):
                # Extract SSID
                match = re.search(r'ESSID:"(.*)"', line)
                if match:
                    current_network['SSID'] = match.group(1)
        
        # Append the last network found
        if current_network:
            networks.append(current_network)

        return networks

    except subprocess.CalledProcessError as e:
        print(f"Error scanning WiFi networks: {e}")
        return []

if __name__ == "__main__":
    wifi_networks = scan_wifi_networks()
    if wifi_networks:
        print("Available WiFi networks:")
        for network in wifi_networks:
            ssid = network.get('SSID', 'Unknown')
            signal_level = network.get('Signal_Level', 'Unknown')
            print(f"SSID: {ssid}, Signal Level: {signal_level}")
    else:
        print("No WiFi networks found.")
