def read_multimeter_voltage():
    return 5.1    # Replace with actual voltage reading

# Function to determine if the voltage reading is within the expected range for 3.3V
def is_3_3_voltage(voltage):
    return 3.0 <= voltage <= 3.6

# Function to determine if the voltage reading is within the expected range for 5V
def is_5_voltage(voltage):
    return 4.8 <= voltage <= 5.2

def main():
    voltage = read_multimeter_voltage()
    
    if is_3_3_voltage(voltage):
        print("Voltage reading from 3.3V multimeter:", voltage)
    elif is_5_voltage(voltage):
        print("Voltage reading from 5V multimeter:", voltage)
    else:
        print("Invalid voltage reading:", voltage)

if __name__ == "__main__":
    main()
