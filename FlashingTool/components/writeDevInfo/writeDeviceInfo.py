
class WriteDeviceInfo:
    
    def __init__(self, send_command, log_message):
        self.send_command = send_command
        self.log_message = log_message

    def send_entry_command(self, send_entry, serial_number):
        command = send_entry.get() + "\r\n"
        self.send_command(command)
        self.log_message(f"Serial Number: {serial_number} ")
        send_entry.delete(0, "end")
